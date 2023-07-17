from musical_chairs_libs.services import SongInfoService
from .constant_fixtures_for_test import *
from .common_fixtures import\
	fixture_song_info_service as fixture_song_info_service
from .common_fixtures import *
from .mocks.db_population import\
	get_initial_songs,\
	get_initial_albums,\
	get_initial_artists,\
	get_initial_stations
from musical_chairs_libs.dtos_and_utilities import StationSongTuple

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

def test_add_album(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	pk = songInfoService.get_or_save_album("who_1_album", 5)
	assert pk == 10
	pk = songInfoService.get_or_save_album("bat_album", 5)
	assert pk == len(get_initial_albums()) + 1
	pk = songInfoService.get_or_save_album("who_1_album", 4)
	assert pk == len(get_initial_albums()) + 2

def test_song_ls(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_alpha") #random user
	assert user
	paths = sorted(songInfoService.song_ls(user), key=lambda d: d.path)
	assert len(paths) == 4
	assert paths[0].path == "blitz/"
	assert paths[1].path == "foo/"
	assert paths[2].path == "jazz/"
	assert paths[3].path == "tossedSlash/"

	paths = sorted(songInfoService.song_ls(user, "foo/"), key=lambda d: d.path)
	assert len(paths) == 4
	assert paths[0].path == "foo/bar/"
	assert paths[1].path == "foo/dude/"
	assert paths[2].path == "foo/goo/"
	assert paths[3].path == "foo/rude/"

def test_song_ls_user_with_paths(
	fixture_song_info_service: SongInfoService,
	fixture_path_user_factory: Callable[[str], AccountInfo]
):
	songInfoService = fixture_song_info_service
	user = fixture_path_user_factory("testUser_uniform") #random user
	paths = sorted(songInfoService.song_ls(user),key=lambda d: d.path)
	# this is no longer expected behavior
	# assert len(paths) == 2
	# assert paths[0].path == "foo/bar/"
	# assert paths[1].path == "foo/dude/"

	assert len(paths) == 1
	assert paths[0].path == "foo/"

	paths = sorted(songInfoService.song_ls(user, "foo/"), key=lambda d: d.path)
	assert len(paths) == 2
	assert paths[0].path == "foo/bar/"
	assert paths[1].path == "foo/dude/"


def test_get_songs_by_station_id(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert len(songs) == 11
	assert [6, 11, 16, 17, 24, 25, 26, 27, 34, 36, 43 ] == songs

def test_get_song_stations_linked(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	result = list(songInfoService.get_station_songs(
		songIds=43,
		stationIds=1
	))
	assert result and len(result) == 1
	assert result[0].songId == 43
	assert result[0].stationId == 1

	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 1],
		stationIds=[1, 2]
	), key=lambda x: (x.songId, x.stationId))

	assert result and len(result) == 3
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 43
	assert result[1].stationId == 1
	assert result[2].songId == 43
	assert result[2].stationId == 2


	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 1, 2],
		stationIds=[1, 2]
	), key=lambda x: (x.songId, x.stationId))

	assert result and len(result) == 4
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 2
	assert result[1].stationId == 1
	assert result[2].songId == 43
	assert result[2].stationId == 1
	assert result[3].songId == 43
	assert result[3].stationId == 2

	result = sorted(songInfoService.get_station_songs(
		stationIds=[1, 3, 2],
		songIds=[24, 43, 1, 2]
	), key=lambda x: (x.songId, x.stationId))

	assert result and len(result) == 6
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 2
	assert result[1].stationId == 1
	assert result[2].songId == 24
	assert result[2].stationId == 3
	assert result[3].songId == 43
	assert result[3].stationId == 1
	assert result[4].songId == 43
	assert result[4].stationId == 2
	assert result[5].songId == 43
	assert result[5].stationId == 3


def test_get_song_stations_unlinked(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service

	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 1, 2, 21],
		stationIds=[1, 2, 3]
	), key=lambda x: (x.songId, x.stationId))

	assert result and len(result) == 6
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 2
	assert result[1].stationId == 1
	assert result[2].songId == 21
	assert result[2].stationId == 1
	assert result[3].songId == 43
	assert result[3].stationId == 1
	assert result[4].songId == 43
	assert result[4].stationId == 2
	assert result[5].songId == 43
	assert result[5].stationId == 3

def test_get_song_stations_extra_filters(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	result = sorted(songInfoService.get_station_songs(
		songIds=[1, 2, 24, 43],
		stationIds=1
	), key=lambda x: x.songId)

	assert result and len(result) == 2
	assert result[0].songId == 2
	assert result[0].stationId == 1
	assert result[1].songId == 43
	assert result[1].stationId == 1

	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 1, 2, 24, 32, 33],
		stationIds=[1,4]
	), key=lambda x: x.songId)

	assert result and len(result) == 4
	assert result[0].songId == 2
	assert result[0].stationId == 1
	assert result[1].songId == 32
	assert result[1].stationId == 4
	assert result[2].songId == 33
	assert result[2].stationId == 4
	assert result[3].songId == 43
	assert result[3].stationId == 1

	result = sorted(songInfoService.get_station_songs(
		stationIds=[1,4],
		songIds=43
	), key=lambda x: x.songId)

	assert result and len(result) == 1
	assert result[0].songId == 43
	assert result[0].stationId == 1

	result = sorted(songInfoService.get_station_songs(
		stationIds=[1,4],
		songIds=[43,32]
	), key=lambda x: x.songId)

	assert result and len(result) == 2
	assert result[0].songId == 32
	assert result[0].stationId == 4
	assert result[1].songId == 43
	assert result[1].stationId == 1


def test_get_song_stations_missing_ids(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	badStationId = len(get_initial_stations()) + 1

	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 2, 1, 21, 33],
		stationIds=[1, 2, 3, badStationId]
	), key=lambda x: x.songId)

	assert result and len(result) == 6
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 2
	assert result[1].stationId == 1
	assert result[2].songId == 21
	assert result[2].stationId == 1
	assert result[3].songId == 43
	assert result[3].stationId == 1
	assert result[4].songId == 43
	assert result[4].stationId == 2
	assert result[5].songId == 43
	assert result[5].stationId == 3

	badSongId = len(get_initial_songs()) + 1

	result = sorted(songInfoService.get_station_songs(
		songIds=[43, 1, 2, 21, badSongId],
		stationIds=[1, 2, 3, badStationId]
	), key=lambda x: x.songId)

	assert result and len(result) == 6
	assert result[0].songId == 1
	assert result[0].stationId == 2
	assert result[1].songId == 2
	assert result[1].stationId == 1
	assert result[2].songId == 21
	assert result[2].stationId == 1
	assert result[3].songId == 43
	assert result[3].stationId == 1
	assert result[4].songId == 43
	assert result[4].stationId == 2
	assert result[5].songId == 43
	assert result[5].stationId == 3


def test_remove_songs_for_stations(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert len(songs) == 11
	assert [6, 11, 16, 17, 24, 25, 26, 27, 34, 36, 43] == songs
	result = songInfoService.remove_songs_for_stations([(43, 3),StationSongTuple(34, 3)]
	)
	assert result == 2
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert [6, 11, 16, 17, 24, 25, 26, 27, 36] == songs

def test_link_songs_with_station(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 0
	songInfoService.link_songs_with_stations(
		[StationSongTuple(34, 7),StationSongTuple(43, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43

def test_link_songs_with_station_duplicates(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 0
	songInfoService.link_songs_with_stations(
		[StationSongTuple(34, 7),StationSongTuple(43, 7), StationSongTuple(43, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43

def test_link_songs_with_station_nonexistent_songs(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	initialSongs = get_initial_songs()
	badId = len(initialSongs) + 1
	songInfoService.link_songs_with_stations(
		[StationSongTuple(34, 7), StationSongTuple(43, 7), StationSongTuple(badId, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43


def test_link_songs_with_station_nonexistent_station(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	initialStations = get_initial_stations()
	badId = len(initialStations) + 1
	results = list(songInfoService\
		.link_songs_with_stations([StationSongTuple(34, badId), StationSongTuple(43, badId)]))
	assert len(results) == 0
	songs = list(songInfoService.get_songIds(stationKey=badId))
	assert len(songs) == 0

def test_link_already_linked_songs_with_stations(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	results = list(songInfoService\
		.link_songs_with_stations([StationSongTuple(27, 3), StationSongTuple(20, 2)]))
	assert len(results) == 2

def test_get_albums(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	allAlbums = list(songInfoService.get_albums())
	assert allAlbums
	assert len(allAlbums) == len(get_initial_albums())

def test_get_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	allArtists = list(songInfoService.get_artists())
	assert allArtists
	assert len(allArtists) == len(get_initial_artists())

	specificArtist = list(songInfoService.get_artists(artistKeys=5))
	assert specificArtist
	assert len(specificArtist) == 1
	assert specificArtist[0].name == "echo_artist"
	specificArtists = sorted(
		songInfoService.get_artists(artistKeys=[5, 1, 2]),
		key=lambda a: a.id or 0
	)
	assert specificArtists

	assert len(specificArtists) == 3
	assert specificArtists[0].name == "alpha_artist"
	assert specificArtists[1].name == "bravo_artist"
	assert specificArtists[2].name == "echo_artist"

	emptyArtists = sorted(
		songInfoService.get_artists(artistKeys=[]),
		key=lambda a: a.id or 0
	)
	assert emptyArtists is not None and len(emptyArtists) == 0


def test_get_artists_for_songs(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service

	songArtists = list(songInfoService.get_song_artists(songIds=17))

	assert songArtists
	assert len(songArtists) == 5
	artists = sorted(songInfoService.get_artists(
			artistKeys=(sa.artistId for sa in songArtists)
	), key=lambda a: a.id or 0)

	assert len(artists) == 5
	assert artists[0].name == "bravo_artist"
	assert artists[1].name == "echo_artist"
	assert artists[2].name == "foxtrot_artist"
	assert artists[3].name == "juliet_artist"
	assert artists[4].name == "kilo_artist"

	songArtists = list(songInfoService.get_song_artists(songIds=[8, 1]))
	assert songArtists

	assert len(songArtists) == 3

	artists = sorted(songInfoService.get_artists(
			artistKeys=(sa.artistId for sa in songArtists)
	), key=lambda a: a.id or 0)

	assert artists and len(artists) == 3
	assert artists[0].name == "delta_artist"
	assert artists[1].name == "echo_artist"
	assert artists[2].name == "foxtrot_artist"




def test_get_single_song_for_edit(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([1], user))
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
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 2
		assert sortedStations[0].name == "papa_station"
		assert sortedStations[0].displayName == "Come to papa"

		assert sortedStations[1].id == 6
		assert sortedStations[1].name == "yankee_station"
		assert sortedStations[1].displayName == "Blurg the blergos"


def test_get_song_for_edit_without_stations(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([39], user))
	assert songInfo
	assert songInfo.name == "foxtrot2_song"
	assert songInfo.stations != None and len(songInfo.stations) == 0

def test_get_song_for_edit_without_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoService = fixture_song_info_service
	songInfo = next(songInfoService.get_songs_for_edit([58], user))
	assert songInfo
	assert songInfo.name == "alpha4_song"
	assert songInfo.artists != None and len(songInfo.artists) == 0

def test_get_song_for_edit_without_album(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([27], user))
	assert songInfo
	assert songInfo.name == "tango2_song"
	assert songInfo.album == None


def test_get_multiple_songs_for_edit(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoList = sorted(songInfoService.get_songs_for_edit([1, 17], user),
		key=lambda s: s.id
	)
	assert songInfoList and len(songInfoList) == 2
	songInfo = songInfoList[0]
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
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 2
		assert sortedStations[0].name == "papa_station"
		assert sortedStations[0].displayName == "Come to papa"

		assert sortedStations[1].id == 6
		assert sortedStations[1].name == "yankee_station"
		assert sortedStations[1].displayName == "Blurg the blergos"

	songInfo = songInfoList[1]
	assert songInfo.path == "foo/goo/shoo/india"
	assert songInfo.name == "india_song"
	assert songInfo.album and songInfo.album.id == 8
	assert songInfo.album and songInfo.album.name == "shoo_album"
	assert songInfo.artists and len(songInfo.artists) == 5
	sortedArtists = sorted(songInfo.artists, key=lambda a: a.id or 0)
	assert len(sortedArtists) == 5
	assert sortedArtists[0].id == 2
	assert sortedArtists[0].name == "bravo_artist"
	assert sortedArtists[1].id == 5
	assert sortedArtists[1].name == "echo_artist"
	assert sortedArtists[2].id == 6
	assert sortedArtists[2].name == "foxtrot_artist"
	assert sortedArtists[3].id == 10
	assert sortedArtists[3].name == "juliet_artist"
	assert sortedArtists[4].id == 11
	assert sortedArtists[4].name == "kilo_artist"
	assert not songInfo.primaryArtist
	assert not songInfo.covers or len(songInfo.covers) == 0
	assert songInfo.track == 2
	assert songInfo.disc == 1
	assert not songInfo.genre
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 1
		assert sortedStations[0].name == "oscar_station"
		assert sortedStations[0].displayName == "Oscar the grouch"

		assert sortedStations[1].id == 3
		assert sortedStations[1].name == "romeo_station"
		assert sortedStations[1].displayName == "But soft, what yonder wind breaks"

def test_get_multiple_songs_for_edit2(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoList = sorted(songInfoService.get_songs_for_edit([2, 3], user),
		key=lambda s: s.id
	)
	assert len(songInfoList) == 2

def test_get_duplicate_song(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoList = sorted(songInfoService.get_songs_for_edit(
			[1, 1, 1, 1, 6],
			user
		),
		key=lambda s: s.id
	)

	assert len(songInfoList) == 2
	assert songInfoList[0].id == 1
	assert songInfoList[1].id == 6

def test_get_user_paths(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	results = list(songInfoService.get_paths_user_can_see(11))
	assert results

def test_get_song_with_owner_info(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_romeo") #random user
	assert user
	results = next(songInfoService.get_songs_for_edit([59], user))
	album = results.album
	assert album
	albumOwner = album.owner
	assert albumOwner.displayName == "julietDisplay"
	albumArtist = album.albumArtist
	assert albumArtist
	albumArtistOwner = albumArtist.owner
	assert albumArtistOwner
	assert albumArtistOwner.username == "testUser_kilo"
	primaryArtist = results.primaryArtist
	assert primaryArtist
	primaryArtistOwner = primaryArtist.owner
	assert primaryArtistOwner
	assert primaryArtistOwner.username == "testUser_november"
	assert results.artists
	assert len(results.artists) == 2
	artsit0Owner = results.artists[0].owner
	assert artsit0Owner.displayName == "IndiaDisplay"
	artsit1Owner = results.artists[1].owner
	assert artsit1Owner.username == "testUser_hotel"
	assert results.stations
	assert len(results.stations) == 2
	station0Owner = results.stations[0].owner
	assert station0Owner
	assert station0Owner.username == "testUser_bravo"
	station1Owner = results.stations[1].owner
	assert station1Owner
	assert station1Owner.displayName == "julietDisplay"