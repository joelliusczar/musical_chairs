#pyright: reportMissingTypeStubs=false
from .common_fixtures import db_conn as db_conn, \
	radio_handle_in_mem as radio_handle_in_mem, \
	radio_handle as radio_handle
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.radio_handle import RadioHandle



def test_construct_radio_handle():
	envMgr = EnvManager()
	RadioHandle("test")
	RadioHandle("test2", envMgr)

def test_radio_init(radio_handle_in_mem: RadioHandle):
	num = radio_handle_in_mem.ices_init()
	assert num == 1

def test_radio_get_next_song(radio_handle_in_mem: RadioHandle):
	radio_handle_in_mem.ices_init()
	path = radio_handle_in_mem.ices_get_next()
	print(path)

def test_radio_get_next_song_with_real_db(radio_handle: RadioHandle):
	radio_handle.ices_init()
	path = radio_handle.ices_get_next()
	print(path)