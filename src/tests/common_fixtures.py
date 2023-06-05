#pyright: reportMissingTypeStubs=false
import pytest
import os
from typing import Iterator, List, Optional, Any, Callable
from datetime import datetime
from musical_chairs_libs.services import (
	EnvManager,
	QueueService,
	AccountsService,
	SongInfoService,
	StationService,
	TemplateService
)
from musical_chairs_libs.radio_handle import RadioHandle
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	ActionRule,
	get_path_owner_roles,
	normalize_opening_slash
)
from sqlalchemy.engine import Connection
from .mocks.mock_db_constructors import (
	MockDbPopulateClosure,
	setup_in_mem_tbls,
	construct_mock_connection_constructor
)
from .mocks.mock_datetime_provider import MockDatetimeProvider
from .constant_fixtures_for_test import (
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
)
from itertools import chain
from dataclasses import asdict

@pytest.fixture
def fixture_db_conn_in_mem(
	request: pytest.FixtureRequest
) -> Iterator[Connection]:
	requestEcho = request.node.get_closest_marker("echo")
	if requestEcho is None:
		echo = False
	else:
		echo = requestEcho.args[0]
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection(inMemory=True, echo=echo)
	try:
		yield conn
	finally:
		conn.close()

@pytest.fixture
def fixture_db_populate_factory(
	fixture_mock_ordered_date_list: List[datetime],
	fixture_primary_user: AccountInfo,
	fixture_mock_password: bytes
) -> MockDbPopulateClosure:
	def _setup_tables(
		conn: Connection,
		request: Optional[pytest.FixtureRequest]=None
	):
		setup_in_mem_tbls(
			conn,
			request,
			fixture_mock_ordered_date_list,
			fixture_primary_user,
			fixture_mock_password,
		)
	return _setup_tables


@pytest.fixture
def fixture_populated_db_conn_in_mem(
	fixture_db_populate_factory: MockDbPopulateClosure,
	fixture_db_conn_in_mem: Connection,
	request: pytest.FixtureRequest
) -> Connection:
	fixture_db_populate_factory(fixture_db_conn_in_mem, request)
	return fixture_db_conn_in_mem


@pytest.fixture
def fixture_env_manager_with_in_mem_db(
	fixture_db_populate_factory: MockDbPopulateClosure,
	request: pytest.FixtureRequest
) -> EnvManager:
	envMgr = EnvManager()
	envMgr.get_configured_db_connection = \
		construct_mock_connection_constructor(fixture_db_populate_factory, request)
	return envMgr

@pytest.fixture
def fixture_radio_handle(
	fixture_env_manager_with_in_mem_db: EnvManager
) -> RadioHandle:
	envMgr = fixture_env_manager_with_in_mem_db
	radioHandle = RadioHandle(
		1,
		envManager=envMgr
	)
	return radioHandle


@pytest.fixture
def fixture_queue_service(
	fixture_populated_db_conn_in_mem: Connection
) -> QueueService:
	queueService = QueueService(fixture_populated_db_conn_in_mem)
	return queueService

@pytest.fixture
def fixture_account_service(
	fixture_populated_db_conn_in_mem: Connection) -> AccountsService:
	accountService = AccountsService(fixture_populated_db_conn_in_mem)
	return accountService

@pytest.fixture
def fixture_station_service(
	fixture_populated_db_conn_in_mem: Connection
) -> StationService:
	stationService = StationService(fixture_populated_db_conn_in_mem)
	return stationService

@pytest.fixture
def fixture_song_info_service(
	fixture_populated_db_conn_in_mem: Connection
) -> SongInfoService:
	songInfoService = SongInfoService(fixture_populated_db_conn_in_mem)
	return songInfoService

@pytest.fixture
def fixture_template_service() -> TemplateService:
	templateService = TemplateService()
	return templateService

@pytest.fixture
def fixture_setup_in_mem_tbls(
	fixture_db_conn_in_mem: Connection,
	fixture_mock_ordered_date_list: List[datetime],
	fixture_primary_user: AccountInfo,
	fixture_mock_password: bytes,
	request: pytest.FixtureRequest
) -> None:
	setup_in_mem_tbls(
		fixture_db_conn_in_mem,
		request,
		fixture_mock_ordered_date_list,
		fixture_primary_user,
		fixture_mock_password,
	)


@pytest.fixture
def fixture_clean_station_folders():
	yield
	for file in os.scandir(EnvManager.station_config_dir):
		os.remove(file.path)
	for file in os.scandir(EnvManager.station_module_dir):
		os.remove(file.path)


@pytest.fixture
def fixture_datetime_iterator(
	fixture_mock_ordered_date_list: List[datetime],
	request: pytest.FixtureRequest
) -> MockDatetimeProvider:
	requestTimestamps = request.node.get_closest_marker("testDatetimes")
	if requestTimestamps:
		datetimes = requestTimestamps.args[0]
		provider = MockDatetimeProvider(datetimes)
		return provider
	provider = MockDatetimeProvider(fixture_mock_ordered_date_list)
	return provider

@pytest.fixture
def fixture_path_user_factory(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
) -> Callable[[str], AccountInfo]:

	def path_user(username: str) -> AccountInfo:
		songInfoService = fixture_song_info_service
		accountService = fixture_account_service
		user,_ = accountService.get_account_for_login(username)
		assert user
		rules = ActionRule.sorted(r for r in chain(
			user.roles,
			(p for p in songInfoService.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirRoot)))
		))
		userDict = asdict(user)
		userDict["roles"] = rules
		resultUser = AccountInfo(
			**userDict,
		)
		return resultUser
	return path_user


@pytest.fixture
def datetime_monkey_patch(
	fixture_datetime_iterator: MockDatetimeProvider,
	monkeypatch: pytest.MonkeyPatch
) -> MockDatetimeProvider:

	class MockDatetimeMeta(type):

		def __instancecheck__(self, __instance: Any) -> bool:
			if type(__instance) == datetime:
				return True
			return super().__instancecheck__(__instance)

	class MockDatetime(datetime, metaclass=MockDatetimeMeta):

		@classmethod
		def now(cls, tz: Any=None) -> datetime:
			dt = fixture_datetime_iterator()
			return dt.astimezone(tz)

		@classmethod
		def utcnow(cls) -> datetime:
			return fixture_datetime_iterator()
	monkeypatch.setattr("musical_chairs_libs.dtos_and_utilities.simple_functions.datetime", MockDatetime)
	monkeypatch.setattr("jose.jwt.datetime", MockDatetime)

	return fixture_datetime_iterator


@pytest.fixture
def fixture_db_queryer(
	fixture_db_conn_in_mem: Connection
) -> Callable[[str], None]:
	def run_query(stmt: str):
		res = fixture_db_conn_in_mem.execute(stmt) #pyright: ignore [reportUnknownMemberType]
		print(res.fetchall())
	return run_query

if __name__ == "__main__":
	print(fixture_mock_ordered_date_list)
	pass