#pyright: reportMissingTypeStubs=false
from .common_fixtures import (
	fixture_radio_handle as fixture_radio_handle,
	fixture_conn_cardboarddb as fixture_conn_cardboarddb,
	fixture_populated_db_name as fixture_populated_db_name,
)
from .common_fixtures import *
from .constant_fixtures_for_test import *
from musical_chairs_libs.services import EnvManager
from musical_chairs_libs.radio_handle import RadioHandle



def test_construct_radio_handle(fixture_populated_db_name: str):
	envMgr = EnvManager()
	RadioHandle(1,fixture_populated_db_name)
	RadioHandle(2,fixture_populated_db_name, envMgr)

def test_radio_init(fixture_radio_handle: RadioHandle):
	num = fixture_radio_handle.ices_init()
	assert num == 1

def test_radio_get_next_song(fixture_radio_handle: RadioHandle):
	fixture_radio_handle.ices_init()
	path = fixture_radio_handle.ices_get_next()
	print(path)

def test_radio_get_next_song_with_real_db(fixture_radio_handle: RadioHandle):
	fixture_radio_handle.ices_init()
	path = fixture_radio_handle.ices_get_next()
	print(path)