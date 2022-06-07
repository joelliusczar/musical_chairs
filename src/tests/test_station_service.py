from musical_chairs_libs.station_service import StationService
from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem, \
	fixture_station_service as fixture_station_service


def test_if_song_can_be_added_to_station(
	fixture_station_service: StationService
):
	stationService = fixture_station_service
	result = stationService.can_song_be_queued_to_station(15, 1)
	assert result == True
	result = stationService.can_song_be_queued_to_station(15, 2)
	assert result == False
	result = stationService.can_song_be_queued_to_station(36, 1)
	assert result == False