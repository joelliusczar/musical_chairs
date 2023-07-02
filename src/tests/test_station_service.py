import pytest
from musical_chairs_libs.services import (
	StationService,
	AccountsService,
	UserRoleDef,
	StationActionRule
)
from musical_chairs_libs.dtos_and_utilities import (
	StationCreationInfo,
	RulePriorityLevel,
	MinItemSecurityLevel
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

def test_get_stations_list_with_admin(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
	):
	stationService = fixture_station_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == len(get_initial_stations())
	data = sorted(
		stationService.get_stations(user=user, stationKeys=16),
		key=lambda s:s.id
	)
	assert len(data) == 1
	assert data[0].viewSecurityLevel == MinItemSecurityLevel.LOCKED.value

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
	assert len(data[0].rules) == 8
	assert len(data[1].rules) == 8
	assert len(data[2].rules) == 8
	assert len(data[3].rules) == 8
	assert len(data[4].rules) == 8
	assert len(data[5].rules) == 8
	assert len(data[6].rules) == 8
	assert len(data[7].rules) == 8
	assert len(data[8].rules) == 8
	assert len(data[9].rules) == 8
	# assert len(data[10].rules) == 0
	# assert len(data[11].rules) == 0

	#juliet doesn't have have the station create role
	user,_ = accountService.get_account_for_login("testUser_juliet")
	assert user
	data = sorted(
		stationService.get_stations(user=user, ownerId=user.id),
		key=lambda s:s.id
	)
	assert len(data) == 1
	assert data[0].name == "zulu_station"

	assert len(data[0].rules) == 7


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
	assert isinstance(rules[0], StationActionRule)
	assert rules[0].count == 5
	assert rules[0].span == 300
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.SITE.value
	assert not isinstance(rules[1], StationActionRule)
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
	assert not isinstance(rules[0], StationActionRule)
	assert rules[0].count == 5
	assert rules[0].span == 120
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.STATION_PATH.value
	assert isinstance(rules[1],StationActionRule)
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
	assert isinstance(rules[0],StationActionRule)
	assert rules[0].count == 25
	assert rules[0].span == 300
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].priority == RulePriorityLevel.SITE.value
	assert not isinstance(rules[1],StationActionRule)
	assert rules[1].count == 20
	assert rules[1].span == 300

	user,_ = accountService.get_account_for_login("testUser_quebec")
	assert user
	station = next(stationService.get_stations(3, user=user))
	rules = ActionRule.sorted(station.rules)
	assert rules
	assert len(rules) == 2
	assert isinstance(rules[0],StationActionRule)
	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].priority == RulePriorityLevel.STATION_PATH.value
	assert rules[0].count == 25
	assert rules[0].span == 300

	assert not isinstance(rules[1],StationActionRule)
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
	assert len(data) == 13


def test_get_stations_with_scopes(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
):
	stationService = fixture_station_service
	accountService = fixture_account_service

	#no user
	data = sorted(
		stationService.get_stations(
			scopes=[UserRoleDef.STATION_ASSIGN.value]
		),
		key=lambda s:s.id
	)
	assert len(data) == 0

	#user no roles
	user,_ = accountService.get_account_for_login("testUser_romeo")
	assert user
	data = sorted(
		stationService.get_stations(
			user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12

	data = sorted(
		stationService.get_stations(
			user=user,
			scopes=[UserRoleDef.STATION_ASSIGN.value]
		),
		key=lambda s:s.id
	)
	assert len(data) == 0

	user,_ = accountService.get_account_for_login("testUser_india")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 13

	data = sorted(
		stationService.get_stations(
			user=user,
			scopes=[UserRoleDef.STATION_ASSIGN.value]
		),
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
	for station in data:
		assert len(station.rules) == 1

	user,_ = accountService.get_account_for_login("testUser_hotel")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12

	data = sorted(
		stationService.get_stations(
			user=user,
			scopes=[UserRoleDef.STATION_ASSIGN.value]
		),
		key=lambda s:s.id
	)

	assert len(data) == 1
	assert len(data[0].rules) == 1

def test_get_stations_with_odd_priority(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
):
	stationService = fixture_station_service
	accountService = fixture_account_service

	user,_ = accountService.get_account_for_login("testUser_zulu")
	assert user
	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12

	user,_ = accountService.get_account_for_login("testUser_alice")
	assert user

	data = sorted(
		stationService.get_stations(user=user),
		key=lambda s:s.id
	)
	assert len(data) == 12

def test_get_station_user_list(
	fixture_station_service: StationService,
	fixture_account_service: AccountsService
):
	stationService = fixture_station_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("ingo")
	assert user

	station = next(stationService.get_stations(17, user=user))
	result = sorted(stationService.get_station_users(station), key=lambda u: u.id)
	assert len(result) == 5
	assert result[0].username == "carl"
	assert len(result[0].roles) == 1
	assert result[0].roles[0].name == UserRoleDef.STATION_FLIP.value

	assert result[1].username == "george"
	assert len(result[1].roles) == 3
	rules = sorted(result[1].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_FLIP.value
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[2].name == UserRoleDef.STATION_VIEW.value

	assert result[2].username == "horsetel"
	assert len(result[2].roles) == 1
	rules = sorted(result[2].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_VIEW.value

	assert result[3].username == "ingo"
	assert len(result[3].roles) == 6
	rules = sorted(result[3].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_ASSIGN.value
	assert rules[1].name == UserRoleDef.STATION_DELETE.value
	assert rules[2].name == UserRoleDef.STATION_EDIT.value
	assert rules[3].name == UserRoleDef.STATION_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.STATION_USER_LIST.value
	assert rules[5].name == UserRoleDef.STATION_VIEW.value

	assert result[4].username == "narlon"
	assert len(result[4].roles) == 3
	rules = sorted(result[4].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_ASSIGN.value
	assert rules[1].name == UserRoleDef.STATION_REQUEST.value
	assert rules[1].span == 5
	assert rules[1].count == 300
	assert rules[2].name == UserRoleDef.STATION_VIEW.value

	station = next(stationService.get_stations(18, user=user))
	result = sorted(stationService.get_station_users(station), key=lambda u: u.id)
	assert len(result) == 2
	assert result[0].username == "ingo"
	assert len(result[0].roles) == 6
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_ASSIGN.value
	assert rules[1].name == UserRoleDef.STATION_DELETE.value
	assert rules[2].name == UserRoleDef.STATION_EDIT.value
	assert rules[3].name == UserRoleDef.STATION_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.STATION_USER_LIST.value
	assert rules[5].name == UserRoleDef.STATION_VIEW.value

	assert result[1].username == "narlon"
	assert len(result[1].roles) == 2
	rules = sorted(result[1].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_REQUEST.value
	assert rules[0].span == 100
	assert rules[0].count == 300
	assert rules[1].name == UserRoleDef.STATION_VIEW.value

	user,_ = accountService.get_account_for_login("testUser_victor")
	station = next(stationService.get_stations(12, user=user))
	result = sorted(stationService.get_station_users(station), key=lambda u: u.id)
	assert len(result) == 1
	assert result[0].username == "testUser_victor"
	assert len(result[0].roles) == 6
	rules = sorted(result[0].roles, key=lambda r: r.name)
	assert rules[0].name == UserRoleDef.STATION_ASSIGN.value
	assert rules[1].name == UserRoleDef.STATION_DELETE.value
	assert rules[2].name == UserRoleDef.STATION_EDIT.value
	assert rules[3].name == UserRoleDef.STATION_USER_ASSIGN.value
	assert rules[4].name == UserRoleDef.STATION_USER_LIST.value
	assert rules[5].name == UserRoleDef.STATION_VIEW.value