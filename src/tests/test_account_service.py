#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
import pytest
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from datetime import datetime, timezone
from musical_chairs_libs.tables import station_queue
from musical_chairs_libs.services import AccountsService
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	ActionRule
)
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
	historyParams: list[dict[str, Any]] = [{
			"stationfk": 1,
			"songfk": 15,
			"playedtimestamp": datetime(
				year=2022,
				month=5,
				day=27,
				hour=19,
				minute=20,
				tzinfo=timezone.utc
			).timestamp(),
			"queuedtimestamp": queuedTimestamp,
			"requestedbyuserfk": userPk
		}
	]
	stmt = insert(station_queue)
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
	queueParams: list[dict[str, Any]] = [{
			"stationfk": 1,
			"songfk": 15,
			"queuedtimestamp": queuedTimestamp,
			"requestedtimestamp": queuedTimestamp,
			"requestedbyuserfk": userPk
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

	testRoles1 = [ActionRule(name=UserRoleDef.STATION_REQUEST.value)]
	gen = ActionRule.filter_out_repeat_roles(testRoles1)
	result = next(gen)
	assert result.name == UserRoleDef.STATION_REQUEST.value
	with pytest.raises(StopIteration):
		next(gen)
	testRoles2 = ActionRule.sorted([
		ActionRule(name=UserRoleDef.STATION_REQUEST.value, span=5, count=1),
		ActionRule(name=UserRoleDef.STATION_REQUEST.value, span=15, count=1)
	])
	gen = ActionRule.filter_out_repeat_roles(testRoles2)
	results = list(gen)
	assert len(results) == 1
	assert results[0].name == UserRoleDef.STATION_REQUEST.value
	assert results[0].span == 15
	testRoles3 = ActionRule.sorted([
		ActionRule(name=UserRoleDef.STATION_REQUEST.value),
		ActionRule(name=UserRoleDef.STATION_REQUEST.value, span=15, count=1)
	])
	gen = ActionRule.filter_out_repeat_roles(testRoles3)
	results = list(gen)
	assert len(results) == 1
	assert results[0].name == UserRoleDef.STATION_REQUEST.value
	assert results[0].span == 15
	testRoles4 = ActionRule.sorted([
		ActionRule(name=UserRoleDef.STATION_REQUEST.value),
		ActionRule(name=UserRoleDef.STATION_REQUEST.value, span=15, count=1),
		ActionRule(name=UserRoleDef.SONG_EDIT.value, span=60, count=1),
		ActionRule(name=UserRoleDef.SONG_EDIT.value, span=15, count=1),
		ActionRule(name=UserRoleDef.USER_LIST.value)
	])
	gen = ActionRule.filter_out_repeat_roles(testRoles4)
	results = list(gen)
	assert len(results) == 3
	assert results[2].name == UserRoleDef.USER_LIST.value
	assert results[0].name == UserRoleDef.SONG_EDIT.value
	assert results[0].span == 60
	assert results[1].name == UserRoleDef.STATION_REQUEST.value
	assert results[1].span == 15

@pytest.mark.echo(False)
def test_save_roles(
	fixture_account_service_mock_current_time: AccountsService
):
	accountService = fixture_account_service_mock_current_time
	accountInfo = accountService.get_account_for_edit(6)
	assert accountInfo and len(accountInfo.roles) == 3
	assert accountInfo and accountInfo.roles[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert accountInfo and accountInfo.roles[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert accountInfo and accountInfo.roles[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)


	result = sorted(accountService.save_roles(6, accountInfo.roles))
	assert len(result) == 3
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert accountInfo and accountInfo.roles[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert result[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	fetched = sorted(accountService.__get_roles__(6))
	assert len(fetched) == 3
	assert fetched[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert fetched[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)


	nextSet = [*result, ActionRule(name=UserRoleDef.USER_LIST.value)]
	result = list(sorted(accountService.save_roles(6, nextSet)))
	assert len(result) == 4
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert result[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert result[3] == ActionRule(name=UserRoleDef.USER_LIST.value)
	fetched = sorted(accountService.__get_roles__(6))
	assert len(fetched) == 4
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert result[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert result[3] == ActionRule(name=UserRoleDef.USER_LIST.value)


	nextSet = [*result, ActionRule(name=UserRoleDef.USER_LIST.value)]
	result = sorted(accountService.save_roles(6, nextSet))
	assert len(result) == 4
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert result[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert result[3] == ActionRule(name=UserRoleDef.USER_LIST.value)
	fetched = sorted(accountService.__get_roles__(6))
	assert len(fetched) == 4
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(
		name=UserRoleDef.PATH_VIEW.value
	)
	assert result[2] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert result[3] == ActionRule(name=UserRoleDef.USER_LIST.value)


	nextSet = [
		ActionRule(name=UserRoleDef.STATION_REQUEST.value, span=15),
		ActionRule(name=UserRoleDef.USER_LIST.value)
	]
	result = sorted(accountService.save_roles(6, nextSet))
	assert len(result) == 2
	assert result[0] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert result[1] == ActionRule(name=UserRoleDef.USER_LIST.value)
	fetched = sorted(accountService.__get_roles__(6))
	assert len(fetched) == 2
	assert fetched[0] == ActionRule(
		name=UserRoleDef.STATION_REQUEST.value, span=15
	)
	assert fetched[1] == ActionRule(name=UserRoleDef.USER_LIST.value)


	nextSet = [
		ActionRule(name=UserRoleDef.USER_LIST.value),
		ActionRule(name=UserRoleDef.PATH_EDIT.value,span=120)
	]
	result = sorted(accountService.save_roles(6, nextSet))
	assert len(result) == 2
	assert result[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert result[1] == ActionRule(name=UserRoleDef.USER_LIST.value)
	fetched = sorted(accountService.__get_roles__(6))
	assert len(fetched) == 2
	assert fetched[0] == ActionRule(
		name=UserRoleDef.PATH_EDIT.value,span=120
	)
	assert fetched[1] == ActionRule(name=UserRoleDef.USER_LIST.value)

@pytest.mark.skip("TODO") #pyright: ignore [reportUntypedFunctionDecorator, reportGeneralTypeIssues]
def test_get_ambiguous_key(
	fixture_account_service_mock_current_time: AccountsService
):
	pass
	# accountService = fixture_account_service_mock_current_time
	# accountInfo = accountService.get_account_for_edit("7")
	# assert accountInfo
	# assert accountInfo.displayname == "seven"

def test_user_search(
	fixture_account_service_mock_current_time: AccountsService
):
	accountService = fixture_account_service_mock_current_time
	res = sorted(
		accountService.get_account_list("a"),
		key=lambda a: a.id
	)
	assert len(res) == 1
	assert res[0].displayname == "Alice is my name"
	res = sorted(
		accountService.get_account_list("f"),
		key=lambda a: a.id
	)
	assert len(res) == 3#4
	#assert res[0].displayname == "\uFB00 ozotroz"
	assert res[0].displayname == "Felix the man"
	assert res[1].displayname == None
	assert res[2].displayname == "Foxtrain chu"

	res = sorted(
		accountService.get_account_list("fo"),
		key=lambda a: a.id
	)
	assert len(res) == 2
	assert res[0].displayname == None
	assert res[1].displayname == "Foxtrain chu"

	res = sorted(
		accountService.get_account_list("fox"),
		key=lambda a: a.id
	)
	assert len(res) == 2
	assert res[0].displayname == None
	assert res[1].displayname == "Foxtrain chu"

	res = sorted(
		accountService.get_account_list("foxt"),
		key=lambda a: a.id
	)
	assert len(res) == 1
	assert res[0].displayname == "Foxtrain chu"

	res = sorted(
		accountService.get_account_list("n"),
		key=lambda a: a.id
	)
	assert len(res) == 3
	assert res[0].displayname == "\u006E\u0303ovoper"
	assert res[1].displayname == "Ned Land of the Spear"
	assert res[2].displayname == "Narloni"
