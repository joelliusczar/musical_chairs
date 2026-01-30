from datetime import datetime, timezone
from typing import Any
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import (
	artists,
	albums,
	songs,
	song_artist,
	stations,
	stations_songs,
	stations_albums,
	station_queue,
	playlists,
	playlists_songs,
	stations_playlists,
)
from sqlalchemy import insert
from .db_data import (
	album_params,
	albumParams1,
	albumParams2,
	albumParams3,
	albumParams4,
	artist_params,
	song_params,
	songArtistParams,
	songArtistParams2,
	playlistsSongsParams,
	station_params,
	stationSongParams,
	station_album_params,
	playlists_params,
	stations_playlists_params,
	get_station_queue,
	get_user_params,
)
from .constant_values_defs import (
	mock_ordered_date_list,
	primary_user,
	mock_password
)



fooDirOwnerId = 11
jazzDirOwnerId = 11
blitzDirOwnerId = 11


def populate_artists(conn: Connection):
	stmt = insert(artists)
	conn.execute(stmt, artist_params)

def populate_albums(conn: Connection):
	stmt = insert(albums)
	conn.execute(stmt, albumParams1)
	conn.execute(stmt, albumParams2)
	conn.execute(stmt, albumParams3)
	conn.execute(stmt, albumParams4)

def populate_songs(conn: Connection):
	stmt = insert(songs)

	songParams1 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		"discnum" in s and \
		'genre' in s and \
		'bitrate' in s and \
		'notes' in s, song_params))
	conn.execute(stmt, songParams1)
	songParams2 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		"discnum" in s and \
		'genre' in s and \
		'bitrate' in s and \
		'notes' in s, song_params))
	conn.execute(stmt, songParams2) #pyright: ignore [reportUnknownMemberType]
	songParams3 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		"discnum" in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'notes' in s, song_params))
	conn.execute(stmt, songParams3) #pyright: ignore [reportUnknownMemberType]
	songParams4 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		"discnum" in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams4) #pyright: ignore [reportUnknownMemberType]
	songParams5 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		"discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams5) #pyright: ignore [reportUnknownMemberType]
	songParams6 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams6) #pyright: ignore [reportUnknownMemberType]s
	songParams7 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		not 'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams7) #pyright: ignore [reportUnknownMemberType]
	songParams8 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams8) #pyright: ignore [reportUnknownMemberType]
	songParams9 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		not 'track' in s and \
		not "discnum" in s and \
		'genre' in s and \
		'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams9) #pyright: ignore [reportUnknownMemberType]
	songParams14 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not "discnum" in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'notes' in s, song_params))
	conn.execute(stmt, songParams14) #pyright: ignore [reportUnknownMemberType]
	songParams10 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams10) #pyright: ignore [reportUnknownMemberType]
	songParams11 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams11) #pyright: ignore [reportUnknownMemberType]
	songParams12 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		'notes' in s, song_params))
	conn.execute(stmt, songParams12) #pyright: ignore [reportUnknownMemberType]
	songParams13 = list(filter(lambda s: \
		not 'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not "discnum" in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'notes' in s, song_params))
	conn.execute(stmt, songParams13) #pyright: ignore [reportUnknownMemberType]

def populate_songs_artists(conn: Connection):
	stmt = insert(song_artist)
	conn.execute(stmt, songArtistParams) #pyright: ignore [reportUnknownMemberType]
	conn.execute(stmt, songArtistParams2) #pyright: ignore [reportUnknownMemberType]

def populate_stations(conn: Connection):
	stmt = insert(stations)
	conn.execute(stmt, station_params) #pyright: ignore [reportUnknownMemberType]

def populate_stations_songs(conn: Connection):
	stmt = insert(stations_songs)
	conn.execute(stmt, stationSongParams) #pyright: ignore [reportUnknownMemberType]

def populate_station_albums(conn: Connection):
	stmt = insert(stations_albums)
	conn.execute(stmt, station_album_params)


def populate_station_playlists(conn: Connection):
	stmt = insert(stations_playlists)
	conn.execute(stmt, stations_playlists_params)


def populate_playlists(conn: Connection):
	stmt = insert(playlists)
	conn.execute(stmt, playlists_params) #pyright: ignore [reportUnknownMemberType]


def populate_playlists_songs(conn: Connection):
	stmt = insert(playlists_songs)
	conn.execute(stmt, playlistsSongsParams) #pyright: ignore [reportUnknownMemberType]


#don't remember why I am using using funcs to return these global variables
def get_initial_users() -> list[dict[Any, Any]]:
	userParams = get_user_params(
		mock_ordered_date_list,
		primary_user(),
		mock_password()
	)
	return userParams


def populate_station_queue(
	conn: Connection
):
	stationQueueParams = get_station_queue(datetime( #0
			year=2021,
			month=5,
			day=27,
			hour=19,
			minute=13,
			tzinfo=timezone.utc
		))
	stmt = insert(station_queue)
	conn.execute(stmt, stationQueueParams) #pyright: ignore [reportUnknownMemberType]

def get_initial_stations() -> list[dict[Any, Any]]:
	return station_params

def get_initial_playlists() -> list[dict[Any, Any]]:
	return playlists_params

def get_initial_songs() -> list[dict[Any, Any]]:
	return song_params

def get_initial_albums() -> list[dict[Any, Any]]:
	return album_params

def get_initial_artists() -> list[dict[Any, Any]]:
	return artist_params