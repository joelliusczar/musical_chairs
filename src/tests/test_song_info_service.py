from musical_chairs_libs.services import SongInfoService
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_song_info_service as fixture_song_info_service
from .common_fixtures import *
from .mocks.db_population import get_starting_songs, get_starting_tags

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

def test_get_songs_by_tag_id(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(
		list(songInfoService.get_songs(tagId=3)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 11
	assert songs[0].name == "alpha2_song"
	assert songs[0].id == 34
	assert songs[1].name == "bravo_song"
	assert songs[1].id == 11
	assert songs[2].name == "charlie2_song"
	assert songs[2].id == 36
	assert songs[3].name == "hotel_song"
	assert songs[3].id == 16
	assert songs[4].name == "india_song"
	assert songs[4].id == 17
	assert songs[5].name == "juliet2_song"
	assert songs[5].id == 43
	assert songs[6].name == "papa_song"
	assert songs[6].id == 24
	assert songs[7].name == "romeo_song"
	assert songs[7].id == 25
	assert songs[8].name == "sierra2_song"
	assert songs[8].id == 26
	assert songs[9].name == "tango2_song"
	assert songs[9].id == 27
	assert songs[10].name == "whiskey_song"
	assert songs[10].id == 6

def test_remove_songs_for_tag(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	result = songInfoService.remove_songs_for_tag(3, [43, 34])
	assert result == 2
	songs = sorted(
		list(songInfoService.get_songs(tagId=3)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 9
	assert songs[0].name == "bravo_song"
	assert songs[0].id == 11
	assert songs[1].name == "charlie2_song"
	assert songs[1].id == 36
	assert songs[2].name == "hotel_song"
	assert songs[2].id == 16
	assert songs[3].name == "india_song"
	assert songs[3].id == 17
	assert songs[4].name == "papa_song"
	assert songs[4].id == 24
	assert songs[5].name == "romeo_song"
	assert songs[5].id == 25
	assert songs[6].name == "sierra2_song"
	assert songs[6].id == 26
	assert songs[7].name == "tango2_song"
	assert songs[7].id == 27
	assert songs[8].name == "whiskey_song"
	assert songs[8].id == 6


def test_link_songs_with_tag(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(
		list(songInfoService.get_songs(tagId=7)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 0
	songInfoService.link_songs_with_tag(7, [34, 43])
	songs = sorted(
		list(songInfoService.get_songs(tagId=7)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 2
	assert songs[0].name == "alpha2_song"
	assert songs[0].id == 34
	assert songs[1].name == "juliet2_song"
	assert songs[1].id == 43

def test_link_songs_with_tag_duplicates(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	songs = sorted(
		list(songInfoService.get_songs(tagId=7)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 0
	songInfoService.link_songs_with_tag(7, [34, 43, 43])
	songs = sorted(
		list(songInfoService.get_songs(tagId=7)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 2
	assert songs[0].name == "alpha2_song"
	assert songs[0].id == 34
	assert songs[1].name == "juliet2_song"
	assert songs[1].id == 43

def test_link_songs_with_tag_nonexistent_songs(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	startingSongs = get_starting_songs()
	badId = len(startingSongs) + 1
	songInfoService.link_songs_with_tag(7, [34, 43, badId])
	songs = sorted(
		list(songInfoService.get_songs(tagId=7)),
		key=lambda s: s.name or ""
	)
	assert len(songs) == 2
	assert songs[0].name == "alpha2_song"
	assert songs[0].id == 34
	assert songs[1].name == "juliet2_song"
	assert songs[1].id == 43


def test_link_songs_with_tag_nonexistent_tag(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	startingTags = get_starting_tags()
	badId = len(startingTags) + 1
	resultTag, resultSongs  = songInfoService\
		.link_songs_with_tag(badId, [34, 43])
	assert resultTag is None
	assert len(list(resultSongs)) == 0
	songs = list(songInfoService.get_songs(tagId=badId))
	assert len(songs) == 0

def test_get_albums(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	allAlbums = list(songInfoService.get_albums())
	assert allAlbums

def test_get_song_for_edit(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	songInfo = songInfoService.get_song_for_edit(1)
	assert songInfo

	assert songInfo.path == "foo/goo/boo/sierra"
	assert songInfo.name == "sierra_song"
	assert songInfo.album and songInfo.album.id == 11
	assert songInfo.album and songInfo.album.name == "boo_album"
	assert songInfo.artists and len(songInfo.artists) == 1
	sortedArtists = sorted(songInfo.artists, key=lambda a: a.id or 0)
	assert len(sortedArtists) == 1
	assert sortedArtists[0].id == 4
	assert sortedArtists[0].name == "delta_artist"
	assert songInfo.primaryArtist
	if songInfo.primaryArtist:
		assert songInfo.primaryArtist.id == 6
		assert songInfo.primaryArtist.name == "foxtrot_artist"
	assert not songInfo.covers or len(songInfo.covers) == 0
	assert songInfo.track == 1
	assert songInfo.disc == 1
	assert songInfo.genre == "pop"
	assert songInfo.tags and len(songInfo.tags) == 2
	sortedTags = sorted(songInfo.tags, key=lambda t: t.id or 0)
	if songInfo.tags:
		assert sortedTags[0].id == 2
		assert sortedTags[0].name == "lima_tag"

		assert sortedTags[1].id == 6
		assert sortedTags[1].name == "papa_tag"
