#pyright: reportMissingTypeStubs=false
import pytest
from typing import Iterator, List, Optional
from datetime import datetime
from musical_chairs_libs.services import\
	EnvManager,\
	QueueService,\
	AccountsService,\
	SongInfoService,\
	StationService,\
	TagService

from musical_chairs_libs.radio_handle import RadioHandle
from musical_chairs_libs.dtos_and_utilities import AccountInfo
from sqlalchemy.engine import Connection
from .mocks.mock_process_manager import MockOSProcessManager
from .mocks.mock_db_constructors import\
	MockDbPopulator,\
	setup_in_mem_tbls,\
	construct_mock_connection_constructor

from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list



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
) -> MockDbPopulator:
	def _setup_tables(
		conn: Connection,
		request: Optional[pytest.FixtureRequest]=None
	):
		setup_in_mem_tbls(
			conn,
			fixture_mock_ordered_date_list,
			fixture_primary_user,
			fixture_mock_password,
			request
		)
	return _setup_tables

@pytest.fixture
def fixture_populated_db_conn_in_mem(
	fixture_db_populate_factory: MockDbPopulator,
	fixture_db_conn_in_mem: Connection,
	request: pytest.FixtureRequest
) -> Connection:
	fixture_db_populate_factory(fixture_db_conn_in_mem, request)
	return fixture_db_conn_in_mem


@pytest.fixture
def fixture_env_manager_with_in_mem_db(
	fixture_db_populate_factory: MockDbPopulator,
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
	processManager = MockOSProcessManager(1)
	radioHandle = RadioHandle(
		"oscar_station",
		envManager=envMgr,
		processManager=processManager
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
def fixture_tag_service(
	fixture_populated_db_conn_in_mem: Connection
) -> TagService:
	tagService = TagService(fixture_populated_db_conn_in_mem)
	return tagService

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
		fixture_mock_ordered_date_list,
		fixture_primary_user,
		fixture_mock_password,
		request
	)




if __name__ == "__main__":
	print(fixture_mock_ordered_date_list)
	pass