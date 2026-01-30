from datetime import datetime
from typing import Callable, Iterator, Optional
from fastapi import (
	Depends,
	HTTPException,
	Path,
	Request,
	status,
)
from fastapi.security import SecurityScopes
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	ActionRule,
	build_error_obj,
	get_station_owner_rules,
	int_or_str,
	UserRoleDef,
	UserRoleSphere,
	StationInfo,
	StationRequestTypes,
	StationTypes,
	TooManyRequestsError,
	WrongPermissionsError
)
from musical_chairs_libs.protocols import RadioPusher
from musical_chairs_libs.services import (
	AccountManagementService,
	CurrentUserProvider,
	CollectionQueueService,
	QueueService,
	StationService,
)
from musical_chairs_libs.services.events import WhenNextCalculator
from sqlalchemy.engine import Connection
from api_dependencies import (
	account_management_service,
	current_user_provider,
	datetime_provider,
	get_configured_db_connection,
	get_from_query_subject_user,
	open_provided_user,
	queue_service,
	station_service,
	when_next_calculator
)



def get_stations(
	request: Request,
	stationService: StationService = Depends(station_service),
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> Iterator[StationInfo]:
	result = None
	pathId = request.path_params.get("id", None)
	if pathId is not None:
		return stationService.get_stations(int(pathId))
	
	pathName = request.path_params.get("stationkey", None)
	if pathName is not None:
		ownerKey = request.path_params.get("ownerkey", None)
		if ownerKey is not None:
			owner = open_provided_user(ownerKey, accountManagementService)
			if owner:
				return stationService.get_stations(
					int_or_str(pathName),
					ownerId=owner.id
				)
			else:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=[
						build_error_obj(
							f"Owner not found for {ownerKey}",
							"ownerKey"
						)],
				)

	queryIds = request.query_params.getlist("stationids")
	if queryIds:
		result = stationService.get_stations((int(s) for s in queryIds))
	if result:
		return result
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[
				build_error_obj(
					f"Stations wer not found",
					"Station"
				)],
		)


def get_station(
	stations: Iterator[StationInfo] = Depends(get_stations)
) -> StationInfo:
	station = next(stations, None)
	if station:
		return station
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[
			build_error_obj(
				f"Station was not found",
				"Station"
			)],
	)


def conforming_scopes(securityScopes: SecurityScopes) -> set[str]:
	return {s for s in securityScopes.scopes \
		if UserRoleSphere.Station.conforms(s)
	}


def __get_station_rules__(
	conformingSopes: set[str],
	station: StationInfo,
	currentUserProvider: CurrentUserProvider,
) -> list[ActionRule]:
	minScope = (not conformingSopes or\
		UserRoleDef.STATION_VIEW.value in conformingSopes
	)
	user = currentUserProvider.current_user()
	if not station.viewsecuritylevel and minScope:
		return station.rules

	if user.isadmin:
		return station.rules
	scopes = conformingSopes
	rules = ActionRule.aggregate(
		station.rules,
		filter=lambda r: r.name in scopes
	)
	if not rules:
		raise WrongPermissionsError()
	return rules


def get_station_rules(
	conformingSopes: set[str] = Depends(conforming_scopes),
	station: StationInfo = Depends(get_station),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> list[ActionRule]:
	return __get_station_rules__(conformingSopes, station, currentUserProvider)
	

def get_secured_station(
	conformingSopes: set[str] = Depends(conforming_scopes),
	station: StationInfo = Depends(get_station),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> StationInfo:
	__get_station_rules__(conformingSopes, station, currentUserProvider)
	return station


def get_rate_secured_station(
	conformingSopes: set[str] = Depends(conforming_scopes),
	rules: list[ActionRule] = Depends(get_station_rules),
	station: StationInfo = Depends(get_station),
	whenNextCalculator: WhenNextCalculator = Depends(
		when_next_calculator
	),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	getDatetime: Callable[[], datetime] = Depends(datetime_provider)
) -> StationInfo:
	user = currentUserProvider.current_user()
	timeoutLookup = whenNextCalculator\
		.calc_lookup_for_when_user_can_next_do_action(
			user.id,
			rules,
			UserRoleSphere.Station.value,
			str(station.id)
		)
	for scope in conformingSopes:
		if scope in timeoutLookup:
			whenNext = timeoutLookup[scope]
			if whenNext is None:
				raise WrongPermissionsError()
			if whenNext > 0:
				currentTimestamp = getDatetime().timestamp()
				timeleft = whenNext - currentTimestamp
				raise TooManyRequestsError(int(timeleft))
	return station


def validate_station_rule(
	rule: ActionRule,
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
	stationInfo: StationInfo = Depends(get_station),
) -> ActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set(UserRoleSphere.Station.value)
	if rule.name not in valid_name_set:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{rule.name} is not a valid rule for stations"
			)],
		)
	if stationInfo.owner and stationInfo.owner.id == user.id:
		if any(get_station_owner_rules((rule.name, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{rule.name} cannot be added to owner"
				)],
			)
	return rule


def validate_station_rule_for_remove(
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
	ruleName: Optional[str]=None,
	stationInfo: StationInfo = Depends(get_station),
) -> Optional[str]:
	if not user:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					"User is required"
				)],
			)
	if not ruleName:
		if stationInfo.owner and stationInfo.owner.id == user.id:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"Cannot remove owner from station"
				)],
			)
		return ruleName
	if ruleName == UserRoleDef.STATION_VIEW.value:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{ruleName} cannot be removed"
			)],
		)
	if stationInfo.owner and stationInfo.owner.id == user.id:
		if any(get_station_owner_rules((ruleName, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{ruleName} cannot be removed from owner"
				)],
			)
	return ruleName


def station_radio_pusher(
	station: StationInfo = Depends(get_station),
	conn: Connection = Depends(get_configured_db_connection),
	queueService: QueueService =  Depends(queue_service),
	currentUserProvider: CurrentUserProvider = Depends(current_user_provider),
) -> RadioPusher:
	if station.typeid == StationTypes.SONGS_ONLY.value:
		return queueService
	if station.typeid == StationTypes.ALBUMS_ONLY.value\
		or station.typeid == StationTypes.PLAYLISTS_ONLY.value\
		or station.typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value\
			:
		return CollectionQueueService(
			conn,
			queueService,
			currentUserProvider
		)
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"Station type: {station.typeid} not found")
		]
	)


def validated_station_request_type(
	requesttypeid: int = Path(),
	radioPusher: RadioPusher = Depends(station_radio_pusher)
) -> StationRequestTypes:
	requestType = StationRequestTypes(requesttypeid)
	if requestType not in radioPusher.accepted_request_types():
		raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{requestType.name} cannot be requested of that station"
					)
				]
			)
	return requestType