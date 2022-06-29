#pyright: reportMissingTypeStubs=false
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Security, HTTPException, status
from musical_chairs_libs.dtos_and_utilities import AccountInfo,\
	CurrentPlayingInfo,\
	HistoryItem,\
	SongItem,\
	StationCreationInfo,\
	StationInfo,\
	TableData,\
	UserRoleDef,\
	build_error_obj
from musical_chairs_libs.services import\
	StationService,\
	HistoryService,\
	QueueService,\
	TagService
from api_dependencies import \
	station_service,\
	history_service,\
	queue_service,\
	get_current_user,\
	tag_service


router = APIRouter(prefix="/stations")

@router.get("/list")
def index(
	stationService: StationService = Depends(station_service)
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_stations_with_songs_list())
	return { "items": stations }

@router.get("/{stationName}/history")
def history(
	stationName: str,
	historyService: HistoryService = Depends(history_service)
) -> Dict[str, List[HistoryItem]]:
	if not stationName:
		return {}
	history = list(historyService \
		.get_history_for_station(stationName=stationName))
	return {"items": history }

@router.get("/{stationName}/queue")
def queue(
	stationName: str,
	queueService: QueueService = Depends(queue_service)
) -> CurrentPlayingInfo:
	if not stationName:
		return CurrentPlayingInfo(nowPlaying=None, items=[])
	queue = queueService.get_now_playing_and_queue(stationName=stationName)
	return queue

@router.get("/{stationName}/catalogue")
def song_catalogue(
	stationName: str,
	page: int = 0,
	limit: int = 50,
	stationService: StationService = Depends(station_service)
) -> TableData[SongItem]:
	if not stationName:
		return TableData(totalRows=0, items=[])
	songs = list(
		stationService.get_station_song_catalogue(
			stationName = stationName,\
			page = page,\
			limit = limit
		)
	)
	totalRows = stationService.song_catalogue_count(stationName = stationName)
	return TableData(totalRows=totalRows, items=songs)

@router.post("/{stationName}/request/{songPk}")
def request_song(
	stationName: str,
	songPk: int,
	queueService: QueueService = Depends(queue_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.SONG_REQUEST.value]
	)
):
	try:
		queueService.add_song_to_queue(songPk, stationName, user)
	except (LookupError, RuntimeError) as ex:
		raise HTTPException(
			status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail = str(ex)
		)

@router.get("/check")
def is_phrase_used(
	name: str = "",
	stationService: StationService = Depends(station_service)
) -> dict[str, bool]:
	return {
		"name": stationService.is_stationName_used(name)
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

def extra_validated_station(
	station: StationCreationInfo,
	tagService: TagService = Depends(tag_service)
) -> StationCreationInfo:
	tagIds = {t.id for t in station.tags or []}
	dbTags = {t.id for t in tagService.get_tags(tagIds=tagIds)}
	if tagIds - dbTags:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Tags associated with ids {str(tagIds)} do not exist", "tags")],
		)
	return station

@router.post("")
def create_station(
	station: StationCreationInfo = Depends(extra_validated_station),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station, userId=user.id)
	return result or StationInfo(id=-1,name="",displayName="",tags=[])

@router.put("")
def update_station(
	id: int,
	station: StationCreationInfo  = Depends(extra_validated_station),
	stationService: StationService = Depends(station_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.STATION_EDIT()]
	)
) -> StationInfo:
	result = stationService.save_station(station, id, userId=user.id)
	return result or StationInfo(id=-1,name="",displayName="",tags=[])


# def request(self, stationName, songPk):
#	 r = cherrypy.request
#	 resultCount = self.queue_service.add_song_to_queue(stationName, songPk)
#	 return resultCount