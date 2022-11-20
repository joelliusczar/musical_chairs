#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
import pytest
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from datetime import datetime, timezone
from musical_chairs_libs.tables import stations_history, station_queue
from musical_chairs_libs.services import AccountsService
from musical_chairs_libs.dtos_and_utilities import AccountInfo,\
	AccountCreationInfo,\
	UserRoleDef
from .constant_fixtures_for_test import\
	fixture_primary_user as fixture_primary_user
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_account_service as fixture_account_service
from .common_fixtures import *

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

@pytest.mark.skip("TODO") #pyright: ignore [reportUntypedFunctionDecorator, reportGeneralTypeIssues]
def test_when_can_make_request_with_history(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	_insert_row_into_history(accountService.conn, 1)

	#fixture_primary_user.roles = [UserRoleDef.STATION_REQUEST.modded_value(60)]
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
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

@pytest.mark.skip("TODO") #pyright: ignore [reportUntypedFunctionDecorator, reportGeneralTypeIssues]
def test_when_can_make_request_with_queue(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	accountService = fixture_account_service_mock_current_time
	_insert_row_into_queue(accountService.conn, 1)

	#fixture_primary_user.roles = [f"{UserRoleDef.STATION_REQUEST.value}60"]
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
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
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

@pytest.mark.skip("TODO") #pyright: ignore [reportUntypedFunctionDecorator, reportGeneralTypeIssues]
def test_when_song_can_be_added_without_role(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	#accountService = fixture_account_service_mock_current_time
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == -1

@pytest.mark.skip("TODO") #pyright: ignore [reportUntypedFunctionDecorator, reportGeneralTypeIssues]
def test_when_song_can_be_added_with_admin(
	fixture_account_service_mock_current_time: AccountsService,
	fixture_primary_user: AccountInfo
):
	#accountService = fixture_account_service_mock_current_time
	#fixture_primary_user.roles = [UserRoleDef.ADMIN.value]
	result = None#accountService.time_til_user_can_make_request(fixture_primary_user)
	assert result == 0

def test_unique_roles():
	with pytest.raises(StopIteration):
		gen = UserRoleDef.remove_repeat_roles([])
		next(gen)
	testRoles1 = [UserRoleDef.STATION_REQUEST.value]
	gen = UserRoleDef.remove_repeat_roles(testRoles1)
	result = next(gen)
	assert result == UserRoleDef.STATION_REQUEST.value
	with pytest.raises(StopIteration):
		next(gen)
	testRoles2 = [
		UserRoleDef.STATION_REQUEST.modded_value(5),
		UserRoleDef.STATION_REQUEST.modded_value("15")
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles2)
	results = list(gen)
	assert len(results) == 1
	assert results[0] == f"{UserRoleDef.STATION_REQUEST.value}5"
	testRoles3 = [
		f"{UserRoleDef.STATION_REQUEST.value}",
		f"{UserRoleDef.STATION_REQUEST.value}15"
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles3)
	results = list(gen)
	assert len(results) == 1
	assert results[0] == UserRoleDef.STATION_REQUEST.modded_value()
	testRoles4 = [
		f"{UserRoleDef.STATION_REQUEST.value}",
		f"{UserRoleDef.STATION_REQUEST.value}15",
		f"{UserRoleDef.SONG_EDIT.value}60",
		f"{UserRoleDef.SONG_EDIT.value}15",
		f"{UserRoleDef.USER_LIST.value}"
	]
	gen = UserRoleDef.remove_repeat_roles(testRoles4)
	results = sorted(list(gen))
	assert len(results) == 3
	assert results[0] == UserRoleDef.SONG_EDIT.modded_value("15")
	assert results[1] == UserRoleDef.STATION_REQUEST.modded_value()
	assert results[2] == UserRoleDef.USER_LIST.modded_value("")


def test_count_repeat_roles():
	testRoles = [
		UserRoleDef.STATION_REQUEST.value,
		UserRoleDef.STATION_REQUEST.modded_value("15"),
		UserRoleDef.SONG_EDIT.modded_value(60),
		UserRoleDef.SONG_EDIT.modded_value(15),
		UserRoleDef.USER_LIST.modded_value()
	]
	result = UserRoleDef.count_repeat_roles(testRoles)
	assert len(result.items()) == 3
	assert result[UserRoleDef.STATION_REQUEST.value] == 2
	assert result[UserRoleDef.SONG_EDIT.value] == 2
	assert result[UserRoleDef.USER_LIST.value] == 1

def test_create_account(
	fixture_account_service_mock_current_time: AccountsService
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

@pytest.mark.echo(True)
def test_save_roles(
	fixture_account_service_mock_current_time: AccountsService
):
	accountService = fixture_account_service_mock_current_time
	accountInfo = accountService.get_account_for_edit(6)
	assert accountInfo and len(accountInfo.roles) == 2
	assert accountInfo and accountInfo.roles[0] == "song:edit:120"
	assert accountInfo and accountInfo.roles[1] == "station:request:15"


	result = list(sorted(accountService.save_roles(6, accountInfo.roles)))
	assert len(result) == 2
	assert result[0] == "song:edit:120"
	assert result[1] == "station:request:15"
	fetched = list(sorted((r.role for r in accountService._get_roles(6))))
	assert len(fetched) == 2
	assert fetched[0] == "song:edit:120"
	assert fetched[1] == "station:request:15"


	nextSet = [*result, UserRoleDef.USER_LIST.value]
	result = list(sorted(accountService.save_roles(6, nextSet)))
	assert len(result) == 3
	assert result[0] == "song:edit:120"
	assert result[1] == "station:request:15"
	assert result[2] == "user:list:"
	fetched = list(sorted((r.role for r in accountService._get_roles(6))))
	assert len(fetched) == 3
	assert fetched[0] == "song:edit:120"
	assert fetched[1] == "station:request:15"
	assert fetched[2] == "user:list:"


	nextSet = [*result, UserRoleDef.USER_LIST.value]
	result = list(sorted(accountService.save_roles(6, nextSet)))
	assert len(result) == 3
	assert result[0] == "song:edit:120"
	assert result[1] == "station:request:15"
	assert result[2] == "user:list:"
	fetched = list(sorted((r.role for r in accountService._get_roles(6))))
	assert len(fetched) == 3
	assert fetched[0] == "song:edit:120"
	assert fetched[1] == "station:request:15"
	assert fetched[2] == "user:list:"


	nextSet = ["station:request:15", "user:list:"]
	result = list(sorted(accountService.save_roles(6, nextSet)))
	assert len(result) == 2
	assert result[0] == "station:request:15"
	assert result[1] == "user:list:"
	fetched = list(sorted((r.role for r in accountService._get_roles(6))))
	assert len(fetched) == 2
	assert fetched[0] == "station:request:15"
	assert fetched[1] == "user:list:"


	nextSet = ["user:list:", "song:edit:120"]
	result = list(sorted(accountService.save_roles(6, nextSet)))
	assert len(result) == 2
	assert result[0] == "song:edit:120"
	assert result[1] == "user:list:"
	fetched = list(sorted((r.role for r in accountService._get_roles(6))))
	assert len(fetched) == 2
	assert fetched[0] == "song:edit:120"
	assert fetched[1] == "user:list:"