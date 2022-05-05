from typing import Iterator
from fastapi import Depends
from sqlalchemy.engine import Connection
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.queue_service import QueueService

def get_configured_db_connection(
	envManager: EnvManager = Depends(EnvManager)
) -> Iterator[Connection]:
	if not envManager:
		envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
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
