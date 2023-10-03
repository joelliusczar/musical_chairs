#pyright: reportUnknownMemberType=false
from sqlalchemy import select, func
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import songs
from .constant_fixtures_for_test import *
from .common_fixtures import *
from .mocks.special_strings_reference import chinese1


sg = songs.columns

def test_iron_str(fixture_db_conn_in_mem: Connection):
	conn = fixture_db_conn_in_mem
	sg_name = sg.name
	sg_pk = sg.pk
	query = select(sg_name,\
		func.format_name_for_search(sg_name).label("ironedStr")
	).where(sg_pk == 50)
	record = conn.execute(query).fetchone()
	if record:
		assert record.name == chinese1
		assert record.ironedStr == "mu hei jiang si"
	else:
		assert False
