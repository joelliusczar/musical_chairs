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
	ValidatedStationCreationInfo,
	SongListDisplayItem,
	StationInfo,
	StationTableData,
	UserRoleDef,
	ActionRule,
	TableData,
	StationActionRule,
	CatalogueItem,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
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
	current_user_provider,
	get_secured_station_by_name_and_owner,
	station_service,
	queue_service,
	get_owner_from_query,
	get_station_by_name_and_owner,
	get_from_query_subject_user,
	get_stations_by_ids,
	get_page_num,
	build_error_obj,
	stations_users_service,
	station_process_service,
	validated_station_request_type,
	station_radio_pusher,
)
from station_validation import (
	validate_station_rule,
	validate_station_rule_for_remove
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
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service),
) -> StationTableData[SongListDisplayItem]:
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
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
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
	limit: int = 50,
	name: str = "",
	parentName: str = "",
	creator: str = "",
	page: int = Depends(get_page_num),
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	queueService: RadioPusher = Depends(station_radio_pusher),
) -> StationTableData[CatalogueItem]:
	if not station:
		return StationTableData(totalrows=0, items=[], stationrules=[])
	items, totalRows = queueService.get_catalogue(
			stationId = station.id,
			page = page,
			limit = limit,
			name=name,
			parentName=parentName,
			creator=creator
		)
	rules = ActionRule.sorted(
		station.rules
	)
	return StationTableData(totalrows=totalRows, items=items, stationrules=rules)


@router.post(
	"/{ownerkey}/{stationkey}/request/{requesttypeid}/{itemid}")
def request_item(
	itemid: int,
	station: StationInfo = Security(
		get_secured_station_by_name_and_owner,
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


@router.delete("/{ownerkey}/{stationkey}/request")
def remove_song_from_queue(
	id: int,
	queuedtimestamp: float,
	station: StationInfo = Depends(get_station_by_name_and_owner),
	queueService: RadioPusher = Security(
		station_radio_pusher,
		scopes=[UserRoleDef.STATION_SKIP.value]
	)
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
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner)
) -> StationInfo:
	return stationInfo


@router.post("")
def create_station(
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Security(
		station_service,
		scopes=[UserRoleDef.STATION_CREATE.value]
	)
) -> StationInfo:
	result = stationService.save_station(station)
	return result or StationInfo(id=-1,name="", displayname="")


@router.put("/{stationid}")
def update_station(
	stationid: int, #this needs to match get_station_user_by_id
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Security(
		station_service,
		scopes=[UserRoleDef.STATION_EDIT.value]
	),
) -> StationInfo:
	result = stationService.save_station(station, stationid)
	return result or StationInfo(id=-1,name="",displayname="")


@router.put("/enable/")
def enable_stations(
	stations: list[StationInfo] = Depends(get_stations_by_ids),
	includeAll: bool = Query(default=False),
	stationProcessService: StationProcessService = Security(
		station_process_service,
		scopes=[UserRoleDef.STATION_FLIP.value]
	)
) -> list[StationInfo]:
	if not stations and not includeAll:
		raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj("No stations selected")
				]
			)
	return list(
		stationProcessService.enable_stations(stations[0])
	)


@router.put("/disable/", status_code=status.HTTP_204_NO_CONTENT)
def disable_stations(
	stationids: list[int]=Query(default=[]),
	includeAll: bool = Query(default=False),
	stationProcessService: StationProcessService = Security(
		station_process_service,
		scopes=[UserRoleDef.STATION_FLIP.value]
	)
) -> None:
	if not stationids and not includeAll:
		raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[build_error_obj("No stations selected")
				]
			)
	stationProcessService.disable_stations(
		next(iter(stationids),None)
	)

@router.post(
	"/{ownerkey}/{stationkey}/play_next",
	status_code=status.HTTP_204_NO_CONTENT,
)
def play_next(
	station: StationInfo = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Security(
		queue_service,
		scopes=[UserRoleDef.ADMIN.value]
	)
):
	queueService.pop_next_queued(station.id)


@router.get("/{ownerkey}/{stationkey}/user_list", dependencies=[
	Security(
		current_user_provider,
		scopes=[UserRoleDef.STATION_USER_LIST.value]
	)
])
def get_station_user_list(
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
	stationsUsersService: StationsUsersService = Depends(stations_users_service),
) -> TableData[AccountInfo]:
	stationUsers = list(stationsUsersService.get_station_users(stationInfo))
	return TableData(items=stationUsers, totalrows=len(stationUsers))


@router.post("/{ownerkey}/{stationkey}/user_role")
def add_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	stationInfo: StationInfo = Security(
		get_secured_station_by_name_and_owner,
		scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
	),
	rule: StationActionRule = Depends(validate_station_rule),
	stationsUsersService: StationsUsersService = Depends(stations_users_service),
) -> StationActionRule:
	return stationsUsersService.add_user_rule_to_station(
		user.id,
		stationInfo.id,
		rule
	)


@router.delete("/{ownerkey}/{stationkey}/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			current_user_provider,
			scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	user: AccountInfo = Depends(get_from_query_subject_user),
	rulename: Optional[str] = Depends(validate_station_rule_for_remove),
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
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
)
def delete(
	stationid: int,
	clearStation: bool=False,
	stationService: StationService = Security(
		station_service,
		scopes=[UserRoleDef.STATION_EDIT.value]
	),
):
	try:
		if stationService.delete_station(stationid, clearStation) == 0:
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
	
@router.post("/copy/{stationid}")
def copy_station(
	stationid: int,
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Security(
		station_service,
		scopes=[UserRoleDef.STATION_CREATE.value]
	),
) -> StationInfo:
	result = stationService.copy_station(stationid, station)
	return result or StationInfo(id=-1,name="", displayname="")