from datetime import datetime
from typing import List
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.tables import \
	artists, \
	albums, \
	songs, \
	song_artist, \
	tags,\
	songs_tags, \
	stations, \
	stations_tags, \
	users
from sqlalchemy import insert

def populate_artists(conn: Connection):
	artistParams = [
		{ "pk": 1, "name": "alpha_artist" },
		{ "pk": 2, "name": "bravo_artist" },
		{ "pk": 3, "name": "charlie_artist" },
		{ "pk": 4, "name": "delta_artist" },
		{ "pk": 5, "name": "echo_artist" },
		{ "pk": 6, "name": "foxtrot_artist" },
		{ "pk": 7, "name": "golf_artist" }
	]
	stmt = insert(artists)
	conn.execute(stmt, artistParams) #pyright: ignore [reportUnknownMemberType]

def populate_albums(conn: Connection):
  albumParams = [
		{ "pk": 1, "name": "broo_album", "albumArtistFk": 7, "year": 2001 },
		{ "pk": 2, "name": "moo_album", "albumArtistFk": 7, "year": 2003 },
		{ "pk": 8, "name": "shoo_album", "albumArtistFk": 6, "year": 2003 },
		{ "pk": 9, "name": "who_2_album", "albumArtistFk": 6, "year": 2001 },
		{ "pk": 10, "name": "who_1_album", "albumArtistFk": 5, "year": 2001 },
		{ "pk": 11, "name": "boo_album", "albumArtistFk": 4, "year": 2001 },
	]
  stmt = insert(albums)
  conn.execute(stmt, albumParams) #pyright: ignore [reportUnknownMemberType]
  albumParams2 = [
		{ "pk": 4, "name": "soo_album", "year": 2004 },
		{ "pk": 7, "name": "koo_album", "year": 2010 },
	]
  conn.execute(stmt, albumParams2) #pyright: ignore [reportUnknownMemberType]
  albumParams3 = [
		{ "pk": 5, "name": "doo_album" },
		{ "pk": 6, "name": "roo_album" },
	]
  conn.execute(stmt, albumParams3) #pyright: ignore [reportUnknownMemberType]
  albumParams4 = [
		{ "pk": 3, "name": "juliet_album", "albumArtistFk": 7 }
	]
  conn.execute(stmt, albumParams4) #pyright: ignore [reportUnknownMemberType]

def populate_songs(conn: Connection):
	songParams = [
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
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 4,
			"path": "foo/goo/boo/victor",
			"name": "victor_song",
			"albumFk": 11,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 5,
			"path": "foo/goo/boo/victor_2",
			"name": "victor_song",
			"albumFk": 11,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
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
			"comment": "Kazoos make good swimmers"
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
			"comment": "Kazoos make good swimmers"
		},
		{ "pk": 11,
			"path": "foo/goo/who_2/bravo",
			"name": "bravo_song",
			"albumFk": 9,
			"track": 1,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
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
	]
	stmt = insert(songs)

	songParams1 = list(filter(lambda s: \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, songParams))
	conn.execute(stmt, songParams1) #pyright: ignore [reportUnknownMemberType]
	songParams2 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		'comment' in s, songParams))
	conn.execute(stmt, songParams2) #pyright: ignore [reportUnknownMemberType]
	songParams3 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, songParams))
	conn.execute(stmt, songParams3) #pyright: ignore [reportUnknownMemberType]
	songParams4 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams4) #pyright: ignore [reportUnknownMemberType]
	songParams5 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams5) #pyright: ignore [reportUnknownMemberType]
	songParams6 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams6) #pyright: ignore [reportUnknownMemberType]s
	songParams7 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams7) #pyright: ignore [reportUnknownMemberType]
	songParams8 = list(filter(lambda s: \
		not 'explicit' in s and \
		not 'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams8) #pyright: ignore [reportUnknownMemberType]
	songParams9 = list(filter(lambda s: \
		'explicit' in s and \
		'albumFk' in s and \
		not 'track' in s and \
		not 'disc' in s and \
		'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams9) #pyright: ignore [reportUnknownMemberType]
	songParams10 = list(filter(lambda s: \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams10) #pyright: ignore [reportUnknownMemberType]
	songParams11 = list(filter(lambda s: \
		'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		not 'comment' in s, songParams))
	conn.execute(stmt, songParams11) #pyright: ignore [reportUnknownMemberType]
	songParams12 = list(filter(lambda s: \
		not 'explicit' in s and \
		'albumFk' in s and \
		'track' in s and \
		not 'disc' in s and \
		not 'genre' in s and \
		not 'bitrate' in s and \
		'comment' in s, songParams))
	conn.execute(stmt, songParams12) #pyright: ignore [reportUnknownMemberType]

def populate_songs_artists(conn: Connection):
	songArtistParams = [
		{ "songFk": 40, "artistFk": 7 },
		{ "songFk": 39, "artistFk": 7 },
		{ "songFk": 38, "artistFk": 7 },
		{ "songFk": 37, "artistFk": 7 },
		{ "songFk": 36, "artistFk": 2 },
		{ "songFk": 35, "artistFk": 1 },
		{ "songFk": 34, "artistFk": 3 },
		{ "songFk": 33, "artistFk": 4 },
		{ "songFk": 32, "artistFk": 4 },
		{ "songFk": 31, "artistFk": 5 },
		{ "songFk": 30, "artistFk": 5 },
		{ "songFk": 29, "artistFk": 6 },
		{ "songFk": 28, "artistFk": 6 },
		{ "songFk": 27, "artistFk": 6 },
		{ "songFk": 26, "artistFk": 6 },
		{ "songFk": 25, "artistFk": 6 },
		{ "songFk": 24, "artistFk": 6 },
		{ "songFk": 23, "artistFk": 6 },
		{ "songFk": 22, "artistFk": 2 },
		{ "songFk": 21, "artistFk": 2 },
		{ "songFk": 20, "artistFk": 2 },
		{ "songFk": 19, "artistFk": 6 },
		{ "songFk": 18, "artistFk": 6 },
		{ "songFk": 17, "artistFk": 6 },
		{ "songFk": 16, "artistFk": 6 },
		{ "songFk": 15, "artistFk": 6 },
		{ "songFk": 14, "artistFk": 6 },
		{ "songFk": 13, "artistFk": 6 },
		{ "songFk": 12, "artistFk": 6 },
		{ "songFk": 11, "artistFk": 6 },
		{ "songFk": 10, "artistFk": 5 },
		{ "songFk": 9, "artistFk": 5 },
		{ "songFk": 8, "artistFk": 5 },
		{ "songFk": 7, "artistFk": 5 },
		{ "songFk": 6, "artistFk": 5 },
		{ "songFk": 5, "artistFk": 4 },
		{ "songFk": 4, "artistFk": 4 },
		{ "songFk": 3, "artistFk": 4 },
		{ "songFk": 2, "artistFk": 4 },
		{ "songFk": 1, "artistFk": 4 },
	]
	stmt = insert(song_artist)
	conn.execute(stmt, songArtistParams) #pyright: ignore [reportUnknownMemberType]
	songArtistParams2 = [
		{ "songFk": 43, "artistFk": 7, "isPrimaryArtist": 1 },
		{ "songFk": 42, "artistFk": 7, "isPrimaryArtist": 1 },
		{ "songFk": 41, "artistFk": 7, "isPrimaryArtist": 1 },
	]
	conn.execute(stmt, songArtistParams2) #pyright: ignore [reportUnknownMemberType]

def populate_tags(conn: Connection):
	tagsParams = [
		{ "pk": 1, "name": "kilo_tag" },
		{ "pk": 2, "name": "lima_tag" },
		{ "pk": 3, "name": "mike_tag" },
		{ "pk": 4, "name": "november_tag" },
	]
	stmt = insert(tags)
	conn.execute(stmt, tagsParams) #pyright: ignore [reportUnknownMemberType]

def populate_songs_tags(conn: Connection):
	songTagParams = [
		{ "songFk": 43, "tagFk": 1 },
		{ "songFk": 43, "tagFk": 2 },
		{ "songFk": 43, "tagFk": 3 },
		{ "songFk": 41, "tagFk": 2 },
		{ "songFk": 40, "tagFk": 2 },
		{ "songFk": 38, "tagFk": 2 },
		{ "songFk": 37, "tagFk": 2 },
		{ "songFk": 36, "tagFk": 3 },
		{ "songFk": 35, "tagFk": 4 },
		{ "songFk": 34, "tagFk": 3 },
		{ "songFk": 33, "tagFk": 4 },
		{ "songFk": 32, "tagFk": 4 },
		{ "songFk": 31, "tagFk": 2 },
		{ "songFk": 30, "tagFk": 1 },
		{ "songFk": 29, "tagFk": 1 },
		{ "songFk": 28, "tagFk": 1 },
		{ "songFk": 27, "tagFk": 3 },
		{ "songFk": 26, "tagFk": 3 },
		{ "songFk": 25, "tagFk": 3 },
		{ "songFk": 24, "tagFk": 3 },
		{ "songFk": 23, "tagFk": 1 },
		{ "songFk": 22, "tagFk": 2 },
		{ "songFk": 21, "tagFk": 1 },
		{ "songFk": 20, "tagFk": 2 },
		{ "songFk": 19, "tagFk": 1 },
		{ "songFk": 18, "tagFk": 1 },
		{ "songFk": 17, "tagFk": 1 },
		{ "songFk": 17, "tagFk": 3 },
		{ "songFk": 16, "tagFk": 3 },
		{ "songFk": 15, "tagFk": 4 },
		{ "songFk": 14, "tagFk": 4 },
		{ "songFk": 13, "tagFk": 4 },
		{ "songFk": 12, "tagFk": 1 },
		{ "songFk": 11, "tagFk": 3 },
		{ "songFk": 10, "tagFk": 2 },
		{ "songFk": 9, "tagFk": 1 },
		{ "songFk": 8, "tagFk": 2 },
		{ "songFk": 7, "tagFk": 1 },
		{ "songFk": 6, "tagFk": 3 },
		{ "songFk": 5, "tagFk": 2 },
		{ "songFk": 4, "tagFk": 4 },
		{ "songFk": 3, "tagFk": 1 },
		{ "songFk": 2, "tagFk": 1 },
		{ "songFk": 1, "tagFk": 2 },
	]
	stmt = insert(songs_tags)
	conn.execute(stmt, songTagParams) #pyright: ignore [reportUnknownMemberType]

def populate_stations(conn: Connection):
	stationParams = [
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
		}
	]
	stmt = insert(stations)
	conn.execute(stmt, stationParams) #pyright: ignore [reportUnknownMemberType]

def populate_station_tags(conn: Connection):
	stationTagsParams = [
		{ "stationFk": 1, "tagFk": 2 },
		{ "stationFk": 1, "tagFk": 4 },
	]
	stmt = insert(stations_tags)
	conn.execute(stmt, stationTagsParams) #pyright: ignore [reportUnknownMemberType]

def populate_users(
	conn: Connection,
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
):
	usersParams = [
		{
			"pk": primaryUser.id,
			"userName": primaryUser.userName,
			"displayName": None,
			"hashedPW": primaryUser.hash,
			"email": primaryUser.email,
			"isActive": 1,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk": 2,
			"userName": "testUser_bravo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test2@test.com",
			"isActive": 1,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 3,
			"userName": "testUser_charlie",
			"displayName": None,
			"hashedPW": None,
			"email": "test3@test.com",
			"isActive": 1,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 4,
			"userName": "testUser_delta",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test4@test.com",
			"isActive": 0,
			"creationTimestamp": orderedTestDates[1].timestamp()
		},
		{
			"pk": 5,
			"userName": "testUser_echo",
			"displayName": None,
			"hashedPW": None,
			"email": None,
			"isActive": 1,
			"creationTimestamp": orderedTestDates[1].timestamp()
		}
	]
	stmt = insert(users)
	conn.execute(stmt, usersParams) #pyright: ignore [reportUnknownMemberType]