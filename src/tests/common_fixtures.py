#pyright: reportMissingTypeStubs=false
import pytest
import os
import hashlib
import subprocess
from typing import Iterator, List, Any, Callable, cast
from datetime import datetime
from musical_chairs_libs.services import (
	EnvManager,
	QueueService,
	AccountsService,
	SongInfoService,
	StationService,
	TemplateService,
	UserActionsHistoryService,
	DbRootConnectionService,
	DbOwnerConnectionService,
	SongFileService,
	PathRuleService,
	ArtistService,
	AlbumService,
	SongArtistService
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
	setup_in_mem_tbls,
)
from .mocks.mock_datetime_provider import MockDatetimeProvider
from .mocks.mock_file_service import MockFileService
from .constant_fixtures_for_test import (
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
)


@pytest.fixture
def fixture_setup_db(request: pytest.FixtureRequest) -> Iterator[str]:
	#some tests were failing because db name was too long
	testId =  hashlib.md5(request.node.name.encode("utf-8")).hexdigest()
	dbName=f"test_{testId}_musical_chairs_db"
	with DbRootConnectionService() as rootConnService:
		rootConnService.drop_database(dbName)
		rootConnService.create_db(dbName)
		rootConnService.create_owner()
		rootConnService.create_app_users()
		rootConnService.grant_owner_roles(dbName)

	with DbOwnerConnectionService(dbName) as ownerConnService:
		ownerConnService.create_tables()
		ownerConnService.add_path_permission_index()
		ownerConnService.grant_api_roles()
		ownerConnService.grant_radio_roles()
		ownerConnService.add_next_directory_level_func()
		ownerConnService.add_normalize_opening_slash()
		ownerConnService.drop_requestedtimestamp_column()
	try:
		yield dbName
	finally:
		with DbRootConnectionService() as rootConnService:
			rootConnService.drop_database(dbName)

@pytest.fixture
def fixture_db_populate_factory(
	request: pytest.FixtureRequest,
	fixture_setup_db: str,
	fixture_mock_ordered_date_list: List[datetime],
	fixture_primary_user: AccountInfo,
	fixture_mock_password: bytes
) -> Callable[[], None]:
	def populate_fn():
		dbName = fixture_setup_db
		with DbOwnerConnectionService(dbName) as ownerConnService:
			conn = ownerConnService.conn
			setup_in_mem_tbls(
				conn,
				request,
				fixture_mock_ordered_date_list,
				fixture_primary_user,
				fixture_mock_password,
			)
	return populate_fn

@pytest.fixture
def fixture_db_empty_populate_factory() -> Callable[[], None]:
	def populate_fn():
		pass
	return populate_fn


@pytest.fixture
def fixture_db_conn_in_mem(
	request: pytest.FixtureRequest,
	fixture_setup_db: str,
) -> Iterator[Connection]:
	requestEcho = request.node.get_closest_marker("echo")
	requestPopulateFnName = request.node.get_closest_marker("populateFnName")

	echo = requestEcho.args[0] if not requestEcho is None else False
	populateFnName = requestPopulateFnName.args[0] \
		if not requestPopulateFnName is None else "fixture_db_populate_factory"
	populateFn = request.getfixturevalue(populateFnName)
	populateFn()
	envManager = EnvManager()
	dbName=fixture_setup_db
	conn = envManager.get_configured_api_connection(dbName, echo=echo)
	try:
		yield conn
	finally:
		#should dispose here
		conn.close()

@pytest.fixture
def fixture_populated_db_name(
	request: pytest.FixtureRequest,
	fixture_setup_db: str
) -> str:
	request.getfixturevalue("fixture_db_conn_in_mem")
	return fixture_setup_db


@pytest.fixture
def fixture_radio_handle(fixture_populated_db_name: str) -> RadioHandle:
	radioHandle = RadioHandle(1, fixture_populated_db_name)
	return radioHandle


@pytest.fixture
def fixture_queue_service(
	fixture_db_conn_in_mem: Connection
) -> QueueService:
	queueService = QueueService(fixture_db_conn_in_mem)
	return queueService

@pytest.fixture
def fixture_account_service(
	fixture_db_conn_in_mem: Connection) -> AccountsService:
	accountService = AccountsService(fixture_db_conn_in_mem)
	return accountService

@pytest.fixture
def fixture_station_service(
	fixture_db_conn_in_mem: Connection
) -> StationService:
	stationService = StationService(fixture_db_conn_in_mem)
	return stationService

@pytest.fixture
def fixture_song_info_service(
	fixture_db_conn_in_mem: Connection
) -> SongInfoService:
	songInfoService = SongInfoService(fixture_db_conn_in_mem)
	return songInfoService

@pytest.fixture
def fixture_album_service(
	fixture_db_conn_in_mem: Connection
) -> AlbumService:
	albumService = AlbumService(fixture_db_conn_in_mem)
	return albumService

@pytest.fixture
def fixture_artist_service(
	fixture_db_conn_in_mem: Connection
) -> ArtistService:
	artistService = ArtistService(fixture_db_conn_in_mem)
	return artistService

@pytest.fixture
def fixture_songartist_service(
	fixture_db_conn_in_mem: Connection
) -> SongArtistService:
	songArtistService = SongArtistService(fixture_db_conn_in_mem)
	return songArtistService

@pytest.fixture
def fixture_path_rule_service(
	fixture_db_conn_in_mem: Connection
) -> PathRuleService:
	pathRuleService = PathRuleService(fixture_db_conn_in_mem)
	return pathRuleService

@pytest.fixture
def fixture_song_file_service(
	fixture_db_conn_in_mem: Connection
) -> SongFileService:
	fileService = MockFileService()
	songFileService = SongFileService(
		fixture_db_conn_in_mem,
		fileService
	)
	return songFileService

@pytest.fixture
def fixture_template_service() -> TemplateService:
	templateService = TemplateService()
	return templateService

@pytest.fixture
def fixture_user_actions_history_service(
	fixture_db_conn_in_mem: Connection
) -> UserActionsHistoryService:
	userActionsHistoryService = UserActionsHistoryService(
		fixture_db_conn_in_mem
	)
	return userActionsHistoryService

@pytest.fixture
def fixture_clean_station_folders():
	yield
	for file in os.scandir(EnvManager.station_config_dir()):
		os.remove(file.path)
	for file in os.scandir(EnvManager.station_module_dir()):
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
	fixture_path_rule_service: PathRuleService,
	fixture_account_service: AccountsService
) -> Callable[[str], AccountInfo]:

	def path_user(username: str) -> AccountInfo:
		pathRuleService = fixture_path_rule_service
		accountService = fixture_account_service
		user,_ = accountService.get_account_for_login(username)
		assert user
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in pathRuleService.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
		)
		userDict = user.model_dump()
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
		def now(cls, tz: Any=None) -> "MockDatetime":
			dt = fixture_datetime_iterator()
			return cast(MockDatetime,dt.astimezone(tz))

		@classmethod
		def utcnow(cls) -> "MockDatetime":
			return cast(MockDatetime,fixture_datetime_iterator())
		
	monkeypatch.setattr(
		"musical_chairs_libs.dtos_and_utilities.simple_functions.datetime",
		MockDatetime
	)
	monkeypatch.setattr("jose.jwt.datetime", MockDatetime)

	return fixture_datetime_iterator


@pytest.fixture
def fixture_db_queryer(
	fixture_db_conn_in_mem: Connection
) -> Callable[[str], None]:
	def run_query(stmt: str):
		res = fixture_db_conn_in_mem.exec_driver_sql(stmt)
		print(res.fetchall())
	return run_query

@pytest.fixture
def ices_config_monkey_patch(
	monkeypatch: pytest.MonkeyPatch
):
	icecastTemplateLocation = f"{EnvManager.templates_dir()}/icecast.xml"
	cmdOutput = "     CGroup: /system.slice/icecast2.service\n"\
		f"           └─966 /usr/bin/icecast2 -b -c {icecastTemplateLocation}"
	def mock_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
		return subprocess.CompletedProcess(
			args=[],
			returncode=0,
			stdout=cmdOutput
		)
		

	monkeypatch.setattr("subprocess.run", mock_run)
		

if __name__ == "__main__":
	print(fixture_mock_ordered_date_list)
	pass