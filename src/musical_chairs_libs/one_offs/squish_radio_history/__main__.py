import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.services  as mcr
from datetime import datetime, timedelta, timezone
from musical_chairs_libs.services.fs import S3FileService

with dtos.DbConnectionProvider.get_configured_janitor_connection(
	"musical_chairs_db"
) as conn:
	currentUserProvider = mcr.NonUserProvider()
	fileService = S3FileService()
	pathRuleService = mcr.PathRuleService(conn, fileService, currentUserProvider)
	stationService = mcr.StationService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	songInfoService = mcr.SongInfoService(
		conn,
		currentUserProvider,
		pathRuleService
	)
	queueService = mcr.QueueService(
		conn,
		currentUserProvider,
		songInfoService,
		pathRuleService,
		stationService
	)
	stations = list(stationService.get_stations())
	dt = datetime.now(timezone.utc)
	cutoffDate = (dt - timedelta(days=7)).timestamp()
	print(f"Cut off date: {cutoffDate}")
	for station in stations:
		result = queueService.squish_station_history(station, cutoffDate)
		print(f"Added count: {result[0]}")
		print(f"Updated count: {result[1]}")
		print(f"Deleted count: {result[2]}")

