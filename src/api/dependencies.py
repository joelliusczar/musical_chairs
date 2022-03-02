import os
from fastapi import Depends
from sqlalchemy.engine import Connection
from musical_chairs_libs.config_loader import ConfigLoader
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.queue_service import QueueService

def configLoader() -> ConfigLoader:
	return ConfigLoader()

def conn(configLoader: ConfigLoader = Depends(configLoader)) -> Connection:
	return configLoader.get_configured_db_connection()

def historyService(conn: Connection = Depends(conn)) -> HistoryService:
	return HistoryService(conn)

def stationService(conn: Connection = Depends(conn)) -> StationService:
	return StationService(conn)

def queueService(conn: Connection = Depends(conn), 
stationService: StationService = Depends(stationService)) -> QueueService:
	return QueueService(conn, stationService)