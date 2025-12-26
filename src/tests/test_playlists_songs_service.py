from musical_chairs_libs.services import (
	AccountsService,
	PlaylistsSongsService
)
from .constant_fixtures_for_test import *
from .common_fixtures import (
	fixture_playlist_service as fixture_playlist_service,
	fixture_account_service as fixture_account_service,
	fixture_playlists_songs_service as fixture_playlists_songs_service,
)
from .common_fixtures import *





def test_move_songs_1(
	fixture_playlists_songs_service: PlaylistsSongsService,
	fixture_account_service: AccountsService
):
	playlistsSongsService = fixture_playlists_songs_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	results = [*playlistsSongsService.get_songs(5, user)]
	assert results[0].id == 2
	assert results[1].id == 3
	assert results[2].id == 4
	assert results[3].id == 5
	assert results[4].id == 6
	assert results[5].id == 7
	assert results[6].id == 8
	assert results[7].id == 9
	assert results[8].id == 10
	assert results[9].id == 11
	assert results[10].id == 12
	assert results[11].id == 13
	assert results[12].id == 14
	assert results[13].id == 15
	assert results[14].id == 16

	playlistsSongsService.move_song(5, 11, 1)
	results = [*playlistsSongsService.get_playlist_songs(playlistIds=5)]
	assert results[0].songid == 11
	assert results[1].songid == 2
	assert results[2].songid == 3
	assert results[3].songid == 4
	assert results[4].songid == 5
	assert results[5].songid == 6
	assert results[6].songid == 7
	assert results[7].songid == 8
	assert results[8].songid == 9
	assert results[9].songid == 10
	assert results[10].songid == 12
	assert results[11].songid == 13
	assert results[12].songid == 14
	assert results[13].songid == 15
	assert results[14].songid == 16

	playlistsSongsService.move_song(5, 6, 1)
	results = [*playlistsSongsService.get_playlist_songs(playlistIds=5)]
	assert results[0].songid == 6
	assert results[1].songid == 11
	assert results[2].songid == 2
	assert results[3].songid == 3
	assert results[4].songid == 4
	assert results[5].songid == 5
	assert results[6].songid == 7
	assert results[7].songid == 8
	assert results[8].songid == 9
	assert results[9].songid == 10
	assert results[10].songid == 12
	assert results[11].songid == 13
	assert results[12].songid == 14
	assert results[13].songid == 15
	assert results[14].songid == 16


def test_move_songs_2(
	fixture_playlists_songs_service: PlaylistsSongsService,
	fixture_account_service: AccountsService
):
	playlistsSongsService = fixture_playlists_songs_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha")
	assert user
	results = [*playlistsSongsService.get_playlist_songs(playlistIds=27)]
	assert len(results) == 3
	assert results[0].songid == 1
	assert results[1].songid == 42
	assert results[2].songid == 86
	playlistsSongsService.rebalance(27)
	results = [*playlistsSongsService.get_playlist_songs(playlistIds=27)]
	assert results[0].lexorder == "1"
	assert results[1].lexorder == "2"
	assert results[2].lexorder == "3"
	playlistsSongsService.move_song(27, 42, 1)
	results = [*playlistsSongsService.get_playlist_songs(playlistIds=27)]
	pass