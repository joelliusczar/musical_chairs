#pyright: reportUnknownMemberType=false
import pytest
from sqlalchemy import select, func
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import songs
from .constant_fixtures_for_test import *
from .common_fixtures import *
from .mocks.db_data.special_strings_reference import chinese1


sg = songs.columns

@pytest.mark.skip()
def test_iron_str(fixture_conn_cardboarddb: Connection):
	conn = fixture_conn_cardboarddb
	sg_name = sg.name
	sg_pk = sg.pk
	query = select(sg_name,\
		sg_name.label("ironedStr")
	).where(sg_pk == 50)
	record = conn.execute(query).fetchone()
	if record:
		assert record.name == chinese1
		assert record.ironedStr == "mu hei jiang si"
	else:
		assert False

@pytest.mark.populateFnName("fixture_db_empty_populate_factory")
def test_next_directory_level(fixture_conn_cardboarddb: Connection):
	conn = fixture_conn_cardboarddb
	path = "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"\
		"01._Come_Together_-_The_Beatles.flac"
	query = select(func.next_directory_level(path, ""))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/"

	query = select(func.next_directory_level(path, "P"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/"
	query = select(func.next_directory_level(path, "Pop"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/"
	query = select(func.next_directory_level(path, "Pop/"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/"
	query = select(func.next_directory_level(path, "Pop/Pop"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/"
	query = select(func.next_directory_level(path, "Pop/Pop_A-"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/"
	query = select(func.next_directory_level(path, "Pop/Pop_A-F"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/"
	query = select(func.next_directory_level(path, "Pop/Pop_A-F/"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/Beatles,_The/"
	query = select(func.next_directory_level(path, "Pop/Pop_A-F/Beatles,_The/"))
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"
	query = select(
		func.next_directory_level(path, "Pop/Pop_A-F/Beatles,_The/Abbey_Road/")
	)
	result = conn.execute(query).fetchone()
	assert result
	assert result[0] == "Pop/Pop_A-F/Beatles,_The/Abbey_Road/"\
		"01._Come_Together_-_The_Beatles.flac"