from musical_chairs_libs.services import (
	BasicUserProvider,
	CurrentUserProvider,
	EmptyUserTrackingService,
	PathRuleService,
	StationService,
	StationProcessService,
)
from musical_chairs_libs.services.fs import S3FileService
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	DbConnectionProvider
)
from sqlalchemy.exc import OperationalError
try:
	conn = DbConnectionProvider.get_configured_janitor_connection(
		ConfigAcessors.db_name()
	)

	basicUserProvider = BasicUserProvider(None)
	pathRuleService = PathRuleService(
		conn, 
		S3FileService(),
		basicUserProvider
	)
	userProvider = CurrentUserProvider(
		basicUserProvider,
		EmptyUserTrackingService(),
		pathRuleService,
	)
	stationService = StationService(
		conn,
		userProvider,
		pathRuleService
	)
	stationProcessService = StationProcessService(
		conn, 
		userProvider, 
		stationService
	)
	stationProcessService.disable_stations(station=None)
except OperationalError as ex:
	print("Could not the shutdown operation."
	" Assuming that they are already down.")
