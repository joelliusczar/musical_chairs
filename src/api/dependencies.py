import os
from fastapi import Depends
from sqlalchemy.engine import Connection
from musical_chairs_libs.config_loader import ConfigLoader
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.queue_service import QueueService

def config_loader() -> ConfigLoader:
	return ConfigLoader()

def conn(configLoader: ConfigLoader = Depends(config_loader)) -> Connection:
	return configLoader.get_configured_db_connection()

def station_service(conn: Connection = Depends(conn)) -> StationService:
	return StationService(conn)

def history_service(conn: Connection = Depends(conn), 
	stationService: StationService = Depends(station_service)
) -> HistoryService:
	return HistoryService(conn, stationService)

def queue_service(
	conn: Connection = Depends(conn), 
	stationService: StationService = Depends(station_service),
	historyService: HistoryService = Depends(history_service)
) -> QueueService:
	return QueueService(conn, stationService, historyService)