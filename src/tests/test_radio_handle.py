#pyright: reportMissingTypeStubs=false
from .common_fixtures import \
	fixture_radio_handle as fixture_radio_handle
from .common_fixtures import *
from .constant_fixtures_for_test import *
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.radio_handle import RadioHandle



def test_construct_radio_handle():
	envMgr = EnvManager()
	RadioHandle("test")
	RadioHandle("test2", envMgr)

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