from musical_chairs_libs.services import (
	StationService,
	QueueService,
)
from musical_chairs_libs.dtos_and_utilities import ConfigAcessors
from datetime import datetime, timedelta, timezone

envManager = ConfigAcessors()
conn = envManager.get_configured_janitor_connection(
	"musical_chairs_db"
)
try:
	stationService = StationService(conn)
	queueService = QueueService(conn, stationService)
	stations = list(stationService.get_stations())
	dt = datetime.now(timezone.utc)
	cutoffDate = (dt - timedelta(days=7)).timestamp()
	print(f"Cut off date: {cutoffDate}")
	for station in stations:
		result = queueService.squish_station_history(station.id, cutoffDate)
		print(f"Added count: {result[0]}")
		print(f"Updated count: {result[1]}")
		print(f"Deleted count: {result[2]}")

finally:
	conn.close()
