import pytest
from musical_chairs_libs.services import (
	StationService,
	AccountsService,
	UserRoleDomain,
	UserRoleDef
)
from musical_chairs_libs.dtos_and_utilities import (
	StationCreationInfo,
	RulePriorityLevel
)
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_station_service as fixture_station_service,
	fixture_account_service as fixture_account_service
)
from .common_fixtures import *
from .mocks.db_population import get_initial_stations
from .mocks.db_data import bravo_user_id, juliet_user_id



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
	assert len(data) == 11

def test_get_stations_list_with_user_and_owner(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
	):
	stationService = fixture_station_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_bravo")
	assert user
	data = sorted(
		stationService.get_stations(user=user, ownerId=user.id),
		key=lambda s:s.id
	)
	assert len(data) == 10
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	# assert data[10].name == "zulu_station"
	# assert data[11].name == "bravo_station_rerun"
	assert len(data[0].rules) == 6
	assert len(data[1].rules) == 6
	assert len(data[2].rules) == 6
	assert len(data[3].rules) == 6
	assert len(data[4].rules) == 6
	assert len(data[5].rules) == 6
	assert len(data[6].rules) == 6
	assert len(data[7].rules) == 6
	assert len(data[8].rules) == 6
	assert len(data[9].rules) == 6
	# assert len(data[10].rules) == 0
	# assert len(data[11].rules) == 0

	user,_ = accountService.get_account_for_login("testUser_juliet")
	assert user
	data = sorted(
		stationService.get_stations(user=user, ownerId=user.id),
		key=lambda s:s.id
	)
	assert len(data) == 1
	assert data[0].name == "zulu_station"

	assert len(data[0].rules) == 5


@pytest.mark.usefixtures("fixture_clean_station_folders")
def test_save_station(
	fixture_station_service: StationService,
	fixture_primary_user: AccountInfo
	):
	stationService = fixture_station_service
	testData = StationCreationInfo(
		name = "brand_new_station",
		displayName="Brand new station"
	)
	julietUser = AccountInfo(
		id = juliet_user_id,
		username="testUser_juliet",
		email="test10@test.com"
	)
	result = stationService.save_station(testData, julietUser)
	assert result and result.id == len(get_initial_stations()) + 1
	fetched = next(stationService.get_stations(result.id))
	assert fetched.id == result.id
	assert fetched.name == "brand_new_station"
	assert fetched.displayName == "Brand new station"

	testData = StationCreationInfo(
		name = "brand_new_station_fake_tag",
		displayName="Brand new station with bad tag"
	)
	result = stationService.save_station(testData, julietUser)
	assert result and result.id == len(get_initial_stations()) + 2
	fetched = next(stationService.get_stations(result.id))


	testData = StationCreationInfo(
		name = "papa_station_update",
		displayName="Come to papa test"
	)
	bravoUser = AccountInfo(
		id = bravo_user_id,
		username="testUser_bravo",
		email="test2@test.com"
	)
	result = stationService.save_station(testData, bravoUser, 2)
	assert result and result.id == 2
	fetched = next(stationService.get_stations(result.id))
	assert fetched and fetched.name == "papa_station_update"
	assert fetched and fetched.displayName == "Come to papa test"


	testData = StationCreationInfo(
		name = "oscar_station",
		displayName="Oscar the grouch"
	)
	result = stationService.save_station(testData, fixture_primary_user, 1)
	assert result and result.id == 1
	fetched = next(stationService.get_stations(result.id))
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
	station = next(stationService.get_stations(3, user=user))
	rules = ActionRule.sorted(station.rules)
	assert rules
	assert len(rules) == 2
	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].priority == RulePriorityLevel.STATION_PATH.value
	assert rules[0].domain == UserRoleDomain.Station.value
	assert rules[0].count == 5
	assert rules[0].span == 300
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.SITE.value
	assert rules[1].domain == UserRoleDomain.Site.value
	assert rules[1].count == 10
	assert rules[1].span == 300

	user,_ = accountService.get_account_for_login("testUser_oscar")
	assert user
	station = next(stationService.get_stations(3, user=user))
	rules = ActionRule.sorted(station.rules)
	assert rules
	assert len(rules) == 2

	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].priority == RulePriorityLevel.STATION_PATH.value + 1
	assert rules[0].domain == UserRoleDomain.Site.value
	assert rules[0].count == 5
	assert rules[0].span == 120
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.STATION_PATH.value
	assert rules[1].domain == UserRoleDomain.Station.value
	assert rules[1].count == 5
	assert rules[1].span == 60

	user,_ = accountService.get_account_for_login("testUser_papa")
	assert user
	station = next(stationService.get_stations(3, user=user))
	rules = ActionRule.sorted(station.rules)
	assert rules
	assert len(rules) == 2
	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].priority == RulePriorityLevel.STATION_PATH.value
	assert rules[0].domain == UserRoleDomain.Station.value
	assert rules[0].count == 25
	assert rules[0].span == 300
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.SITE.value
	assert rules[1].domain == UserRoleDomain.Site.value
	assert rules[1].count == 20
	assert rules[1].span == 300

	user,_ = accountService.get_account_for_login("testUser_quebec")
	assert user
	station = next(stationService.get_stations(3, user=user))
	rules = ActionRule.sorted(station.rules)
	assert rules
	assert len(rules) == 2
	assert rules[0].domain == UserRoleDomain.Station.value
	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].priority == RulePriorityLevel.STATION_PATH.value
	assert rules[0].count == 25
	assert rules[0].span == 300

	assert rules[1].domain == UserRoleDomain.Site.value
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.SITE.value
	assert rules[1].count == 15
	assert rules[1].span == 300


def test_get_stations_with_view_security(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
):
	stationService = fixture_station_service
	accountService = fixture_account_service

	#no user
	data = sorted(
		stationService.get_stations(),
		key=lambda s:s.id
	)
	assert len(data) == 11
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	assert data[10].name == "zulu_station"

	#user no roles
	user,_ = accountService.get_account_for_login("testUser_romeo")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	assert data[10].name == "zulu_station"
	assert data[11].name == "bravo_station_rerun"

	#user with a site rule
	user,_ = accountService.get_account_for_login("testUser_whiskey")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	assert data[10].name == "zulu_station"
	assert data[11].name == "alpha_station_rerun"
	assert data[12].name == "bravo_station_rerun"

	#user invited to see a station
	user,_ = accountService.get_account_for_login("testUser_xray")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	assert data[10].name == "zulu_station"
	assert data[11].name == "bravo_station_rerun"
	assert data[12].name == "charlie_station_rerun"

	#owner a station
	user,_ = accountService.get_account_for_login("testUser_yankee")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13
	assert data[0].name == "oscar_station"
	assert data[1].name == "papa_station"
	assert data[2].name == "romeo_station"
	assert data[3].name == "sierra_station"
	assert data[4].name == "tango_station"
	assert data[5].name == "yankee_station"
	assert data[6].name == "uniform_station"
	assert data[7].name == "victor_station"
	assert data[8].name == "whiskey_station"
	assert data[9].name == "xray_station"
	assert data[10].name == "zulu_station"
	assert data[11].name == "bravo_station_rerun"
	assert data[12].name == "delta_station_rerun"
	pass

	user,_ = accountService.get_account_for_login("testUser_juliet")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12