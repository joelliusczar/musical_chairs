from typing import cast
from musical_chairs_libs.services import StationService
from musical_chairs_libs.dtos_and_utilities import StationCreationInfo, Tag
from .constant_fixtures_for_test import *
from .common_fixtures import \
	fixture_station_service as fixture_station_service
from .common_fixtures import *
from .mocks.db_population import get_initial_tags, get_initial_stations


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

def test_get_stations_list(fixture_station_service: StationService):
	stationService = fixture_station_service
	data = list(stationService.get_stations_with_songs_list())
	assert len(data) == 2


def test_save_station(fixture_station_service: StationService):
	stationService = fixture_station_service
	testData = StationCreationInfo(
		name = "brand_new_station",
		displayName="Brand new station",
		tags=[Tag(id=3, name="mike_tag"), Tag(id=5, name="oscar_tag")]
	)
	result = stationService.save_station(testData)
	assert result and result.id == len(get_initial_stations()) + 1
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.id == result.id
	assert fetched and fetched.name == "brand_new_station"
	assert fetched and fetched.displayName == "Brand new station"
	assert fetched and fetched.tags and len(fetched.tags) == 2


	nonExistentTagId = max(cast(int, t["pk"]) for t in  get_initial_tags()) + 2
	testData = StationCreationInfo(
		name = "brand_new_station_fake_tag",
		displayName="Brand new station with bad tag",
		tags=[Tag(id=3, name="mike_tag"), Tag(id=nonExistentTagId, name="bad_tag")]
	)
	result = stationService.save_station(testData)
	assert result and result.id == len(get_initial_stations()) + 2
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.tags and len(fetched.tags) == 1


	testData = StationCreationInfo(
		name = "papa_station_update",
		displayName="Come to papa test",
		tags=[Tag(id=3, name="mike_tag"), Tag(id=5, name="oscar_tag")]
	)
	result = stationService.save_station(testData, 2)
	assert result and result.id == 2
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.name == "papa_station_update"
	assert fetched and fetched.displayName == "Come to papa test"
	assert fetched and fetched.tags and len(fetched.tags) == 2

	testData = StationCreationInfo(
		name = "oscar_station",
		displayName="Oscar the grouch",
		tags=[
			Tag(id=2, name="badlima_tag"),
			Tag(id=4, name="november_tag"),
			Tag(id=7, name="badromeo_tag")
		]
	)
	result = stationService.save_station(testData, 1)
	assert result and result.id == 1
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.name == "oscar_station"
	assert fetched and fetched.displayName == "Oscar the grouch"
	assert fetched and fetched.tags and len(fetched.tags) == 3

def test_save_with_duplicate_tags(fixture_station_service: StationService):
	stationService = fixture_station_service

	testData = StationCreationInfo(
		name = "oscar_station",
		displayName="Oscar the grouch",
		tags=[
			Tag(id=2, name="badlima_tag"),
			Tag(id=2, name="november_tag"),
			Tag(id=7, name="badromeo_tag")
		]
	)
	result = stationService.save_station(testData, 1)
	assert result and result.id == 1
	assert result.tags and len(result.tags) == 2
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.name == "oscar_station"
	assert fetched and fetched.displayName == "Oscar the grouch"
	assert fetched and fetched.tags and len(fetched.tags) == 2