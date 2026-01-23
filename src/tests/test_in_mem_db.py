#pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false
#pyright: reportMissingTypeStubs=false
import pytest
import sqlite3
from typing import Callable, Any
from sqlalchemy import select
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_setup_db as fixture_setup_db,
	fixture_conn_cardboarddb as fixture_conn_cardboarddb,
	fixture_db_queryer as fixture_db_queryer,
	fixture_datetime_iterator as fixture_datetime_iterator
)
from musical_chairs_libs.services import DbOwnerConnectionService
from musical_chairs_libs.tables import artists
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

@pytest.mark.populateFnName("fixture_db_populate_factory")
@pytest.mark.echo(False)
def test_in_mem_db(fixture_conn_cardboarddb: Connection) -> None:
	a = artists.columns
	query = select(artists).order_by(a.name)
	res = fixture_conn_cardboarddb.execute(query).fetchall()
	assert res[0].name == "alpha_artist"
	assert res[0].pk == 1
	assert res[1].name == "bravo_artist"
	assert res[1].pk == 2
	assert res[2].name == "charlie_artist"
	assert res[2].pk == 3
	assert res[3].name == "delta_artist"
	assert res[3].pk == 4
	assert res[4].name == "echo_artist"
	assert res[4].pk == 5
	assert res[5].name == "foxtrot_artist"
	assert res[5].pk == 6
	assert res[6].name == "golf_artist"
	assert res[6].pk == 7

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