#pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false
#pyright: reportMissingTypeStubs=false
import pytest
import sqlite3
from typing import Callable, Any
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_setup_db as fixture_setup_db,
	fixture_conn_cardboarddb as fixture_conn_cardboarddb,
	fixture_db_queryer as fixture_db_queryer,
	fixture_datetime_iterator as fixture_datetime_iterator,
	fixture_sqlite_conn as fixture_sqlite_conn
)
from musical_chairs_libs.services import DbOwnerConnectionService
from sqlalchemy.engine import Connection
from .mocks.db_data import (
	album_params,
	artist_params,
	get_path_permission_params,
	get_station_permission_params,
	get_user_params,
	get_user_role_params,
	song_params
)
from .mocks import db_population
from .mocks import db_data
from .mocks.mock_datetime_provider import MockDatetimeProvider
from .constant_fixtures_for_test import (
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
)

@pytest.fixture
def fixture_db_populate_factory(
	request: pytest.FixtureRequest,
	fixture_setup_db: str,
	fixture_datetime_iterator: MockDatetimeProvider,
	fixture_primary_user: AccountInfo,
	fixture_mock_password: bytes
) -> Callable[[], None]:
	def populate_fn():
		dbName = fixture_setup_db
		with DbOwnerConnectionService(dbName) as ownerConnService:
			conn = ownerConnService.conn
			db_data.populate_users(
				conn,
				fixture_datetime_iterator,
				fixture_primary_user,
				fixture_mock_password
			)
			db_population.populate_artists(conn)
			conn.commit()
	return populate_fn


def test_data_view(
	fixture_datetime_iterator: MockDatetimeProvider,
	fixture_primary_user: AccountInfo,
	fixture_mock_password: bytes
):
	# this test exists as a convience to run queires on
	# the test data
	noop: Callable[[Any], Any] = lambda x: None
	noop(song_params)
	noop(artist_params)
	noop(album_params)
	users = get_user_params(
		fixture_datetime_iterator,
		fixture_primary_user,
		fixture_mock_password
	)
	noop(users)
	userRoles = get_user_role_params(
		fixture_datetime_iterator,
		fixture_primary_user
	)
	noop(userRoles)
	stationRules = get_station_permission_params(fixture_datetime_iterator)
	noop(stationRules)
	pathRules = get_path_permission_params(fixture_datetime_iterator)
	noop(pathRules)
	pass


def test_data_in_db(
	fixture_conn_cardboarddb: Connection,
	fixture_db_queryer: Callable[[str], None]):
	# this test exists as a convience to run sql queires on
	# the test data
	# print(query.compile(compile_kwargs={"literal_binds": True}))
	pass


def test_sqlite_version():
	print(sqlite3.sqlite_version_info)
	# print(dir(alco))