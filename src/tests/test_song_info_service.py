from musical_chairs_libs.song_info_service import SongInfoService
from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem, \
	fixture_song_info_service as fixture_song_info_service

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