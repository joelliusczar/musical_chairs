#pyright: reportUnknownMemberType=false
from typing import cast
from sqlalchemy import select, func
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from musical_chairs_libs.tables import songs
from .constant_fixtures_for_test import *
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem
from .common_fixtures import *
from .mocks.special_strings_reference import chinese1


sg = cast(ColumnCollection,songs.columns) #pyright: ignore [reportUnknownMemberType]

def test_iron_str(fixture_populated_db_conn_in_mem: Connection):
	conn = fixture_populated_db_conn_in_mem
	sg_name = sg.name #pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]
	sg_pk = sg.pk #pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]
	query = select(sg_name,\
		func.format_name_for_search(sg_name).label("ironedStr")
	).where(sg_pk == 50)
	record = conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
	if record:
		assert record.name == chinese1 #pyright: ignore [reportGeneralTypeIssues]
		assert record.ironedStr == "mu hei jiang si" #pyright: ignore [reportGeneralTypeIssues]
	else:
		assert False
