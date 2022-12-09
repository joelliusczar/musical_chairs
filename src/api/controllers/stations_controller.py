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
	HistoryItem,
	SongListDisplayItem,
	StationInfo,
	TableData,
	UserRoleDef,
	build_error_obj
)
from musical_chairs_libs.services import (
	StationService,
	QueueService,
	ProcessService
)
from api_dependencies import (
	station_service,
	queue_service,
	get_current_user,
	process_service
)


router = APIRouter(prefix="/stations")

@router.get("/list")
def index(
	stationService: StationService = Depends(station_service)
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_stations())
	return { "items": stations }

@router.get("/{stationName}/history/")
def history(
	stationName: str,
	page: int = 0,
	limit: int = 50,
	queueService: QueueService = Depends(queue_service)
) -> TableData[HistoryItem]:
	if not stationName:
		return TableData(totalRows=0, items=[])
	history = list(queueService \
		.get_history_for_station(
			stationName=stationName,
			page = page,
			limit = limit
		))
	totalRows = queueService.history_count(stationName = stationName)
	return TableData(totalRows=totalRows, items=history)

@router.get("/{stationName}/queue/")
def queue(
	stationName: str,
	queueService: QueueService = Depends(queue_service)
) -> CurrentPlayingInfo:
	if not stationName:
		return CurrentPlayingInfo(nowPlaying=None, items=[], totalRows=0)
	queue = queueService.get_now_playing_and_queue(stationName=stationName)
	return queue

@router.get("/{stationName}/catalogue/")
def song_catalogue(
	stationName: str,
	page: int = 0,
	limit: int = 50,
	stationService: StationService = Depends(station_service)
) -> TableData[SongListDisplayItem]:
	if not stationName:
		return TableData(totalRows=0, items=[])
	songs = list(
		stationService.get_station_song_catalogue(
			stationName = stationName,
			page = page,
			limit = limit
		)
	)
	totalRows = stationService.song_catalogue_count(stationName = stationName)
	return TableData(totalRows=totalRows, items=songs)

@router.post("/{stationName}/request/{songId}")
def request_song(
	stationName: str,
	songId: int,
	queueService: QueueService = Depends(queue_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.STATION_REQUEST.value]
	)
):
	try:
		queueService.add_song_to_queue(songId, stationName, user)
	except (LookupError, RuntimeError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = str(ex)
		)

@router.delete("/{stationName}/request/",
	dependencies=[
		Security(get_current_user, scopes=[UserRoleDef.STATION_SKIP.value])
	]
)
def remove_song_from_queue(
	stationName: str,
	id: int,
	queuedTimestamp: float,
	queueService: QueueService = Depends(queue_service)
) -> CurrentPlayingInfo:
	queue = queueService.remove_song_from_queue(
		id,
		queuedTimestamp,
		stationName=stationName
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
	stationService: StationService = Depends(station_service)
) -> dict[str, bool]:
	return {
		"name": stationService.is_stationName_used(id, name)
	}

def get_station(
	id: Optional[int]=None,
	name: Optional[str]=None,
	stationService: StationService = Depends(station_service)
) -> StationInfo:
	stationInfo = stationService.get_station_for_edit(
		stationId=id,
		stationName=name
	)
	if stationInfo is None:
		msg = f"{id or name or 'Station'} not found"
		field = "id" if id else "name" \
			if name else None
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(msg, field)]
		)
	return stationInfo

@router.get("")
def get_station_for_edit(
	stationInfo: StationInfo = Depends(get_station)
) -> StationInfo:
	return stationInfo

@router.post("")
def create_station(
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station, userId=user.id)
	return result or StationInfo(id=-1,name="",displayName="")

@router.put("")
def update_station(
	id: int,
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station, id, userId=user.id)
	return result or StationInfo(id=-1,name="",displayName="")

@router.put("/enable/",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(get_current_user, scopes=[UserRoleDef.STATION_FLIP.value])
	]
)
def enable_stations(
	id: list[int] = Query(default=[]),
	name: list[str] = Query(default=[]),
	processService: ProcessService = Depends(process_service)
) -> None:
	processService.enable_stations(id, name)

@router.put("/disable/",
	status_code=status.HTTP_204_NO_CONTENT,
	dependencies=[
		Security(get_current_user, scopes=[UserRoleDef.STATION_FLIP.value])
	]
)
def disable_stations(
	id: list[int] = Query(default=[]),
	name: list[str] = Query(default=[]),
	processService: ProcessService = Depends(process_service)
) -> None:
	processService.disable_stations(id, name)