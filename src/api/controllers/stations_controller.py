#pyright: reportMissingTypeStubs=false
from typing import Dict, List, Optional, Union
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
	TableData,
	UserRoleDef,
	build_error_obj,
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
	get_owner_from_path,
	get_station_by_name_and_owner,
	get_current_user_simple,
	get_user_with_rate_limited_scope
)


router = APIRouter(prefix="/stations")

@router.get("/list")
def index(
	stationService: StationService = Depends(station_service),
	owner: Optional[AccountInfo] = Depends(get_owner_from_path)
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_stations(
		ownerKey=owner.id if owner else None)
	)
	return { "items": stations }

@router.get("/{ownerKey}/{stationKey}/history/")
def history(
	page: int = 0,
	limit: int = 50,
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service)
) -> TableData[SongListDisplayItem]:
	if not station:
		return TableData(totalRows=0, items=[])
	history = list(queueService \
		.get_history_for_station(
			stationId=station.id,
			page = page,
			limit = limit
		))
	totalRows = queueService.history_count(stationId=station.id)
	return TableData(totalRows=totalRows, items=history)

@router.get("/{ownerKey}/{stationKey}/queue/")
def queue(
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	queueService: QueueService = Depends(queue_service)
) -> CurrentPlayingInfo:
	if not station:
		return CurrentPlayingInfo(
			nowPlaying=None,
			items=[],
			totalRows=0,
			requestRule=ActionRule("")
		)
	queue = queueService.get_now_playing_and_queue(stationId=station.id)
	return queue

@router.get("/{ownerKey}/{stationKey}/catalogue/")
def song_catalogue(
	page: int = 0,
	limit: int = 50,
	station: Optional[StationInfo] = Depends(get_station_by_name_and_owner),
	stationService: StationService = Depends(station_service)
) -> TableData[SongListDisplayItem]:
	if not station:
		return TableData(totalRows=0, items=[])
	songs = list(
		stationService.get_station_song_catalogue(
			stationId = station.id,
			page = page,
			limit = limit
		)
	)
	totalRows = stationService.song_catalogue_count(
		stationId = station.id
	)
	return TableData(totalRows=totalRows, items=songs)

@router.post("/{ownerKey}/{stationName}/request/{songId}")
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

@router.get("/{ownerKey}/{stationName}/")
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
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station, user=user)
	return result or StationInfo(id=-1,name="",displayName="")

@router.put("")
def update_station(
	id: int,
	station: ValidatedStationCreationInfo = Body(default=None),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station,user, id)
	return result or StationInfo(id=-1,name="",displayName="")

@router.put("/enable/", status_code=status.HTTP_204_NO_CONTENT)
def enable_stations(
	stationKeys: Union[list[int],str] = Query(default=[]),
	user: AccountInfo = Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	processService: ProcessService = Depends(process_service)
) -> None:
	processService.enable_stations(stationKeys, user.id)

@router.put("/disable/", status_code=status.HTTP_204_NO_CONTENT)
def disable_stations(
	stationKeys: Union[list[int],str] = Query(default=[]),
	user: AccountInfo = Security(
		get_station_user,
		scopes=[UserRoleDef.STATION_FLIP.value]
	),
	processService: ProcessService = Depends(process_service)
) -> None:
	if user.isAdmin and stationKeys == "**":
		processService.disable_stations("*", None)
	else:
		processService.disable_stations(stationKeys, user.id)