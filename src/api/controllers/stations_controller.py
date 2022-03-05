from typing import Dict
from fastapi import APIRouter, Depends
from musical_chairs_libs.station_service import StationService

from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.queue_service import QueueService
from dependencies import station_service, history_service, queue_service

router = APIRouter(prefix="/api/stations")

@router.get("/")
def index(stationService: StationService = Depends(station_service)):
	stations = list(stationService.get_station_list())
	return { "items": stations }

@router.get("/{stationName}/history")
def history(
	stationName: str, 
	historyService: HistoryService = Depends(history_service)
) -> Dict:
	if not stationName:
		return []
	history = list(historyService \
		.get_history_for_station(stationName=stationName))
	return {"items": history }

@router.get("/{stationName}/queue")
def queue(
	stationName: str, 
	queueService: QueueService = Depends(queue_service)
):
	if not stationName:
		return []
	queue = queueService.get_now_playing_and_queue(stationName=stationName)
	return queue

@router.get("/{stationName}/catalogue")
def song_catalogue(stationName: str, 
	stationService: StationService = Depends(station_service)
):
	if not stationName:
		return []
	songs = list(stationService\
		.get_station_song_catalogue(stationName=stationName))
	return { "items": songs}

# def request(self, stationName, songPk):
#	 r = cherrypy.request
#	 resultCount = self.queue_service.add_song_to_queue(stationName, songPk)
#	 return resultCount