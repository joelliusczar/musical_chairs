#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
import pytest
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from datetime import datetime, timezone
from musical_chairs_libs.tables import stations_history, station_queue
from musical_chairs_libs.accounts_service import AccountsService,\
	UserRoleDef
from musical_chairs_libs.dtos import AccountInfo, AccountCreationInfo
from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem, \
	fixture_account_service as fixture_account_service

currentTestDate: datetime = datetime.now(timezone.utc)

def _insert_row_into_history(conn: Connection, userPk: int):
	queuedTimestamp = \
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=10,
			tzinfo=timezone.utc
		).timestamp()
	historyParams = [{
			"stationFk": 1,
			"songFk": 15,
			"playedTimestamp": datetime(
				year=2022,
				month=5,
				day=27,
				hour=19,
				minute=20,
				tzinfo=timezone.utc
			).timestamp(),
			"queuedTimestamp": queuedTimestamp,
			"requestedTimestamp": queuedTimestamp,
			"requestedByUserFk": userPk
		}
	]
	stmt = insert(stations_history)
	conn.execute(stmt, historyParams) #pyright: ignore [reportUnknownMemberType]

@pytest.fixture
def fixture_account_service_mock_current_time(
	fixture_account_service: AccountsService
):
	def _get_test_datetime() -> datetime:
		global currentTestDate
		if not currentTestDate:
			currentTestDate = datetime.now(timezone.utc)
		return currentTestDate
	fixture_account_service.get_datetime = _get_test_datetime
	return fixture_account_service

def test_when_can_make_request_with_history(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	_insert_row_into_history(accountService.conn, 1)

	fixture_primary_user.roles = [UserRoleDef.SONG_REQUEST.modded_value(60)]
	global currentTestDate
	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=25,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 2700

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			second=1,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

def _insert_row_into_queue(conn: Connection, userPk: int):
	queuedTimestamp = \
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=10,
			tzinfo=timezone.utc
		).timestamp()
	queueParams = [{
			"stationFk": 1,
			"songFk": 15,
			"queuedTimestamp": queuedTimestamp,
			"requestedTimestamp": queuedTimestamp,
			"requestedByUserFk": userPk
		}
	]
	stmt = insert(station_queue)
	conn.execute(stmt, queueParams) #pyright: ignore [reportUnknownMemberType]

def test_when_can_make_request_with_queue(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	_insert_row_into_queue(accountService.conn, 1)

	fixture_primary_user.roles = [f"{UserRoleDef.SONG_REQUEST.value}60"]
	global currentTestDate
	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=25,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 2700

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			second=1,
			tzinfo=timezone.utc
		)
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

def test_when_song_can_be_added_without_role(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == -1

def test_when_song_can_be_added_with_admin(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	fixture_primary_user.roles = [UserRoleDef.ADMIN.value]
	result = accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

def test_unique_roles():
	with pytest.raises(StopIteration):
		gen = UserRoleDef.remove_repeat_roles([])
		next(gen)
	testRoles1 = [UserRoleDef.SONG_REQUEST.value]
	gen = UserRoleDef.remove_repeat_roles(testRoles1)
	result = next(gen)
	assert result == UserRoleDef.SONG_REQUEST.value
	with pytest.raises(StopIteration):
		next(gen)
	testRoles2 = [
		UserRoleDef.SONG_REQUEST.modded_value(5),
		UserRoleDef.SONG_REQUEST.modded_value("15")
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles2)
	results = list(gen)
	assert len(results) == 1
	assert results[0] == f"{UserRoleDef.SONG_REQUEST.value}5"
	testRoles3 = [
		f"{UserRoleDef.SONG_REQUEST.value}",
		f"{UserRoleDef.SONG_REQUEST.value}15"
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles3)
	results = list(gen)
	assert len(results) == 1
	assert results[0] == UserRoleDef.SONG_REQUEST.modded_value()
	testRoles4 = [
		f"{UserRoleDef.SONG_REQUEST.value}",
		f"{UserRoleDef.SONG_REQUEST.value}15",
		f"{UserRoleDef.SONG_ADD.value}60",
		f"{UserRoleDef.SONG_ADD.value}15",
		f"{UserRoleDef.USER_LIST.value}"
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles4)
	results = sorted(list(gen))
	assert len(results) == 3
	assert results[0] == UserRoleDef.SONG_ADD.modded_value("15")
	assert results[1] == UserRoleDef.SONG_REQUEST.modded_value()
	assert results[2] == UserRoleDef.USER_LIST.modded_value("")


def test_count_repeat_roles():
	testRoles = [
		UserRoleDef.SONG_REQUEST.value,
		UserRoleDef.SONG_REQUEST.modded_value("15"),
		UserRoleDef.SONG_ADD.modded_value(60),
		UserRoleDef.SONG_ADD.modded_value(15),
		UserRoleDef.USER_LIST.modded_value()
	]
	result = UserRoleDef.count_repeat_roles(testRoles)
	assert len(result.items()) == 3
	assert result[UserRoleDef.SONG_REQUEST.value] == 2
	assert result[UserRoleDef.SONG_ADD.value] == 2
	assert result[UserRoleDef.USER_LIST.value] == 1

def test_create_account(
	fixture_account_service_mock_current_time: AccountsService,
):
	accountService = fixture_account_service_mock_current_time
	accountInfo = AccountCreationInfo(
		username="testUser",
		email="testPerson@gmail.com",
		password="hello12",
		displayName="Testeroni"
	)
	result = accountService.create_account(accountInfo)
	assert result
	assert len(result.roles) == 1