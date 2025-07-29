from datetime import datetime
from typing import List, Any
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import AccountInfo
from musical_chairs_libs.tables import (
	artists,
	albums,
	songs,
	song_artist,
	stations,
	users,
	userRoles,
	stations_songs,
	stations_albums,
	station_user_permissions,
	path_user_permissions,
	user_action_history,
	station_queue
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
	station_params,
	stationSongParams,
	station_album_params,
	get_actions_history,
	get_path_permission_params,
	get_station_permission_params,
	get_station_queue,
	get_user_params,
	get_user_role_params
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
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams1)
	songParams2 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams2) #pyright: ignore [reportUnknownMemberType]
	songParams3 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams3) #pyright: ignore [reportUnknownMemberType]
	songParams4 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams4) #pyright: ignore [reportUnknownMemberType]
	songParams5 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams5) #pyright: ignore [reportUnknownMemberType]
	songParams6 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams6) #pyright: ignore [reportUnknownMemberType]s
	songParams7 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams7) #pyright: ignore [reportUnknownMemberType]
	songParams8 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams8) #pyright: ignore [reportUnknownMemberType]
	songParams9 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams9) #pyright: ignore [reportUnknownMemberType]
	songParams14 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams14) #pyright: ignore [reportUnknownMemberType]
	songParams10 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams10) #pyright: ignore [reportUnknownMemberType]
	songParams11 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams11) #pyright: ignore [reportUnknownMemberType]
	songParams12 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumfk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams12) #pyright: ignore [reportUnknownMemberType]
	songParams13 = list(filter(lambda s: \
		not 'name' in s and \
		not 'explicit' in s and \
		not 'albumfk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
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
	conn.execute(stmt,station_album_params)

def populate_users(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
):
	userParams = get_user_params(orderedTestDates, primaryUser, testPassword)
	stmt = insert(users)
	conn.execute(stmt, userParams)

def populate_user_roles(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
):
	userRoleParams = get_user_role_params(orderedTestDates, primaryUser)
	stmt = insert(userRoles)
	conn.execute(stmt, userRoleParams) #pyright: ignore [reportUnknownMemberType]

def populate_station_permissions(
	conn: Connection,
	orderedTestDates: List[datetime]
):
	stationPermissionParams = get_station_permission_params(orderedTestDates)
	stmt = insert(station_user_permissions)
	conn.execute(stmt, stationPermissionParams) #pyright: ignore [reportUnknownMemberType]

def populate_path_permissions(
	conn: Connection,
	orderedTestDates: List[datetime]
):
	pathPermissionParams = get_path_permission_params(orderedTestDates)
	stmt = insert(path_user_permissions)
	conn.execute(stmt, pathPermissionParams) #pyright: ignore [reportUnknownMemberType]

#don't remember why I am using using funcs to return these global variables
def get_initial_users() -> list[dict[Any, Any]]:
	userParams = get_user_params(
		mock_ordered_date_list,
		primary_user(),
		mock_password()
	)
	return userParams

def populate_user_actions_history(
	conn: Connection,
	orderedTestDates: List[datetime]
):
	actionsHistoryParams = get_actions_history(orderedTestDates)
	stmt = insert(user_action_history)
	conn.execute(stmt, actionsHistoryParams) #pyright: ignore [reportUnknownMemberType]

def populate_station_queue(
	conn: Connection
):
	stationQueueParams = get_station_queue()
	stmt = insert(station_queue)
	conn.execute(stmt, stationQueueParams) #pyright: ignore [reportUnknownMemberType]

def get_initial_stations() -> list[dict[Any, Any]]:
	return station_params

def get_initial_songs() -> list[dict[Any, Any]]:
	return song_params

def get_initial_albums() -> list[dict[Any, Any]]:
	return album_params

def get_initial_artists() -> list[dict[Any, Any]]:
	return artist_params