from musical_chairs_libs.services import (
	StationProcessService,
)
from musical_chairs_libs.dtos_and_utilities import ConfigAcessors
from sqlalchemy.exc import OperationalError
try:
	conn = ConfigAcessors.get_configured_janitor_connection(
		ConfigAcessors.db_name()
	)
	stationProcessService = StationProcessService(conn)
	stationProcessService.disable_stations(stationId=None)
except OperationalError as ex:
	print("Could not the shutdown operation."
	" Assuming that they are already down.")
