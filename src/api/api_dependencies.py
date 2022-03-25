from fastapi import Depends
from sqlalchemy.engine import Connection
from musical_chairs_libs.config_loader import ConfigLoader
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.queue_service import QueueService
from collections.abc import Generator

def get_configured_db_connection(
	configLoader: ConfigLoader = Depends(ConfigLoader)
) -> Generator[Connection]:
	if not configLoader:
		configLoader = ConfigLoader()
	conn = configLoader.get_configured_db_connection()
	try:
		yield conn
	finally:
		conn.close()

def station_service(
	conn: Connection = Depends(get_configured_db_connection)
) -> StationService:
	return StationService(conn)

def history_service(
	conn: Connection = Depends(get_configured_db_connection)
) -> HistoryService:
	return HistoryService(conn)

def queue_service(
	conn: Connection = Depends(get_configured_db_connection)
) -> QueueService:
	return QueueService(conn)
