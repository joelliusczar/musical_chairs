#pyright: reportMissingTypeStubs=false
import pytest
from typing import Iterator, List, Protocol
from datetime import datetime
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.queue_service import QueueService
from musical_chairs_libs.accounts_service import AccountsService
from musical_chairs_libs.radio_handle import RadioHandle
from musical_chairs_libs.dtos import AccountInfo
from sqlalchemy.engine import Connection
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.tables import metadata
from .mocks.mock_process_manager import MockOSProcessManager
from .db_population import populate_artists,\
	populate_albums,\
	populate_songs,\
	populate_songs_artists,\
	populate_tags,\
	populate_songs_tags,\
	populate_stations,\
	populate_station_tags,\
	populate_users
from .constant_fixtures_for_test import test_password as test_password,\
	primary_user as primary_user,\
	test_date_ordered_list as test_date_ordered_list


class ConnectionConstructor(Protocol):
	def __call__(self, echo: bool=False, inMemory: bool=False) -> Connection:
			...

@pytest.fixture
def db_conn() -> Connection:
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
	return conn

@pytest.fixture
def db_conn_in_mem() -> Iterator[Connection]:
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection(inMemory=True)
	try:
		yield conn
	finally:
		conn.close()

@pytest.fixture
def db_conn_in_mem_full(
	test_date_ordered_list: List[datetime],
	primary_user: AccountInfo,
	test_password: bytes,
	request: pytest.FixtureRequest
) -> Iterator[Connection]:
	requestEcho = request.node.get_closest_marker("echo")
	if requestEcho is None:
		echo = False
	else:
		echo = requestEcho.args[0]
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection(inMemory=True, echo=echo)
	_setup_in_mem_tbls_full(
		conn,
		test_date_ordered_list,
		primary_user,
		test_password
	)
	try:
		yield conn
	finally:
		conn.close()

def construct_mock_connection_constructor(
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
) -> ConnectionConstructor:

	def get_mock_db_connection_constructor(
		echo: bool=False,
		inMemory: bool=False
	) -> Connection:
		envMgr = EnvManager()
		inMemory = True
		conn = envMgr.get_configured_db_connection(echo=echo, inMemory=inMemory)
		_setup_in_mem_tbls_full(
			conn,
			orderedTestDates,
			primaryUser,
			testPassword
		)
		return conn
	return get_mock_db_connection_constructor

@pytest.fixture
def env_manager_with_in_mem_db(
	test_date_ordered_list: List[datetime],
	primary_user: AccountInfo,
	test_password: bytes
) -> EnvManager:
	envMgr = EnvManager()
	envMgr.get_configured_db_connection = \
		construct_mock_connection_constructor(
			test_date_ordered_list,
			primary_user,
			test_password
		)
	return envMgr

@pytest.fixture
def radio_handle_in_mem(env_manager_with_in_mem_db: EnvManager) -> RadioHandle:
	envMgr = env_manager_with_in_mem_db
	processManager = MockOSProcessManager(1)
	radioHandle = RadioHandle(
		"oscar_station",
		envManager=envMgr,
		processManager=processManager
	)
	return radioHandle

@pytest.fixture
def radio_handle() -> RadioHandle:
	radioHandle = RadioHandle("vg", processManager=MockOSProcessManager(1))
	return radioHandle

@pytest.fixture
def queue_service_in_mem(db_conn_in_mem_full: Connection) -> QueueService:
	queueService = QueueService(db_conn_in_mem_full)
	return queueService

@pytest.fixture
def account_service_in_mem(db_conn_in_mem_full: Connection) -> AccountsService:
	accountService = AccountsService(db_conn_in_mem_full)
	return accountService

@pytest.fixture
def station_service_in_mem(db_conn_in_mem_full: Connection) -> StationService:
	stationService = StationService(db_conn_in_mem_full)
	return stationService

@pytest.fixture
def setup_in_mem_tbls_full(
	db_conn_in_mem: Connection,
	test_date_ordered_list: List[datetime],
	primary_user: AccountInfo,
	test_password: bytes
) -> None:
	_setup_in_mem_tbls_full(
		db_conn_in_mem,
		test_date_ordered_list,
		primary_user,
		test_password
	)

def _setup_in_mem_tbls_full(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
) -> None:
	metadata.create_all(conn.engine)
	populate_artists(conn)
	populate_albums(conn)
	populate_songs(conn)
	populate_songs_artists(conn)
	populate_tags(conn)
	populate_songs_tags(conn)
	populate_stations(conn)
	populate_station_tags(conn)
	populate_users(conn, orderedTestDates, primaryUser, testPassword)


if __name__ == "__main__":
	print(test_date_ordered_list)
	pass