import pytest
from musical_chairs_libs.services import (
	StationService,
	AccountsService,
	UserRoleDomain
)
from musical_chairs_libs.dtos_and_utilities import StationCreationInfo
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_station_service as fixture_station_service,
	fixture_account_service as fixture_account_service
)
from .common_fixtures import *
from .mocks.db_population import get_initial_stations


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
	data = list(stationService.get_stations())
	assert len(data) == 10

@pytest.mark.usefixtures("fixture_clean_station_folders")
def test_save_station(fixture_station_service: StationService):
	stationService = fixture_station_service
	testData = StationCreationInfo(
		name = "brand_new_station",
		displayName="Brand new station"
	)
	result = stationService.save_station(testData)
	assert result and result.id == len(get_initial_stations()) + 1
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.id == result.id
	assert fetched and fetched.name == "brand_new_station"
	assert fetched and fetched.displayName == "Brand new station"

	testData = StationCreationInfo(
		name = "brand_new_station_fake_tag",
		displayName="Brand new station with bad tag"
	)
	result = stationService.save_station(testData)
	assert result and result.id == len(get_initial_stations()) + 2
	fetched = stationService.get_station_for_edit(result.id)


	testData = StationCreationInfo(
		name = "papa_station_update",
		displayName="Come to papa test"
	)
	result = stationService.save_station(testData, 2)
	assert result and result.id == 2
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.name == "papa_station_update"
	assert fetched and fetched.displayName == "Come to papa test"

	testData = StationCreationInfo(
		name = "oscar_station",
		displayName="Oscar the grouch"
	)
	result = stationService.save_station(testData, 1)
	assert result and result.id == 1
	fetched = stationService.get_station_for_edit(result.id)
	assert fetched and fetched.name == "oscar_station"
	assert fetched and fetched.displayName == "Oscar the grouch"

def test_get_station_user_rule_selection(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
):
	stationService = fixture_station_service
	accountService = fixture_account_service

	user,_ = accountService.get_account_for_login("testUser_november")
	assert user
	stationUser = stationService.get_station_user(user,3)
	assert stationUser
	assert len(stationUser.roles) == 1
	assert stationUser.roles[0].id == 6
	stationUser = stationService.get_station_user(user,4)
	assert stationUser
	assert len(stationUser.roles) == 1
	assert stationUser.roles[0].id == 5
	user,_ = accountService.get_account_for_login("testUser_oscar")
	assert user
	stationUser = stationService.get_station_user(user,3)
	assert stationUser
	assert len(stationUser.roles) == 1
	assert stationUser.roles[0].id == 7

	user,_ = accountService.get_account_for_login("testUser_papa")
	assert user
	stationUser = stationService.get_station_user(user,3)
	assert stationUser
	assert len(stationUser.roles) == 1
	assert stationUser.roles[0].id == 10

	user,_ = accountService.get_account_for_login("testUser_quebec")
	assert user
	stationUser = stationService.get_station_user(user,3)
	assert stationUser
	assert len(stationUser.roles) == 2
	assert stationUser.roles[0].id == None
	assert stationUser.roles[0].domain == UserRoleDomain.Site

	assert stationUser.roles[1].id == 12
	assert stationUser.roles[1].domain == UserRoleDomain.Station
