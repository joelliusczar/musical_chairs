from musical_chairs_libs.services import (
	StationService,
	QueueService,
	EnvManager,
)
from datetime import datetime, timedelta, timezone

envManager = EnvManager()
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
		print(f"Deleted from queue count: {result[2]}")
except Exception as e:
	print(e)
finally:
	conn.close()