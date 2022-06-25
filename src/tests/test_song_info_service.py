from musical_chairs_libs.song_info_service import SongInfoService
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_song_info_service as fixture_song_info_service
from .common_fixtures import *

def test_songs_query(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_song_refs(songName=None))
	assert len(songs) == 6

def test_song_query_paging(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_song_refs(page=0, pageSize=5))
	assert len(songs) == 5
	assert songs[0].name == "sierra_song"
	assert songs[4].name == "victor_song"
	songs2 = list(songInfoService.get_song_refs(page=1, pageSize=5))
	assert len(songs2) == 5
	assert songs2[0].name == "whiskey_song"
	assert songs2[4].name == "alpha_song"

def test_add_artists(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	pk = songInfoService.get_or_save_artist("foxtrot_artist")
	assert pk == 6
	pk = songInfoService.get_or_save_artist("hotel_artist")
	assert pk == 8

def test_add_album(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	pk = songInfoService.get_or_save_album("who_1_album", 5)
	assert pk == 10
	pk = songInfoService.get_or_save_album("bat_album", 5)
	assert pk == 12
	pk = songInfoService.get_or_save_album("who_1_album", 4)
	assert pk == 13

def test_song_ls(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	paths = list(sorted(songInfoService.song_ls(), key=lambda d: d.path))
	assert len(paths) == 3
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"