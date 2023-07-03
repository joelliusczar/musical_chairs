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
	StationActionRule
)
from musical_chairs_libs.services import (
	StationService,
	QueueService,
	ProcessService
)
from api_dependencies import (
	station_service,
	queue_service,
	process_service,
	get_station_user,
	get_owner,
	get_station_by_name_and_owner,
	get_current_user_simple,
	get_user_with_rate_limited_scope,
	get_user_with_simple_scopes,
	get_optional_user_from_token,
	get_subject_user
)
from station_validation import (
	validate_station_rule,
	validate_station_rule_for_remove
)


router = APIRouter(prefix="/stations")

@router.get("/list")
def station_list(
	user: AccountInfo = Depends(get_optional_user_from_token),
	owner: Optional[AccountInfo] = Depends(get_owner),
	stationService: StationService = Depends(station_service),
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_stations(None,
		ownerId=owner.id if owner else None,
		user=user
	))
	return { "items": stations }

@router.get("/{ownerKey}/{stationKey}/history/")
def history(
	page: int = 0,
	limit: int = 50,
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	user: AccountInfo = Depends(get_station_user),
	queueService: QueueService = Depends(queue_service),
	stationService: StationService = Depends(station_service)
) -> StationTableData[SongListDisplayItem]:
	if not station:
		return StationTableData(totalRows=0, items=[], stationRules=[])
	history = list(queueService.get_history_for_station(
			stationId=station.id,
			page = page,
			limit = limit,
			user=user
		))
	rules =  ActionRule.sorted(
		station.rules
	)
	totalRows = queueService.history_count(stationId=station.id)
	return StationTableData(
		totalRows=totalRows,
		items=history,
		stationRules=rules
	)

@router.get("/{ownerKey}/{stationKey}/queue/")
def queue(
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	user: AccountInfo = Depends(get_station_user),
	queueService: QueueService = Depends(queue_service),
) -> CurrentPlayingInfo:
	if not station:
		return CurrentPlayingInfo(
			nowPlaying=None,
			items=[],
			totalRows=0,
			stationRules=[]
		)
	queue = queueService.get_now_playing_and_queue(
		stationId=station.id,
		user=user
	)
	queue.stationRules = ActionRule.sorted(
		station.rules
	)
	return queue

@router.get("/{ownerKey}/{stationKey}/catalogue/")
def song_catalogue(
	page: int = 0,
	limit: int = 50,
	user: AccountInfo = Depends(get_station_user),
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	stationService: StationService = Depends(station_service)
) -> StationTableData[SongListDisplayItem]:
	if not station:
		return StationTableData(totalRows=0, items=[], stationRules=[])
	songs = list(
		stationService.get_station_song_catalogue(
			stationId = station.id,
			page = page,
			limit = limit,
			user=user
		)
	)
	totalRows = stationService.song_catalogue_count(
		stationId = station.id
	)
	rules = ActionRule.sorted(
		station.rules
	)
	return StationTableData(totalRows=totalRows, items=songs, stationRules=rules)

@router.post("/{ownerKey}/{stationKey}/request/{songId}")
def request_song(
	songId: int,
	station: StationInfo = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service),
	user: AccountInfo = Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_REQUEST.value]
	)
):
	try:
		queueService.add_song_to_queue(songId, station, user)
	except (LookupError, RuntimeError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = str(ex)
		)

@router.delete("/{ownerKey}/{stationName}/request/",
	dependencies=[
		Security(get_station_user, scopes=[UserRoleDef.STATION_SKIP.value])
	]
)
def remove_song_from_queue(
	stationName: str,
	id: int,
	queuedTimestamp: float,
	station: StationInfo = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service)
) -> CurrentPlayingInfo:
	queue = queueService.remove_song_from_queue(
		id,
		queuedTimestamp,
		stationId=station.id
	)
	if queue:
		return queue
	raise HTTPException(
			status_code = status.HTTP_404_NOT_FOUND,
			detail = f"Song: {id} not found at {queuedTimestamp} on {stationName}"
		)


@router.get("/check/")
def is_phrase_used(
	id: Optional[int]=None,
	name: str = "",
	user: AccountInfo = Depends(get_current_user_simple),
	stationService: StationService = Depends(station_service)
) -> dict[str, bool]:
	return {
		"name": stationService.is_stationName_used(id, name, user.id)
	}


@router.get("/{ownerKey}/{stationKey}")
def get_station_for_edit(
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner)
) -> StationInfo:
	return stationInfo

@router.post("")
def create_station(
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_user_with_rate_limited_scope,
		scopes=[UserRoleDef.STATION_CREATE.value]
	)
) -> StationInfo:
	result = stationService.save_station(station, user=user)
	return result or StationInfo(id=-1,name="", displayName="")

@router.put("/{stationKey}")
def update_station(
	stationKey: int,
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_EDIT.value]
	)
) -> StationInfo:
	result = stationService.save_station(station,user, stationKey)
	return result or StationInfo(id=-1,name="",displayName="")

@router.put("/enable/")
def enable_stations(
	stationId: list[int] = Query(default=[]),
	includeAll: bool = Query(default=False),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	processService: ProcessService = Depends(process_service)
) -> list[StationInfo]:
	return list(processService.enable_stations(stationId, user, includeAll))

@router.put("/disable/", status_code=status.HTTP_204_NO_CONTENT)
def disable_stations(
	stationIds: list[int] = Query(default=[]),
	includeAll: bool = Query(default=False),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	processService: ProcessService = Depends(process_service)
) -> None:
	processService.disable_stations(stationIds, user.id, includeAll)

@router.post("/{ownerKey}/{stationKey}/play_next",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_user_with_simple_scopes,
			scopes=[UserRoleDef.ADMIN.value]
		)]
)
def play_next(
	station: StationInfo = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service)
):
	queueService.pop_next_queued(station.id)

@router.get("/{ownerKey}/{stationKey}/user_list",dependencies=[
	Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_USER_LIST.value]
	)
])
def get_station_user_list(
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
	stationService: StationService = Depends(station_service),
) -> TableData[AccountInfo]:
	stationUsers = list(stationService.get_station_users(stationInfo))
	return TableData(stationUsers, len(stationUsers))




@router.post("/{ownerKey}/{stationKey}/user_role",
	dependencies=[
		Security(
			get_station_user,
			scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
		)
	]
)
def add_user_rule(
	user: AccountInfo = Depends(get_subject_user),
	rule: StationActionRule = Depends(validate_station_rule),
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
	stationService: StationService = Depends(station_service),
) -> StationActionRule:
	return stationService.add_user_rule_to_station(user.id, stationInfo.id, rule)


@router.delete("/{ownerKey}/{stationKey}/user_role",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(
			get_station_user,
			scopes=[UserRoleDef.STATION_USER_ASSIGN.value]
		)
	]
)
def remove_user_rule(
	user: AccountInfo = Depends(get_subject_user),
	ruleName: Optional[str] = Depends(validate_station_rule_for_remove),
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
	stationService: StationService = Depends(station_service),
):
	stationService.remove_user_rule_from_station(
		user.id,
		stationInfo.id,
		ruleName
	)