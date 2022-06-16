#pyright: reportMissingTypeStubs=false
from typing import Dict, List
from fastapi import APIRouter, Depends, Security, HTTPException, status
from musical_chairs_libs.dtos import AccountInfo,\
	CurrentPlayingInfo,\
	HistoryItem,\
	SongItem,\
	StationInfo,\
	TableData,\
	UserRoleDef
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.queue_service import QueueService
from api_dependencies import \
	station_service,\
	history_service,\
	queue_service,\
	get_current_user


router = APIRouter(prefix="/stations")

@router.get("/")
def index(
	stationService: StationService = Depends(station_service)
) -> Dict[str, List[StationInfo]]:
	stations = list(stationService.get_station_list())
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
		return CurrentPlayingInfo(None, [])
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
# def request(self, stationName, songPk):
#	 r = cherrypy.request
#	 resultCount = self.queue_service.add_song_to_queue(stationName, songPk)
#	 return resultCount