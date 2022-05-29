from musical_chairs_libs.station_service import StationService
from .constant_fixtures_for_test import test_password as test_password,\
	primary_user as primary_user,\
	test_date_ordered_list as test_date_ordered_list
from .common_fixtures import \
	db_conn as db_conn, \
	db_conn_in_mem_full as db_conn_in_mem_full, \
	station_service_in_mem as station_service_in_mem


def test_if_song_can_be_added_to_station(
	station_service_in_mem: StationService
):
	stationService = station_service_in_mem
	result = stationService.can_song_be_queued_to_station(15, 1)
	assert result == True
	result = stationService.can_song_be_queued_to_station(15, 2)
	assert result == False
	result = stationService.can_song_be_queued_to_station(36, 1)
	assert result == False