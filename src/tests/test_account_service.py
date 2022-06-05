#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
import pytest
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from datetime import datetime, timezone
from musical_chairs_libs.tables import stations_history, station_queue
from musical_chairs_libs.accounts_service import AccountsService,\
	UserRoleDef
from musical_chairs_libs.dtos import AccountInfo
from .constant_fixtures_for_test import test_password as test_password,\
	primary_user as primary_user,\
	test_date_ordered_list as test_date_ordered_list
from .common_fixtures import \
	db_conn as db_conn, \
	db_conn_in_mem_full as db_conn_in_mem_full, \
	account_service_in_mem as account_service_in_mem

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
def account_service_mock_current_time(account_service_in_mem: AccountsService):
	def _get_test_datetime() -> datetime:
		return currentTestDate
	account_service_in_mem.get_datetime = _get_test_datetime
	return account_service_in_mem

def test_when_can_make_request_with_history(
	account_service_mock_current_time: AccountsService,
	primary_user: AccountInfo
):
	accountService = account_service_mock_current_time
	_insert_row_into_history(accountService.conn, 1)

	primary_user.roles = [f"{UserRoleDef.SONG_REQUEST.value}60"]
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
	result = accountService.time_til_user_can_make_request(primary_user)
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
	result = accountService.time_til_user_can_make_request(primary_user)
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
	result = accountService.time_til_user_can_make_request(primary_user)
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
	account_service_mock_current_time: AccountsService,
	primary_user: AccountInfo
):
	accountService = account_service_mock_current_time
	_insert_row_into_queue(accountService.conn, 1)

	primary_user.roles = [f"{UserRoleDef.SONG_REQUEST.value}60"]
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
	result = accountService.time_til_user_can_make_request(primary_user)
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
	result = accountService.time_til_user_can_make_request(primary_user)
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
	result = accountService.time_til_user_can_make_request(primary_user)
	assert result == 0

def test_when_song_can_be_added_without_role(
	account_service_mock_current_time: AccountsService,
	primary_user: AccountInfo
):
	accountService = account_service_mock_current_time
	result = accountService.time_til_user_can_make_request(primary_user)
	assert result == -1

def test_when_song_can_be_added_with_admin(
	account_service_mock_current_time: AccountsService,
	primary_user: AccountInfo
):
	accountService = account_service_mock_current_time
	primary_user.roles = [UserRoleDef.ADMIN.value]
	result = accountService.time_til_user_can_make_request(primary_user)
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
		f"{UserRoleDef.SONG_REQUEST.value}5",
		f"{UserRoleDef.SONG_REQUEST.value}15"
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
	assert results[0] == f"{UserRoleDef.SONG_REQUEST.value}"
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
	assert results[0] == f"{UserRoleDef.SONG_ADD.value}15"
	assert results[1] == f"{UserRoleDef.SONG_REQUEST.value}"
	assert results[2] == f"{UserRoleDef.USER_LIST.value}"


def test_count_repeat_roles():
	testRoles = [
		f"{UserRoleDef.SONG_REQUEST.value}",
		f"{UserRoleDef.SONG_REQUEST.value}15",
		f"{UserRoleDef.SONG_ADD.value}60",
		f"{UserRoleDef.SONG_ADD.value}15",
		f"{UserRoleDef.USER_LIST.value}"
	]
	result = UserRoleDef.count_repeat_roles(testRoles)
	assert len(result.items()) == 3
	assert result[UserRoleDef.SONG_REQUEST.value] == 2
	assert result[UserRoleDef.SONG_ADD.value] == 2
	assert result[UserRoleDef.USER_LIST.value] == 1