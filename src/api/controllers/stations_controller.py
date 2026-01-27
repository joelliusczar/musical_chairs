#pyright: reportMissingTypeStubs=false
from typing import Dict, List, Optional
from fastapi import (
	APIRouter,
	Depends,
	Security,
	HTTPException,
	status,
	Body,
	Query
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	CurrentPlayingInfo,
	HistoryItem,
	StationInfo,
	StationTableData,
	UserRoleDef,
	ActionRule,
	TableData,
	CatalogueItem,
	SimpleQueryParameters,
	UserRoleDomain,
	ValidatedStationCreationInfo,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationActions,
	StationRequestTypes
)
from musical_chairs_libs.services import (
	StationService,
	QueueService,
	StationsUsersService,
	StationProcessService,
)
from musical_chairs_libs.protocols import RadioPusher
from api_dependencies import (
	check_top_level_rate_limit,
	station_service,
	queue_service,
	get_owner_from_query,
	get_query_params,
	get_from_query_subject_user,
	get_page_num,
	build_error_obj,
	stations_users_service,
	station_process_service,
)
from api_logging import log_event
from station_validation import (
	get_station,
	get_rate_secured_station,
	get_secured_station,
	station_radio_pusher,
	validate_station_rule,
	validated_station_request_type,
	validate_station_rule_for_remove,
)
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/stations")

@router.get("/list")
def station_list(
	owner: Optional[AccountInfo] = Depends(get_owner_from_query),
	stationService: StationService = Depends(station_service),
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_stations(None,
		ownerId=owner.id if owner else None
	))
	return { "items": stations }


@router.get("/{ownerkey}/{stationkey}/history/")
def history(
	limit: int = 50,
	page: int = Depends(get_page_num),
	station: Optional[StationInfo] = Depends(get_station),
	queueService: QueueService = Depends(queue_service),
) -> StationTableData[HistoryItem]:
	if not station:
		return StationTableData(totalrows=0, items=[], stationrules=[])
	history, totalRows = queueService.get_history_for_station(
			station=station,
			page = page,
			limit = limit,
		)
	rules =  ActionRule.sorted(
		station.rules
	)
	return StationTableData(
		totalrows=totalRows,
		items=history,
		stationrules=rules
	)

@router.get("/{ownerkey}/{stationkey}/queue/")
def queue(
	limit: int = 50,
	page: int = Depends(get_page_num),
	station: Optional[StationInfo] = Depends(get_station),
	queueService: QueueService = Depends(queue_service),
) -> CurrentPlayingInfo:
	if not station:
		return CurrentPlayingInfo(
			nowplaying=None,
			items=[],
			totalrows=0,
			stationrules=[]
		)
	queue = queueService.get_now_playing_and_queue(
		station=station,
		page=page,
		limit=limit,
	)
	queue.stationrules = ActionRule.sorted(
		station.rules
	)
	return queue


@router.get("/{ownerkey}/{stationkey}/catalogue/")
def catalogue(
	name: str = "",
	parentname: str = "",
	creator: str = "",
	queryParams: SimpleQueryParameters = Depends(get_query_params,),
	station: Optional[StationInfo] = Depends(get_station),
	queueService: RadioPusher = Depends(station_radio_pusher),
) -> StationTableData[CatalogueItem]:
	if not station:
		return StationTableData(totalrows=0, items=[], stationrules=[])
	if queryParams.limit is None:
		queryParams.limit = 50
	items, totalRows = queueService.get_catalogue(
			stationId = station.id,
			queryParams=queryParams,
			name=name,
			parentname=parentname,
			creator=creator
		)
	rules = ActionRule.sorted(
		station.rules
	)
	return StationTableData(totalrows=totalRows, items=items, stationrules=rules)


@router.post(
	"/{ownerkey}/{stationkey}/request/{requesttypeid}/{itemid}",
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_REQUEST.value
			)
		)
	]
)
def request_item(
	itemid: int,
	station: StationInfo = Security(
		get_rate_secured_station,
		scopes=[UserRoleDef.STATION_REQUEST.value]
	),
	requestType: StationRequestTypes = Depends(validated_station_request_type),
	queueService: RadioPusher = Depends(station_radio_pusher),
):
	try:
		queueService.add_to_queue(
			itemid,
			station,
			requestType
		)
	except (LookupError, RuntimeError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = str(ex)
		)


@router.delete(
	"/{ownerkey}/{stationkey}/request",
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_SKIP.value
			)
		)
	]
)
def remove_song_from_queue(
	id: int,
	queuedtimestamp: float,
	station: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_SKIP.value]
	),
	queueService: RadioPusher = Depends(station_radio_pusher)
) -> CurrentPlayingInfo:
	queue = queueService.remove_song_from_queue(
		id,
		queuedtimestamp,
		station=station
	)
	if queue:
		return queue
	raise HTTPException(
			status_code = status.HTTP_404_NOT_FOUND,
			detail = f"Song: {id} not found at {queuedtimestamp} on {station.name}"
		)



@router.get("/check/")
def is_phrase_used(
	id: Optional[int]=None,
	name: str = "",
	stationService: StationService = Depends(station_service)
) -> dict[str, bool]:
	return {
		"name": stationService.is_stationName_used(id, name)
	}


@router.get("/{ownerkey}/{stationkey}")
def get_station_for_edit(
	stationInfo: StationInfo = Depends(get_station)
) -> StationInfo:
	return stationInfo


@router.post("", dependencies=[
	Security(
		check_top_level_rate_limit(UserRoleDomain.Station.value),
		scopes=[UserRoleDef.STATION_CREATE.value]
	),
	Depends(
			log_event(
				UserRoleDomain.Site.value,
				StationActions.STATION_CREATE.value
			)
		)
])
def create_station(
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(
		station_service,
		
	)
) -> StationInfo:
	result = stationService.save_station(station)
	return result or StationInfo(id=-1,name="", displayname="")


@router.put("/{id}",dependencies=[
	Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_EDIT.value
			)
		)
])
def update_station(
	savedStation: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_EDIT.value]
	),
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
) -> StationInfo:
	result = stationService.save_station(station, savedStation.id)
	return result or StationInfo(id=-1,name="",displayname="")


@router.put("/enable/", dependencies=[
	Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_ENABLE.value
			)
		)
])
def enable_stations(
	station: StationInfo = Security(
		get_rate_secured_station,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	stationProcessService: StationProcessService = Depends(
		station_process_service
	)
) -> list[StationInfo]:
	return list(
		stationProcessService.enable_stations(station)
	)


@router.put(
	"/disable/",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_DISABLE.value
			)
		)
	]
)
def disable_stations(
	station: StationInfo = Security(
		get_rate_secured_station,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	includeAll: bool = Query(default=False),
	stationProcessService: StationProcessService = Depends(
		station_process_service
	)
) -> None:
	stationProcessService.disable_stations(
		station
	)
	stationProcessService.unset_station_procs(stationIds=station.id)


@router.post(
	"/{ownerkey}/{stationkey}/play_next",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_PLAYNEXT.value
			)
		)
	]
)
def play_next(
	station: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.ADMIN.value]
	),
	queueService: QueueService = Depends(queue_service)
):
	queueService.pop_next_queued(station.id)


@router.get("/{ownerkey}/{stationkey}/user_list")
def get_station_user_list(
	stationInfo: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_USER_LIST.value]
	),
	stationsUsersService: StationsUsersService = Depends(stations_users_service),
) -> TableData[AccountInfo]:
	stationUsers = list(stationsUsersService.get_station_users(stationInfo))
	return TableData(items=stationUsers, totalrows=len(stationUsers))


@router.post(
	"/{ownerkey}/{stationkey}/user_role",
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_USER_ASSIGN.value
			)
		)
	]
)
def add_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	stationInfo: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
	),
	rule: ActionRule = Depends(validate_station_rule),
	stationsUsersService: StationsUsersService = Depends(stations_users_service),
) -> ActionRule:
	return stationsUsersService.add_user_rule_to_station(
		user.id,
		stationInfo.id,
		rule
	)


@router.delete(
	"/{ownerkey}/{stationkey}/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_USER_REMOVE.value
			)
		)
	]
)
def remove_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	rulename: Optional[str] = Depends(validate_station_rule_for_remove),
	stationInfo: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
	),
	stationsUsersService: StationsUsersService = Depends(stations_users_service),
):
	stationsUsersService.remove_user_rule_from_station(
		user.id,
		stationInfo.id,
		rulename
	)


@router.delete(
	"/{stationid}",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_DELETE.value
			)
		)
	]
)
def delete(
	station: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_DELETE.value]
	),
	clearStation: bool=False,
	stationService: StationService = Depends(station_service),
):
	try:
		if stationService.delete_station(station.id, clearStation) == 0:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj(f"Station not found")
				]
			)
	except IntegrityError:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,	
			detail=[build_error_obj(f"Station cannot be deleted")
			]
		)


@router.post(
	"/copy/{stationid}",
	dependencies=[
		Depends(
			log_event(
				UserRoleDomain.Station.value,
				StationActions.STATION_COPY.value
			)
		)
	]
)
def copy_station(
	savedstation: StationInfo = Security(
		get_secured_station,
		scopes=[UserRoleDef.STATION_CREATE.value]
	),
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
) -> StationInfo:
	result = stationService.copy_station(savedstation.id, station)
	return result or StationInfo(id=-1,name="", displayname="")