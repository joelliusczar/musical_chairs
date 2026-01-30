import pytest
from musical_chairs_libs.services import (
	SongInfoService,
	StationsSongsService
)
from .constant_fixtures_for_test import *
from .common_fixtures import(
	fixture_song_info_service as fixture_song_info_service,
	fixture_artist_service as fixture_artist_service,
	fixture_album_service as fixture_album_service,
	fixture_station_service as fixture_station_service,
	fixture_stations_songs_service as fixture_stations_songs_service,
	fixture_primary_user as fixture_primary_user
)
from .common_fixtures import *
from .mocks.db_population import (
	get_initial_songs,
	get_initial_albums,
	get_initial_artists,
	get_initial_stations
)

from musical_chairs_libs.dtos_and_utilities import (
	PlaylistInfo,
	SimpleQueryParameters,
	SongEditInfo,
	StationInfo,
	StationSongTuple,
)



def test_songs_query(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_song_refs(songName=None))
	assert len(songs) == 5

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

def test_add_artists(fixture_artist_service: ArtistService):
	artistService = fixture_artist_service
	pk = artistService.get_or_save_artist("foxtrot_artist")
	assert pk == 6
	pk = artistService.get_or_save_artist("hotel_artist")
	assert pk == 8

@pytest.mark.current_username("testUser_november")
def test_change_song_tracknum(
		fixture_song_info_service: SongInfoService,
		fixture_account_service: AccountsService
):
		songInfoService = fixture_song_info_service
		accountService = fixture_account_service

		# Get a user for the test
		user, _ = accountService.get_account_for_login("testUser_november")	# random user
		assert user

		# Fetch the song for editing
		songInfo = next(songInfoService.get_songs_for_edit([84]))
		assert songInfo
		assert songInfo.tracknum == 0

		# Modify the trackNum
		copy = songInfo.model_copy()
		copy.tracknum = 5	# Change the trackNum to a new value

		# Save the changes
		afterSaved = next(songInfoService.save_songs([84], copy))
		assert afterSaved.tracknum == 5	# Verify the trackNum was updated

		# Refetch the song and verify the change persisted
		refetched = next(songInfoService.get_songs_for_edit([84]))
		assert refetched.tracknum == 5

@pytest.mark.current_username("testUser_november")
def test_save_song_remove_1_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.artists
	sortedArtists = sorted(copy.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 20 #primary artist
	assert sortedArtists[3].id == 21
	copy.artists = [a for a in copy.artists if a.id != 19]
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert afterSaved.artists
	sortedArtists = sorted(afterSaved.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 20 #primary artist
	assert sortedArtists[2].id == 21
	refetched = next(songInfoService.get_songs_for_edit([84]))
	sortedArtists = sorted(refetched.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 20 #primary artist
	assert sortedArtists[2].id == 21


@pytest.mark.current_username("testUser_november")
def test_save_song_remove_nonprimary_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.artists
	sortedArtists = sorted(copy.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 20 #primary artist
	assert sortedArtists[3].id == 21
	copy.artists.pop()
	copy.artists.pop()
	copy.artists.pop()
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert not afterSaved.artists
	assert afterSaved.primaryartist
	sortedArtists = sorted(afterSaved.allArtists, key=lambda a: a.id)
	assert len(sortedArtists) == 1
	assert sortedArtists[0].id == 20
	refetched = next(songInfoService.get_songs_for_edit([84]))
	sortedArtists = sorted(refetched.allArtists, key=lambda a: a.id)
	assert len(sortedArtists) == 1
	assert sortedArtists[0].id == 20


@pytest.mark.current_username("testUser_november")
def test_save_song_remove_primary_artist(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.artists
	sortedArtists = sorted(copy.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 20 #primary artist
	assert sortedArtists[3].id == 21
	copy.primaryartist = None
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert afterSaved.artists
	assert not afterSaved.primaryartist
	sortedArtists = sorted(afterSaved.allArtists, key=lambda a: a.id)
	assert len(sortedArtists) == 3
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 21
	refetched = next(songInfoService.get_songs_for_edit([84]))
	sortedArtists = sorted(refetched.allArtists, key=lambda a: a.id)
	assert len(sortedArtists) == 3
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 21

@pytest.mark.current_username("testUser_november")
def test_save_song_remove_all_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.artists
	sortedArtists = sorted(copy.allArtists, key=lambda a: a.id)
	assert sortedArtists[0].id == 18
	assert sortedArtists[1].id == 19
	assert sortedArtists[2].id == 20 #primary artist
	assert sortedArtists[3].id == 21
	copy.primaryartist = None
	copy.artists.pop()
	copy.artists.pop()
	copy.artists.pop()
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert not afterSaved.artists
	assert not afterSaved.primaryartist
	refetched = next(songInfoService.get_songs_for_edit([84]))
	assert not refetched.artists
	assert not refetched.primaryartist

@pytest.mark.current_username("testUser_november")
def test_save_song_swap_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService,
	fixture_artist_service: ArtistService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	artistService = fixture_artist_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([85]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.artists
	assert len(copy.artists) == 1
	assert copy.artists[0].id == 22
	replacement = next(artistService.get_artists(artistKeys=23))
	copy.artists = [replacement]
	afterSaved = next(songInfoService.save_songs([85], copy))
	assert afterSaved.artists
	assert len(afterSaved.artists) == 1
	assert afterSaved.artists[0].id == 23
	refetched = next(songInfoService.get_songs_for_edit([85]))
	assert refetched.artists
	assert len(refetched.artists) == 1
	assert refetched.artists[0].id == 23
	copy = songInfo.model_copy()
	assert copy
	copy.artists = []
	copy.primaryartist = next(artistService.get_artists(artistKeys=24))
	afterSaved = next(songInfoService.save_songs([85], copy))
	assert not afterSaved.artists
	assert afterSaved.primaryartist
	assert afterSaved.primaryartist.id == 24
	refetched = next(songInfoService.get_songs_for_edit([85]))
	assert not refetched.artists
	assert refetched.primaryartist
	assert refetched.primaryartist.id == 24

	copy = refetched.model_copy()
	copy.primaryartist = next(artistService.get_artists(artistKeys=25))
	afterSaved = next(songInfoService.save_songs([85], copy))
	assert not afterSaved.artists
	assert afterSaved.primaryartist
	assert afterSaved.primaryartist.id == 25
	refetched = next(songInfoService.get_songs_for_edit([85]))
	assert not refetched.artists
	assert refetched.primaryartist
	assert refetched.primaryartist.id == 25



def test_add_album(
	fixture_album_service: AlbumService
):
	albumService = fixture_album_service
	pk = albumService.get_or_save_album("who_1_album", 5)
	assert pk == 10
	pk = albumService.get_or_save_album("bat_album", 5)
	assert pk == len(get_initial_albums()) + 1
	pk = albumService.get_or_save_album("who_1_album", 4)
	assert pk == len(get_initial_albums()) + 2

def test_get_songs_by_station_id(fixture_song_info_service: SongInfoService):
	songInfoService = fixture_song_info_service
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert len(songs) == 11
	assert [6, 11, 16, 17, 24, 25, 26, 27, 34, 36, 43 ] == songs

@pytest.mark.current_username("testUser_bravo")
def test_save__multiple_song_add_station_and_playlist(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	songInfoList = sorted(songInfoService.get_songs_for_edit([39, 48]),
		key=lambda s: s.id
	)
	assert not songInfoList[0].stations
	assert not songInfoList[1].stations

	bravo_user, _ = accountService.get_account_for_login("testUser_bravo")
	assert bravo_user

	sendData = SongEditInfo(
		id=0,
		name="",
		treepath="",
		internalpath="",
		stations=[
			StationInfo(id=5, name="tango_station")
		],
		playlists=[
			PlaylistInfo(
				id=7,
				name="uniform_playlist",
				owner=bravo_user,
			)
		],
		touched={"stations","playlists"}
	)


	list(songInfoService.save_songs([39, 48], sendData))
	songInfoList = sorted(songInfoService.get_songs_for_edit([39, 48]),
		key=lambda s: s.id
	)
	assert songInfoList[0].stations
	assert len(songInfoList[0].stations) == 1
	assert songInfoList[1].stations
	assert len(songInfoList[1].stations) == 1

	assert songInfoList[0].playlists
	assert len(songInfoList[0].playlists) == 1
	assert songInfoList[1].playlists
	assert len(songInfoList[1].playlists) == 1

@pytest.mark.current_username("testUser_november")
def test_save_song_remove_1_station(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.stations
	sortedStations = sorted(copy.stations, key=lambda a: a.id)
	assert sortedStations[0].id == 21
	assert sortedStations[1].id == 22
	assert sortedStations[2].id == 23
	copy.stations = [s for s in copy.stations if s.id != 22]
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert afterSaved.stations
	sortedStations = sorted(afterSaved.stations, key=lambda a: a.id)
	assert sortedStations[0].id == 21
	assert sortedStations[1].id == 23
	refetched = next(songInfoService.get_songs_for_edit([84]))
	assert refetched.stations
	sortedStations = sorted(refetched.stations, key=lambda a: a.id)
	assert sortedStations[0].id == 21
	assert sortedStations[1].id == 23

@pytest.mark.current_username("testUser_november")
def test_save_song_remove_all_stations(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([84]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.stations
	sortedStations = sorted(copy.stations, key=lambda a: a.id)
	assert sortedStations[0].id == 21
	assert sortedStations[1].id == 22
	assert sortedStations[2].id == 23
	copy.stations = []
	afterSaved = next(songInfoService.save_songs([84], copy))
	assert not afterSaved.stations
	refetched = next(songInfoService.get_songs_for_edit([84]))
	assert not refetched.stations

@pytest.mark.current_username("testUser_kilo")
def test_save_song_swap_station(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService,
	fixture_station_service: StationService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	stationService = fixture_station_service
	user,_ = accountService.get_account_for_login("testUser_kilo") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([85]))
	copy = songInfo.model_copy()
	assert copy
	assert copy.stations
	assert len(copy.stations) == 1
	assert copy.stations[0].id == 24
	replacement = next(stationService.get_stations(stationKeys=25))
	copy.stations = [replacement]
	afterSaved = next(songInfoService.save_songs([85], copy))
	assert afterSaved.stations
	assert len(afterSaved.stations) == 1
	assert afterSaved.stations[0].id == 25
	refetched = next(songInfoService.get_songs_for_edit([85]))
	assert refetched.stations
	assert len(refetched.stations) == 1
	assert refetched.stations[0].id == 25

def test_get_song_stations_linked(
	fixture_stations_songs_service: StationsSongsService
):
	stationsSongsService = fixture_stations_songs_service
	result = list(stationsSongsService.get_station_songs(
		songIds=43,
		stationIds=1
	))
	assert result and len(result) == 1
	assert result[0].songid == 43
	assert result[0].stationid == 1

	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 1],
		stationIds=[1, 2]
	), key=lambda x: (x.songid, x.stationid))

	assert result and len(result) == 3
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 43
	assert result[1].stationid == 1
	assert result[2].songid == 43
	assert result[2].stationid == 2


	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 1, 2],
		stationIds=[1, 2]
	), key=lambda x: (x.songid, x.stationid))

	assert result and len(result) == 4
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 2
	assert result[1].stationid == 1
	assert result[2].songid == 43
	assert result[2].stationid == 1
	assert result[3].songid == 43
	assert result[3].stationid == 2

	result = sorted(stationsSongsService.get_station_songs(
		stationIds=[1, 3, 2],
		songIds=[24, 43, 1, 2]
	), key=lambda x: (x.songid, x.stationid))

	assert result and len(result) == 6
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 2
	assert result[1].stationid == 1
	assert result[2].songid == 24
	assert result[2].stationid == 3
	assert result[3].songid == 43
	assert result[3].stationid == 1
	assert result[4].songid == 43
	assert result[4].stationid == 2
	assert result[5].songid == 43
	assert result[5].stationid == 3


def test_get_song_stations_unlinked(
		fixture_stations_songs_service: StationsSongsService
	):
	stationsSongsService = fixture_stations_songs_service

	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 1, 2, 21],
		stationIds=[1, 2, 3]
	), key=lambda x: (x.songid, x.stationid))

	assert result and len(result) == 6
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 2
	assert result[1].stationid == 1
	assert result[2].songid == 21
	assert result[2].stationid == 1
	assert result[3].songid == 43
	assert result[3].stationid == 1
	assert result[4].songid == 43
	assert result[4].stationid == 2
	assert result[5].songid == 43
	assert result[5].stationid == 3

def test_get_song_stations_extra_filters(
	fixture_stations_songs_service: StationsSongsService
):
	stationsSongsService = fixture_stations_songs_service
	result = sorted(stationsSongsService.get_station_songs(
		songIds=[1, 2, 24, 43],
		stationIds=1
	), key=lambda x: x.songid)

	assert result and len(result) == 2
	assert result[0].songid == 2
	assert result[0].stationid == 1
	assert result[1].songid == 43
	assert result[1].stationid == 1

	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 1, 2, 24, 32, 33],
		stationIds=[1,4]
	), key=lambda x: x.songid)

	assert result and len(result) == 4
	assert result[0].songid == 2
	assert result[0].stationid == 1
	assert result[1].songid == 32
	assert result[1].stationid == 4
	assert result[2].songid == 33
	assert result[2].stationid == 4
	assert result[3].songid == 43
	assert result[3].stationid == 1

	result = sorted(stationsSongsService.get_station_songs(
		stationIds=[1,4],
		songIds=43
	), key=lambda x: x.songid)

	assert result and len(result) == 1
	assert result[0].songid == 43
	assert result[0].stationid == 1

	result = sorted(stationsSongsService.get_station_songs(
		stationIds=[1,4],
		songIds=[43,32]
	), key=lambda x: x.songid)

	assert result and len(result) == 2
	assert result[0].songid == 32
	assert result[0].stationid == 4
	assert result[1].songid == 43
	assert result[1].stationid == 1


def test_get_song_stations_missing_ids(
	fixture_stations_songs_service: StationsSongsService
):
	stationsSongsService = fixture_stations_songs_service
	badStationId = len(get_initial_stations()) + 1

	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 2, 1, 21, 33],
		stationIds=[1, 2, 3, badStationId]
	), key=lambda x: x.songid)

	assert result and len(result) == 6
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 2
	assert result[1].stationid == 1
	assert result[2].songid == 21
	assert result[2].stationid == 1
	assert result[3].songid == 43
	assert result[3].stationid == 1
	assert result[4].songid == 43
	assert result[4].stationid == 2
	assert result[5].songid == 43
	assert result[5].stationid == 3

	badSongId = len(get_initial_songs()) + 1

	result = sorted(stationsSongsService.get_station_songs(
		songIds=[43, 1, 2, 21, badSongId],
		stationIds=[1, 2, 3, badStationId]
	), key=lambda x: x.songid)

	assert result and len(result) == 6
	assert result[0].songid == 1
	assert result[0].stationid == 2
	assert result[1].songid == 2
	assert result[1].stationid == 1
	assert result[2].songid == 21
	assert result[2].stationid == 1
	assert result[3].songid == 43
	assert result[3].stationid == 1
	assert result[4].songid == 43
	assert result[4].stationid == 2
	assert result[5].songid == 43
	assert result[5].stationid == 3


def test_remove_songs_for_stations(
	fixture_song_info_service: SongInfoService,
	fixture_stations_songs_service: StationsSongsService
):
	songInfoService = fixture_song_info_service
	stationsSongsService = fixture_stations_songs_service
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert len(songs) == 11
	assert [6, 11, 16, 17, 24, 25, 26, 27, 34, 36, 43] == songs
	result = stationsSongsService.remove_songs_for_stations(
		[(43, 3),StationSongTuple(34, 3)]
	)
	assert result == 2
	songs = sorted(songInfoService.get_songIds(stationKey=3))
	assert [6, 11, 16, 17, 24, 25, 26, 27, 36] == songs

@pytest.mark.current_username("testUser_kilo")
def test_link_songs_with_station(
	fixture_song_info_service: SongInfoService,
	fixture_stations_songs_service: StationsSongsService
):
	songInfoService = fixture_song_info_service
	stationsSongsService = fixture_stations_songs_service
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 0
	stationsSongsService.link_songs_with_stations(
		[StationSongTuple(34, 7),StationSongTuple(43, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43


@pytest.mark.current_username("testUser_kilo")
def test_link_songs_with_station_duplicates(
	fixture_song_info_service: SongInfoService,
	fixture_stations_songs_service: StationsSongsService
):
	songInfoService = fixture_song_info_service
	stationsSongService = fixture_stations_songs_service
	songs = list(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 0
	stationsSongService.link_songs_with_stations(
		[StationSongTuple(34, 7),StationSongTuple(43, 7), StationSongTuple(43, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43


@pytest.mark.current_username("testUser_kilo")
def test_link_songs_with_station_nonexistent_songs(
	fixture_song_info_service: SongInfoService,
	fixture_stations_songs_service: StationsSongsService
):
	songInfoService = fixture_song_info_service
	stationsSongService = fixture_stations_songs_service
	initialSongs = get_initial_songs()
	badId = max(s["pk"] for s in initialSongs) + 1
	stationsSongService.link_songs_with_stations(
		[StationSongTuple(34, 7), StationSongTuple(43, 7), StationSongTuple(badId, 7)]
	)
	songs = sorted(songInfoService.get_songIds(stationKey=7))
	assert len(songs) == 2
	assert songs[0] == 34
	assert songs[1] == 43


def test_link_songs_with_station_nonexistent_station(
	fixture_song_info_service: SongInfoService,
	fixture_stations_songs_service: StationsSongsService
):
	songInfoService = fixture_song_info_service
	stationsSongService = fixture_stations_songs_service
	initialStations = get_initial_stations()
	badId = len(initialStations) + 1
	results = list(stationsSongService\
		.link_songs_with_stations([StationSongTuple(34, badId), StationSongTuple(43, badId)]))
	assert len(results) == 0
	songs = list(songInfoService.get_songIds(stationKey=badId))
	assert len(songs) == 0

def test_link_already_linked_songs_with_stations(
	fixture_stations_songs_service: StationsSongsService
):
	stationsSongService = fixture_stations_songs_service
	results = list(stationsSongService\
		.link_songs_with_stations([StationSongTuple(27, 3), StationSongTuple(20, 2)]))
	assert len(results) == 2

def test_get_albums(
	fixture_album_service: AlbumService
):
	albumService = fixture_album_service
	allAlbums = list(albumService.get_albums())
	assert allAlbums
	assert len(allAlbums) == len(get_initial_albums())

def test_get_artists(
	fixture_artist_service: ArtistService,
	fixture_account_service: AccountsService
):
	artistService = fixture_artist_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	allArtists = list(artistService.get_artists())
	assert allArtists
	assert len(allArtists) == len(get_initial_artists())

	specificArtist = list(artistService.get_artists(artistKeys=5))
	assert specificArtist
	assert len(specificArtist) == 1
	assert specificArtist[0].name == "echo_artist"
	specificArtists = sorted(
		artistService.get_artists(artistKeys=[5, 1, 2]),
		key=lambda a: a.id or 0
	)
	assert specificArtists

	assert len(specificArtists) == 3
	assert specificArtists[0].name == "alpha_artist"
	assert specificArtists[1].name == "bravo_artist"
	assert specificArtists[2].name == "echo_artist"

	emptyArtists = sorted(
		artistService.get_artists(artistKeys=[]),
		key=lambda a: a.id or 0
	)
	assert emptyArtists is not None and len(emptyArtists) == 0


def test_get_artists_for_songs(
	fixture_artist_service: ArtistService,
	fixture_songartist_service: SongArtistService
):
	artistService = fixture_artist_service
	songArtistService = fixture_songartist_service

	songArtists = list(songArtistService.get_song_artists(songIds=17))

	assert songArtists
	assert len(songArtists) == 5
	artists = sorted(artistService.get_artists(
			artistKeys=(sa.artistid or 0 for sa in songArtists)
	), key=lambda a: a.id or 0)

	assert len(artists) == 5
	assert artists[0].name == "bravo_artist"
	assert artists[1].name == "echo_artist"
	assert artists[2].name == "foxtrot_artist"
	assert artists[3].name == "juliet_artist"
	assert artists[4].name == "kilo_artist"

	songArtists = list(songArtistService.get_song_artists(songIds=[8, 1]))
	assert songArtists

	assert len(songArtists) == 3

	artists = sorted(artistService.get_artists(
			artistKeys=(sa.artistid or 0 for sa in songArtists)
	), key=lambda a: a.id or 0)

	assert artists and len(artists) == 3
	assert artists[0].name == "delta_artist"
	assert artists[1].name == "echo_artist"
	assert artists[2].name == "foxtrot_artist"


@pytest.mark.current_username("testUser_november")
def test_get_single_song_for_edit(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([1]))
	assert songInfo

	assert songInfo.treepath == "foo/goo/boo/sierra"
	assert songInfo.name == "sierra_song"
	assert songInfo.album and songInfo.album.id == 11
	assert songInfo.album and songInfo.album.name == "boo_album"
	assert songInfo.artists and len(songInfo.artists) == 1
	sortedArtists = sorted(songInfo.artists, key=lambda a: a.id or 0)
	assert len(sortedArtists) == 1
	assert sortedArtists[0].id == 4
	assert sortedArtists[0].name == "delta_artist"
	assert songInfo.primaryartist
	if songInfo.primaryartist:
		assert songInfo.primaryartist.id == 6
		assert songInfo.primaryartist.name == "foxtrot_artist"
	assert not songInfo.covers or len(songInfo.covers) == 0
	assert songInfo.track == "1"
	assert songInfo.discnum == 1
	assert songInfo.genre == "pop"
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 2
		assert sortedStations[0].name == "papa_station"
		assert sortedStations[0].displayname == "Come to papa"

		assert sortedStations[1].id == 6
		assert sortedStations[1].name == "yankee_station"
		assert sortedStations[1].displayname == "Blurg the blergos"


@pytest.mark.current_username("testUser_november")
def test_get_song_for_edit_without_stations(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([39]))
	assert songInfo
	assert songInfo.name == "foxtrot2_song"
	assert songInfo.stations != None and len(songInfo.stations) == 0

@pytest.mark.current_username("testUser_november")
def test_get_song_for_edit_without_artists(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoService = fixture_song_info_service
	songInfo = next(songInfoService.get_songs_for_edit([58]))
	assert songInfo
	assert songInfo.name == "alpha4_song"
	assert songInfo.artists != None and len(songInfo.artists) == 0


@pytest.mark.current_username("testUser_november")
def test_get_song_for_edit_without_album(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfo = next(songInfoService.get_songs_for_edit([27]))
	assert songInfo
	assert songInfo.name == "tango2_song"
	assert songInfo.album == None


@pytest.mark.current_username("testUser_november")
def test_get_multiple_songs_for_edit(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoList = sorted(songInfoService.get_songs_for_edit([1, 17]),
		key=lambda s: s.id
	)
	assert songInfoList and len(songInfoList) == 2
	songInfo = songInfoList[0]
	assert songInfo.treepath == "foo/goo/boo/sierra"
	assert songInfo.name == "sierra_song"
	assert songInfo.album and songInfo.album.id == 11
	assert songInfo.album and songInfo.album.name == "boo_album"
	assert songInfo.artists and len(songInfo.artists) == 1
	sortedArtists = sorted(songInfo.artists, key=lambda a: a.id or 0)
	assert len(sortedArtists) == 1
	assert sortedArtists[0].id == 4
	assert sortedArtists[0].name == "delta_artist"
	assert songInfo.primaryartist
	if songInfo.primaryartist:
		assert songInfo.primaryartist.id == 6
		assert songInfo.primaryartist.name == "foxtrot_artist"
	assert not songInfo.covers or len(songInfo.covers) == 0
	assert songInfo.track == "1"
	assert songInfo.discnum == 1
	assert songInfo.genre == "pop"
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 2
		assert sortedStations[0].name == "papa_station"
		assert sortedStations[0].displayname == "Come to papa"

		assert sortedStations[1].id == 6
		assert sortedStations[1].name == "yankee_station"
		assert sortedStations[1].displayname == "Blurg the blergos"

	songInfo = songInfoList[1]
	assert songInfo.treepath == "foo/goo/shoo/india"
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
	assert not songInfo.primaryartist
	assert not songInfo.covers or len(songInfo.covers) == 0
	assert songInfo.track == "2"
	assert songInfo.discnum == 1
	assert not songInfo.genre
	assert songInfo.stations and len(songInfo.stations) == 2
	sortedStations = sorted(songInfo.stations, key=lambda t: t.id or 0)
	if songInfo.stations:
		assert sortedStations[0].id == 1
		assert sortedStations[0].name == "oscar_station"
		assert sortedStations[0].displayname == "Oscar the grouch"

		assert sortedStations[1].id == 3
		assert sortedStations[1].name == "romeo_station"
		assert sortedStations[1].displayname == "But soft, what yonder wind breaks"

@pytest.mark.current_username("testUser_november")
def test_get_multiple_songs_for_edit2(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_november") #random user
	assert user
	songInfoList = sorted(songInfoService.get_songs_for_edit([2, 3]),
		key=lambda s: s.id
	)
	assert len(songInfoList) == 2

@pytest.mark.current_username("testUser_november")
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
		),
		key=lambda s: s.id
	)

	assert len(songInfoList) == 2
	assert songInfoList[0].id == 1
	assert songInfoList[1].id == 6

@pytest.mark.current_username("testUser_november")
def test_get_song_with_owner_info(
	fixture_song_info_service: SongInfoService,
	fixture_account_service: AccountsService
):
	songInfoService = fixture_song_info_service
	accountService = fixture_account_service
	user,_ = accountService.get_account_for_login("testUser_romeo") #random user
	assert user
	results = next(songInfoService.get_songs_for_edit([59]))
	album = results.album
	assert album
	albumOwner = album.owner
	assert albumOwner.displayname == "julietDisplay"
	albumArtist = album.albumartist
	assert albumArtist
	albumArtistOwner = albumArtist.owner
	assert albumArtistOwner
	assert albumArtistOwner.username == "testUser_kilo"
	primaryArtist = results.primaryartist
	assert primaryArtist
	primaryArtistOwner = primaryArtist.owner
	assert primaryArtistOwner
	assert primaryArtistOwner.username == "testUser_november"
	assert results.artists
	assert len(results.artists) == 2
	artsit0Owner = results.artists[0].owner
	assert artsit0Owner.displayname == "IndiaDisplay"
	artsit1Owner = results.artists[1].owner
	assert artsit1Owner.username == "testUser_hotel"
	assert results.stations
	assert len(results.stations) == 2
	station0Owner = results.stations[0].owner
	assert station0Owner
	assert station0Owner.username == "testUser_bravo"
	station1Owner = results.stations[1].owner
	assert station1Owner
	assert station1Owner.displayname == "julietDisplay"

@pytest.mark.current_username("testUser_november")
def test_get_all_songs(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_all_songs(
		queryParams=SimpleQueryParameters(limit=30)
	))
	assert songs

@pytest.mark.current_username("testUser_november")
def test_get_all_songs_songless_artist(
	fixture_song_info_service: SongInfoService
):
	songInfoService = fixture_song_info_service
	songs = list(songInfoService.get_all_songs(
		queryParams=SimpleQueryParameters(limit=30),
		artistId=28
	))
	assert songs == []