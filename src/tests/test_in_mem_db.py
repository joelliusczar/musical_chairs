#pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false
#pyright: reportMissingTypeStubs=false
import pytest
from typing import cast, Callable
from sqlalchemy import select
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_setup_in_mem_tbls as fixture_setup_in_mem_tbls, \
	fixture_db_conn_in_mem as fixture_db_conn_in_mem
from musical_chairs_libs.tables import artists
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from .mocks.db_data import *
from .constant_fixtures_for_test import (
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
)

@pytest.mark.usefixtures("fixture_setup_in_mem_tbls")
def test_in_mem_db(fixture_db_conn_in_mem: Connection) -> None:
	a = cast(ColumnCollection, artists.columns)
	query = select(artists).order_by(a.name)
	res = fixture_db_conn_in_mem.execute(query).fetchall()
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
	fixture_mock_ordered_date_list: List[datetime],
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
		fixture_mock_ordered_date_list,
		fixture_primary_user,
		fixture_mock_password
	)
	noop(users)
	userRoles = get_user_role_params(
		fixture_mock_ordered_date_list,
		fixture_primary_user
	)
	noop(userRoles)
	stationRules = get_station_permission_params(fixture_mock_ordered_date_list)
	noop(stationRules)
	pathRules = get_path_permission_params(fixture_mock_ordered_date_list)
	noop(pathRules)
	pass