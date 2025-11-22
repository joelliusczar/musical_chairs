from musical_chairs_libs.services import (
	StationProcessService,
	EnvManager
)
from sqlalchemy.exc import OperationalError
try:
	conn = EnvManager.get_configured_janitor_connection(
		EnvManager.db_name()
	)
	stationProcessService = StationProcessService(conn)
	stationProcessService.disable_stations(stationIds=None)
except OperationalError as ex:
	print("Could not the shutdown operation."
	" Assuming that they are already down.")
