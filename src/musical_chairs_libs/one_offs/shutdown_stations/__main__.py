from musical_chairs_libs.services.station_service import StationService
from sqlalchemy.exc import OperationalError
try:
	stationService = StationService()
	stationService.disable_stations(stationIds=None)
except OperationalError as ex:
	print("Could not the shutdown operation."
	" Assuming that they are already down.")
