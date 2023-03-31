from datetime import datetime
from typing import List, Any
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import AccountInfo, UserRoleDef
from musical_chairs_libs.tables import (
	artists,
	albums,
	songs,
	song_artist,
	stations,
	users,
	userRoles,
	stations_songs,
	station_user_permissions,
	path_user_permissions
)
from sqlalchemy import insert
from .special_strings_reference import chinese1, irish1



def populate_artists(conn: Connection):
	global artist_params
	artist_params = [
		{ "pk": 1, "name": "alpha_artist" },
		{ "pk": 2, "name": "bravo_artist" },
		{ "pk": 3, "name": "charlie_artist" },
		{ "pk": 4, "name": "delta_artist" },
		{ "pk": 5, "name": "echo_artist" },
		{ "pk": 6, "name": "foxtrot_artist" },
		{ "pk": 7, "name": "golf_artist" },
		{ "pk": 8, "name": "hotel_artist" },
		{ "pk": 9, "name": "india_artist" },
		{ "pk": 10, "name": "juliet_artist" },
		{ "pk": 11, "name": "kilo_artist" },
		{ "pk": 12, "name": "lima_artist" },
		{ "pk": 13, "name": "november_artist" },
		{ "pk": 14, "name": "oscar_artist" },
	]
	stmt = insert(artists)
	conn.execute(stmt, artist_params) #pyright: ignore [reportUnknownMemberType]

def populate_albums(conn: Connection):
	global album_params
	albumParams1 = [
		{ "pk": 1, "name": "broo_album", "albumArtistFk": 7, "year": 2001 },
		{ "pk": 2, "name": "moo_album", "albumArtistFk": 7, "year": 2003 },
		{ "pk": 8, "name": "shoo_album", "albumArtistFk": 6, "year": 2003 },
		{ "pk": 9, "name": "who_2_album", "albumArtistFk": 6, "year": 2001 },
		{ "pk": 10, "name": "who_1_album", "albumArtistFk": 5, "year": 2001 },
		{ "pk": 11, "name": "boo_album", "albumArtistFk": 4, "year": 2001 },
	]
	stmt = insert(albums)
	conn.execute(stmt, albumParams1) #pyright: ignore [reportUnknownMemberType]
	album_params = albumParams1
	albumParams2 = [
		{ "pk": 4, "name": "soo_album", "year": 2004 },
		{ "pk": 7, "name": "koo_album", "year": 2010 },
	]
	conn.execute(stmt, albumParams2) #pyright: ignore [reportUnknownMemberType]
	album_params.extend(albumParams2)
	albumParams3 = [
		{ "pk": 5, "name": "doo_album" },
		{ "pk": 6, "name": "roo_album" },
		{ "pk": 12, "name": "garoo_album" },
	]
	conn.execute(stmt, albumParams3) #pyright: ignore [reportUnknownMemberType]
	album_params.extend(albumParams3)
	albumParams4 = [
		{ "pk": 3, "name": "juliet_album", "albumArtistFk": 7 }
	]
	conn.execute(stmt, albumParams4) #pyright: ignore [reportUnknownMemberType]
	album_params.extend(albumParams4)

def populate_songs(conn: Connection):
	global song_params
	song_params = [
		{ "pk": 1,
			"path": "foo/goo/boo/sierra",
			"name": "sierra_song",
			"albumFk": 11,
			"track": 1,
			"disc": 1,
			"genre": "pop",
			"explicit": 0,
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 2,
			"path": "foo/goo/boo/tango",
			"name": "tango_song",
			"albumFk": 11,
			"track": 2,
			"disc": 1,
			"genre": "pop",
			"explicit": 0,
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 3,
			"path": "foo/goo/boo/uniform",
			"name": "uniform_song",
			"albumFk": 11,
			"track": 3,
			"disc": 1,
			"genre": "pop",
			"explicit": 1,
			"bitrate": 144,
			"comment": "Kazoos make good parrallel parkers"
		},
		{ "pk": 4,
			"path": "foo/goo/boo/victor",
			"name": "victor_song",
			"albumFk": 11,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make bad swimmers"
		},
		{ "pk": 5,
			"path": "foo/goo/boo/victor_2",
			"name": "victor_song",
			"albumFk": 11,
			"track": 5,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make good hood rats"
		},
		{ "pk": 6,
			"path": "foo/goo/who_1/whiskey",
			"name": "whiskey_song",
			"albumFk": 10,
			"track": 1,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 7,
			"path": "foo/goo/who_1/xray",
			"name": "xray_song",
			"albumFk": 10,
			"track": 2,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 8,
			"path": "foo/goo/who_1/yankee",
			"name": "yankee_song",
			"albumFk": 10,
			"track": 3,
			"disc": 1,
			"genre": "pop",
			"comment": "guitars make good swimmers"
		},
		{ "pk": 9,
			"path": "foo/goo/who_1/zulu",
			"name": "zulu_song",
			"albumFk": 10,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 10,
			"path": "foo/goo/who_1/alpha",
			"name": "alpha_song",
			"albumFk": 10,
			"track": 5,
			"disc": 1,
			"genre": "pop",
			"comment": "hotdogs make good lava swimmers"
		},
		{ "pk": 11,
			"path": "foo/goo/who_2/bravo",
			"name": "bravo_song",
			"albumFk": 9,
			"track": 1,
			"disc": 2,
			"genre": "pop",
			"comment": "hamburgers make flat swimmers"
		},
		{ "pk": 12,
			"path": "foo/goo/who_2/charlie",
			"name": "charlie_song",
			"albumFk": 9,
			"track": 2,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 13,
			"path": "foo/goo/who_2/delta",
			"name": "delta_song",
			"albumFk": 9,
			"track": 3,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 14,
			"path": "foo/goo/who_2/foxtrot",
			"name": "foxtrot_song",
			"albumFk": 9,
			"track": 4,
			"disc": 2,
			"genre": "pop",
		},
		{ "pk": 15,
			"path": "foo/goo/who_2/golf",
			"name": "golf_song",
			"albumFk": 9,
			"track": 5,
			"disc": 2,
			"genre": "pop",
		},
		{ "pk": 16,
			"path": "foo/goo/shoo/hotel",
			"name": "hotel_song",
			"albumFk": 8,
			"track": 1,
			"disc": 1,
		},
		{ "pk": 17,
			"path": "foo/goo/shoo/india",
			"name": "india_song",
			"albumFk": 8,
			"track": 2,
			"disc": 1,
		},
		{ "pk": 18,
			"path": "foo/goo/shoo/juliet",
			"name": "juliet_song",
			"albumFk": 8,
			"track": 3,
			"disc": 1,
		},
		{ "pk": 19,
			"path": "foo/goo/shoo/kilo",
			"name": "kilo_song",
			"albumFk": 8,
			"track": 4,
			"disc": 1,
		},
		{ "pk": 20,
			"path": "foo/goo/koo/lima",
			"name": "lima_song",
			"albumFk": 7,
			"track": 1,
		},
		{ "pk": 21,
			"path": "foo/goo/koo/mike",
			"name": "mike_song",
			"albumFk": 7,
			"track": 2,
		},
		{ "pk": 22,
			"path": "foo/goo/koo/november",
			"name": "november_song",
			"albumFk": 7,
			"track": 3,
		},
		{ "pk": 23,
			"path": "foo/goo/roo/oscar",
			"name": "oscar_song",
			"albumFk": 6,
		},
		{ "pk": 24,
			"path": "foo/goo/roo/papa",
			"name": "papa_song",
			"albumFk": 6,
		},
		{ "pk": 25,
			"path": "foo/goo/roo/romeo",
			"name": "romeo_song",
			"albumFk": 6,
		},
		{ "pk": 26,
			"path": "foo/goo/roo/sierra2",
			"name": "sierra2_song",
			"albumFk": 6,
		},
		{ "pk": 27,
			"path": "foo/goo/roo/tango2",
			"name": "tango2_song",
		},
		{ "pk": 28,
			"path": "foo/goo/roo/uniform2",
			"name": "uniform2_song",
		},
		{ "pk": 29,
			"path": "foo/goo/roo/victor2",
			"name": "victor2_song",
			"albumFk": 4,
		},
		{ "pk": 30,
			"path": "foo/goo/roo/whiskey2",
			"name": "whiskey2_song",
		},
		{ "pk": 31,
			"path": "foo/goo/roo/xray2",
			"name": "xray2_song",
		},
		{ "pk": 32,
			"path": "foo/goo/doo/yankee2",
			"name": "yankee2_song",
			"albumFk": 5,
			"genre": "bop",
			"explicit": 0,
			"bitrate": 121,
		},
		{ "pk": 33,
			"path": "foo/goo/doo/zulu2",
			"name": "zulu2_song",
			"albumFk": 5,
			"genre": "bop",
			"explicit": 1,
			"bitrate": 121,
		},
		{ "pk": 34,
			"path": "foo/goo/soo/alpha2",
			"name": "alpha2_song",
			"albumFk": 4,
			"track": 1,
			"explicit": 1,
			"bitrate": 121,
		},
		{ "pk": 35,
			"path": "foo/goo/soo/bravo2",
			"name": "bravo2_song",
			"albumFk": 4,
			"track": 2,
			"explicit": 1,
		},
		{ "pk": 36,
			"path": "foo/goo/soo/charlie2",
			"name": "charlie2_song",
			"albumFk": 4,
			"track": 3,
			"comment": "Boot 'n' scoot"
		},
		{ "pk": 37,
			"path": "foo/goo/moo/delta2",
			"name": "delta2_song",
			"albumFk": 2,
			"track": 1,
		},
		{ "pk": 38,
			"path": "foo/goo/moo/echo2",
			"name": "echo2_song",
			"albumFk": 2,
			"track": 2,
		},
		{ "pk": 39,
			"path": "foo/goo/moo/foxtrot2",
			"name": "foxtrot2_song",
			"albumFk": 2,
			"track": 3,
		},
		{ "pk": 40,
			"path": "foo/goo/moo/golf2",
			"name": "golf2_song",
			"albumFk": 2,
			"track": 4,
		},
		{ "pk": 41,
			"path": "foo/goo/broo/hotel2",
			"name": "hotel2_song",
			"albumFk": 1,
		},
		{ "pk": 42,
			"path": "foo/goo/broo/india2",
			"name": "india2_song",
			"albumFk": 1,
		},
		{ "pk": 43,
			"path": "foo/goo/broo/juliet2",
			"name": "juliet2_song",
			"albumFk": 1,
		},
		{ "pk": 44,
			"path": "foo/rude/bog/kilo2",
		},
		{ "pk": 45,
			"path": "foo/rude/bog/lima2",
		},
		{ "pk": 46,
			"path": "foo/rude/rog/mike2",
		},
		{ "pk": 47,
			"path": "foo/rude/rog/november2",
		},
		{ "pk": 48,
			"path": "foo/rude/rog/oscar2",
		},
		{ "pk": 49,
			"path": "foo/dude/dog/papa2",
		},
		{ "pk": 50,
			"path": "foo/bar/baz/romeo2",
			"name": chinese1,
		},
		{ "pk": 51,
			"path": "foo/bar/baz/sierra3",
			"name": irish1,
		},
		{ "pk": 52,
			"name": "tango3",
			"path": "jazz/rude/rog/tango3",
		},
		{ "pk": 53,
			"name": "uniform3",
			"path": "jazz/rude/rog/uniform3",
		},
		{ "pk": 54,
			"name": "victor3",
			"path": "jazz/cat/kitten/victor3",
		},
		{ "pk": 55,
			"name": "whiskey3",
			"path": "blitz/mar/wall/whiskey3",
		},
		{ "pk": 56,
			"name": "xray3",
			"path": "blitz/mar/wall/xray3",
		},
		{ "pk": 57,
			"name": "zulu3",
			"path": "blitz/rhino/rhina/zulu3",
		},
		{ "pk": 58,
			"name": "alpha4_song",
			"path": "jazz/lurk/toot/alpha4_song",
			"albumFk": 7,
		},
	]
	stmt = insert(songs)

	songParams1 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams1) #pyright: ignore [reportUnknownMemberType]
	songParams2 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams2) #pyright: ignore [reportUnknownMemberType]
	songParams3 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams3) #pyright: ignore [reportUnknownMemberType]
	songParams4 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams4) #pyright: ignore [reportUnknownMemberType]
	songParams5 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams5) #pyright: ignore [reportUnknownMemberType]
	songParams6 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams6) #pyright: ignore [reportUnknownMemberType]s
	songParams7 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams7) #pyright: ignore [reportUnknownMemberType]
	songParams8 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		not 'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams8) #pyright: ignore [reportUnknownMemberType]
	songParams9 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams9) #pyright: ignore [reportUnknownMemberType]
	songParams10 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams10) #pyright: ignore [reportUnknownMemberType]
	songParams11 = list(filter(lambda s: \
		'name' in s and \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams11) #pyright: ignore [reportUnknownMemberType]
	songParams12 = list(filter(lambda s: \
		'name' in s and \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, song_params))
	conn.execute(stmt, songParams12) #pyright: ignore [reportUnknownMemberType]
	songParams13 = list(filter(lambda s: \
		not 'name' in s and \
		not 'explicit' in s and \
		not 'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, song_params))
	conn.execute(stmt, songParams13) #pyright: ignore [reportUnknownMemberType]

def populate_songs_artists(conn: Connection):
	songArtistParams = [
		{ "pk": 1, "songFk": 40, "artistFk": 7 },
		{ "pk": 2, "songFk": 39, "artistFk": 7 },
		{ "pk": 3, "songFk": 38, "artistFk": 7 },
		{ "pk": 4, "songFk": 37, "artistFk": 7 },
		{ "pk": 5, "songFk": 36, "artistFk": 2 },
		{ "pk": 6, "songFk": 35, "artistFk": 1 },
		{ "pk": 7, "songFk": 34, "artistFk": 3 },
		{ "pk": 8, "songFk": 33, "artistFk": 4 },
		{ "pk": 9, "songFk": 32, "artistFk": 4 },
		{ "pk": 10, "songFk": 31, "artistFk": 5 },
		{ "pk": 11, "songFk": 30, "artistFk": 5 },
		{ "pk": 12, "songFk": 29, "artistFk": 6 },
		{ "pk": 13, "songFk": 28, "artistFk": 6 },
		{ "pk": 14, "songFk": 27, "artistFk": 6 },
		{ "pk": 15, "songFk": 26, "artistFk": 6 },
		{ "pk": 16, "songFk": 25, "artistFk": 6 },
		{ "pk": 17, "songFk": 24, "artistFk": 6 },
		{ "pk": 18, "songFk": 23, "artistFk": 6 },
		{ "pk": 19, "songFk": 22, "artistFk": 2 },
		{ "pk": 20, "songFk": 21, "artistFk": 2 },
		{ "pk": 21, "songFk": 20, "artistFk": 2 },
		{ "pk": 22, "songFk": 19, "artistFk": 6 },
		{ "pk": 23, "songFk": 18, "artistFk": 6 },
		{ "pk": 24, "songFk": 17, "artistFk": 6 },
		{ "pk": 25, "songFk": 16, "artistFk": 6 },
		{ "pk": 26, "songFk": 15, "artistFk": 6 },
		{ "pk": 27, "songFk": 14, "artistFk": 6 },
		{ "pk": 28, "songFk": 13, "artistFk": 6 },
		{ "pk": 29, "songFk": 12, "artistFk": 6 },
		{ "pk": 30, "songFk": 11, "artistFk": 6 },
		{ "pk": 31, "songFk": 10, "artistFk": 5 },
		{ "pk": 32, "songFk": 9, "artistFk": 5 },
		{ "pk": 33, "songFk": 8, "artistFk": 5 },
		{ "pk": 34, "songFk": 7, "artistFk": 5 },
		{ "pk": 35, "songFk": 6, "artistFk": 5 },
		{ "pk": 36, "songFk": 5, "artistFk": 4 },
		{ "pk": 37, "songFk": 4, "artistFk": 4 },
		{ "pk": 38, "songFk": 3, "artistFk": 4 },
		{ "pk": 39, "songFk": 2, "artistFk": 4 },
		{ "pk": 40, "songFk": 1, "artistFk": 4 },
		{ "pk": 45, "songFk": 21, "artistFk": 4 },
		{ "pk": 46, "songFk": 21, "artistFk": 6 },
		{ "pk": 47, "songFk": 17, "artistFk": 10 },
		{ "pk": 48, "songFk": 17, "artistFk": 5 },
		{ "pk": 49, "songFk": 17, "artistFk": 2 },
		{ "pk": 50, "songFk": 17, "artistFk": 11 },
		{ "pk": 51, "songFk": 35, "artistFk": 12 },
	]
	stmt = insert(song_artist)
	conn.execute(stmt, songArtistParams) #pyright: ignore [reportUnknownMemberType]
	songArtistParams2 = [
		{ "pk": 41, "songFk": 43, "artistFk": 7, "isPrimaryArtist": 1 },
		{ "pk": 42, "songFk": 42, "artistFk": 7, "isPrimaryArtist": 1 },
		{ "pk": 43, "songFk": 41, "artistFk": 7, "isPrimaryArtist": 1 },
		{ "pk": 44, "songFk": 1, "artistFk": 6, "isPrimaryArtist": 1 },
	]
	conn.execute(stmt, songArtistParams2) #pyright: ignore [reportUnknownMemberType]

def populate_stations(conn: Connection):
	global station_params
	station_params = [
		{ "pk": 1,
			"name": "oscar_station",
			"displayName": "Oscar the grouch"
		},
		{ "pk": 2,
			"name": "papa_station",
			"displayName": "Come to papa"
		},
		{ "pk": 3,
			"name": "romeo_station",
			"displayName": "But soft, what yonder wind breaks"
		},
		{ "pk": 4,
			"name": "sierra_station",
			"displayName": "The greatest lie the devil ever told"
		},
		{ "pk": 5,
			"name": "tango_station",
			"displayName": "Nuke the whales"
		},
		{ "pk": 6,
			"name": "yankee_station",
			"displayName": "Blurg the blergos"
		},
		{ "pk": 7,
			"name": "uniform_station",
			"displayName": "Asshole at the wheel"
		},
		{ "pk": 8,
			"name": "victor_station",
			"displayName": "Fat, drunk, and stupid"
		},
		{ "pk": 9,
			"name": "whiskey_station",
			"displayName": "Chris-cross apple sauce"
		},
		{ "pk": 10,
			"name": "xray_station",
			"displayName": "Pentagular"
		}
	]
	stmt = insert(stations)
	conn.execute(stmt, station_params) #pyright: ignore [reportUnknownMemberType]

def populate_stations_songs(conn: Connection):
	stationSongParams = [
		{ "songFk": 43, "stationFk": 1 },
		{ "songFk": 43, "stationFk": 2 },
		{ "songFk": 43, "stationFk": 3 },
		{ "songFk": 41, "stationFk": 2 },
		{ "songFk": 40, "stationFk": 2 },
		{ "songFk": 38, "stationFk": 2 },
		{ "songFk": 37, "stationFk": 2 },
		{ "songFk": 36, "stationFk": 3 },
		{ "songFk": 35, "stationFk": 4 },
		{ "songFk": 34, "stationFk": 3 },
		{ "songFk": 33, "stationFk": 4 },
		{ "songFk": 32, "stationFk": 4 },
		{ "songFk": 31, "stationFk": 2 },
		{ "songFk": 30, "stationFk": 1 },
		{ "songFk": 29, "stationFk": 1 },
		{ "songFk": 28, "stationFk": 1 },
		{ "songFk": 27, "stationFk": 3 },
		{ "songFk": 26, "stationFk": 3 },
		{ "songFk": 25, "stationFk": 3 },
		{ "songFk": 24, "stationFk": 3 },
		{ "songFk": 23, "stationFk": 1 },
		{ "songFk": 22, "stationFk": 2 },
		{ "songFk": 21, "stationFk": 1 },
		{ "songFk": 20, "stationFk": 2 },
		{ "songFk": 19, "stationFk": 1 },
		{ "songFk": 18, "stationFk": 1 },
		{ "songFk": 17, "stationFk": 1 },
		{ "songFk": 17, "stationFk": 3 },
		{ "songFk": 16, "stationFk": 3 },
		{ "songFk": 15, "stationFk": 4 },
		{ "songFk": 15, "stationFk": 1 },
		{ "songFk": 14, "stationFk": 4 },
		{ "songFk": 13, "stationFk": 4 },
		{ "songFk": 12, "stationFk": 1 },
		{ "songFk": 11, "stationFk": 3 },
		{ "songFk": 10, "stationFk": 2 },
		{ "songFk": 9, "stationFk": 1 },
		{ "songFk": 8, "stationFk": 2 },
		{ "songFk": 7, "stationFk": 1 },
		{ "songFk": 6, "stationFk": 3 },
		{ "songFk": 5, "stationFk": 2 },
		{ "songFk": 4, "stationFk": 4 },
		{ "songFk": 3, "stationFk": 1 },
		{ "songFk": 2, "stationFk": 1 },
		{ "songFk": 1, "stationFk": 2 },
		{ "songFk": 1, "stationFk": 6 },
		{ "songFk": 4, "stationFk": 6 },
		{ "songFk": 50, "stationFk": 6 },
		{ "songFk": 44, "stationFk": 8 },
		{ "songFk": 45, "stationFk": 8 },
		{ "songFk": 46, "stationFk": 8 },
		{ "songFk": 47, "stationFk": 8 },
	]
	stmt = insert(stations_songs)
	conn.execute(stmt, stationSongParams) #pyright: ignore [reportUnknownMemberType]

def populate_users(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
):
	global users_params
	users_params = [
		{
			"pk": primaryUser.id,
			"username": primaryUser.username,
			"displayName": None,
			"hashedPW": testPassword,
			"email": primaryUser.email,
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk": 2,
			"username": "testUser_bravo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test2@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 3,
			"username": "testUser_charlie",
			"displayName": None,
			"hashedPW": None,
			"email": "test3@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 4,
			"username": "testUser_delta",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test4@test.com",
			"isDisabled": True,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 5,
			"username": "testUser_echo",
			"displayName": None,
			"hashedPW": None,
			"email": None,
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 6,
			"username": "testUser_foxtrot",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test6@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 7,
			"username": "testUser_golf",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test7@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 8,
			"username": "testUser_hotel",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test8@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 9,
			"username": "testUser_india",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test9@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 10,
			"username": "testUser_juliet",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test10@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 11,
			"username": "testUser_kilo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test11@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 12,
			"username": "testUser_lima",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test12@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 13,
			"username": "testUser_mike",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test13@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 14,
			"username": "testUser_november",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test14@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 15,
			"username": "testUser_oscar",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test15@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 16,
			"username": "testUser_papa",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test16@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 17,
			"username": "testUser_quebec",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test17@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp()
		}
	]
	stmt = insert(users)
	conn.execute(stmt, users_params) #pyright: ignore [reportUnknownMemberType]

def populate_user_roles(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
):
	userRoleParams = [
		{
			"userFk": primaryUser.id,
			"role": UserRoleDef.ADMIN.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 2,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 4,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 4,
			"role": UserRoleDef.SONG_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 6,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 6,
			"role": UserRoleDef.SONG_EDIT.modded_value(span=120),
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 7,
			"role": f"name={UserRoleDef.USER_LIST.value}",
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 10,
			"role": UserRoleDef.STATION_EDIT(),
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":300,
			"count":15,
			"priority": None
		}

	]
	stmt = insert(userRoles)
	conn.execute(stmt, userRoleParams) #pyright: ignore [reportUnknownMemberType]

def populate_station_permissions(
	conn: Connection,
	orderedTestDates: List[datetime],
):
	stationPermissionParams = [
		{
			"pk":1,
			"userFk": 11,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":2,
			"userFk": 12,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":3,
			"userFk": 13,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userFk": 13,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":5,
			"userFk": 14,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":10,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":6,
			"userFk": 14,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":5,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":7,
			"userFk": 15,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"count":5,
			"priority": 2,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userFk": 15,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"count":5,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":9,
			"userFk": 16,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userFk": 16,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":11,
			"userFk": 17,
			"stationFk": None,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userFk": 17,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		}
	]
	stmt = insert(station_user_permissions)
	conn.execute(stmt, stationPermissionParams) #pyright: ignore [reportUnknownMemberType]

def populate_path_permissions(
	conn: Connection,
	orderedTestDates: List[datetime],
):
	pathPermissionParams = [
		{
			"pk":1,
			"userFk": 11,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":2,
			"userFk": 11,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":3,
			"userFk": 11,
			"path": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userFk": 11,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_ITEM_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":5,
			"userFk": 11,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_ITEM_DOWNLOAD.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
	]
	stmt = insert(path_user_permissions)
	conn.execute(stmt, pathPermissionParams) #pyright: ignore [reportUnknownMemberType]

#don't remember why I am using using funcs to return these global variables
def get_initial_users() -> list[dict[Any, Any]]:
	return users_params

def get_initial_stations() -> list[dict[Any, Any]]:
	return station_params

def get_initial_songs() -> list[dict[Any, Any]]:
	return song_params

def get_initial_albums() -> list[dict[Any, Any]]:
	return album_params

def get_initial_artists() -> list[dict[Any, Any]]:
	return artist_params