#pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false
#pyright: reportMissingTypeStubs=false
import pytest
from sqlalchemy import select
from .common_fixtures import setup_in_mem_tbls as setup_in_mem_tbls, \
	db_conn_in_mem as db_conn_in_mem
from musical_chairs_libs.tables import artists
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection

@pytest.mark.usefixtures("setup_in_mem_tbls")
def test_in_mem_db(db_conn_in_mem: Connection) -> None:
	a: ColumnCollection = artists.columns
	query = select(artists).order_by(a.name)
	res = db_conn_in_mem.execute(query).fetchall()
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