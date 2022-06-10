#pyright: reportUnknownMemberType=false
from sqlalchemy import select, func
from sqlalchemy.engine import Connection
from sqlalchemy.sql import ColumnCollection
from musical_chairs_libs.tables import songs
from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem


sg: ColumnCollection = songs.columns #pyright: ignore [reportUnknownMemberType]

def test_iron_str(fixture_populated_db_conn_in_mem: Connection):
	conn = fixture_populated_db_conn_in_mem
	sg_name = sg.name #pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]
	sg_pk = sg.pk #pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]
	query = select(sg_name,\
		func.format_name_for_search(sg_name).label("ironedStr")
	).where(sg_pk == 50)
	record = conn.execute(query).fetchone() #pyright: ignore [reportUnknownMemberType]
	if record:
		assert record.name == "目黒将司" #pyright: ignore [reportGeneralTypeIssues]
		assert record.ironedStr == "mu hei jiang si" #pyright: ignore [reportGeneralTypeIssues]
	else:
		assert False
