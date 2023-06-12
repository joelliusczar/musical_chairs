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
	ActionRule
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
	get_optional_user_from_token
)


router = APIRouter(prefix="/stations")

@router.get("/listAll")
def list_all(
	user: AccountInfo = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
):
	stations = list(stationService.get_stations())
	return { "items": stations }

@router.get("/{ownerKey}/list")
def station_list(
	user: AccountInfo = Depends(get_optional_user_from_token),
	owner: Optional[AccountInfo] = Depends(get_owner),
	stationService: StationService = Depends(station_service),
) -> Dict[str, List[StationInfo]]:
	if not owner:
		raise HTTPException(
			status_code = status.HTTP_404_NOT_FOUND,
			detail = f"Station list not found"
		)
	stations = list(stationService.get_stations(None,
		ownerId=owner.id)
	)
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
	rules =  ActionRule.aggregate(
		user.roles if user else (),
		stationService.get_station_rules(user.id, station.id) if user else ()
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
	stationService: StationService = Depends(station_service)
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
	queue.stationRules = ActionRule.aggregate(
		user.roles if user else (),
		stationService.get_station_rules(user.id, station.id) if user else ()
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
	rules = ActionRule.aggregate(
		user.roles if user else (),
		stationService.get_station_rules(user.id, station.id) if user else ()
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

@router.put("/enable/", status_code=status.HTTP_204_NO_CONTENT)
def enable_stations(
	stationIds: list[int] = Query(default=[]),
	includeAll: bool = Query(default=False),
	user: AccountInfo = Security(
		get_user_with_simple_scopes,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	processService: ProcessService = Depends(process_service)
) -> None:
	processService.enable_stations(stationIds, user)

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
	processService.disable_stations(stationIds, user.id)

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