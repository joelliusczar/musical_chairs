from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import AccountInfo, UserRoleDef
try:
	from .special_strings_reference import chinese1, irish1
except:
	#for if I try to import file from interactive
	from special_strings_reference import chinese1, irish1

fooDirOwnerId = 11
jazzDirOwnerId = 11
blitzDirOwnerId = 11

bravo_user_id = 2
charlie_user_id = 3
delta_user_id = 4
echo_user_id = 5
foxtrot_user_id = 6
golf_user_id = 7
hotel_user_id = 8
india_user_id = 9
juliet_user_id = 10
kilo_user_id = 11
lima_user_id = 12
mike_user_id = 13
november_user_id = 14
oscar_user_id = 15
papa_user_id = 16
quebec_user_id = 17

artist_params = [
	{
		"pk": 1,
		"name": "alpha_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 2,
		"name": "bravo_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 3,
		"name": "charlie_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 4,
		"name": "delta_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 5,
		"name": "echo_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 6,
		"name": "foxtrot_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 7,
		"name": "golf_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 8,
		"name": "hotel_artist",
		"ownerFk": jazzDirOwnerId,
		"lastModifiedByUserFk": jazzDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 9,
		"name": "india_artist",
		"ownerFk": jazzDirOwnerId,
		"lastModifiedByUserFk": jazzDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 10,
		"name": "juliet_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 11,
		"name": "kilo_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 12,
		"name": "lima_artist",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 13,
		"name": "november_artist",
		"ownerFk": blitzDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 14,
		"name": "oscar_artist",
		"ownerFk": blitzDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
]

albumParams1 = [
	{
		"pk": 1,
		"name": "broo_album",
		"albumArtistFk": 7,
		"year": 2001,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 2,
		"name": "moo_album",
		"albumArtistFk": 7,
		"year": 2003,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 8,
		"name": "shoo_album",
		"albumArtistFk": 6,
		"year": 2003,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 9,
		"name": "who_2_album",
		"albumArtistFk": 6,
		"year": 2001,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 10,
		"name": "who_1_album",
		"albumArtistFk": 5,
		"year": 2001,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 11,
		"name": "boo_album",
		"albumArtistFk": 4,
		"year": 2001,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
]

albumParams2 = [
	{
		"pk": 4,
		"name": "soo_album",
		"year": 2004,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 7,
		"name": "koo_album",
		"year": 2010,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 13,
		"name": "koo_album",
		"year": 2010,
		"ownerFk": jazzDirOwnerId,
		"lastModifiedByUserFk": jazzDirOwnerId,
		"lastModifiedTimestamp": 0
	},
]

albumParams3 = [
	{
		"pk": 5,
		"name": "doo_album",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 6,
		"name": "roo_album",
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 12,
		"name": "garoo_album",
		"ownerFk": blitzDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
]

albumParams4 = [
	{
		"pk": 3,
		"name": "juliet_album",
		"albumArtistFk": 7,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	}
]

album_params = [
	*albumParams1,
	*albumParams2,
	*albumParams3,
	*albumParams4
]

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

songArtistParams2 = [
	{ "pk": 41, "songFk": 43, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 42, "songFk": 42, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 43, "songFk": 41, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 44, "songFk": 1, "artistFk": 6, "isPrimaryArtist": 1 },
]

songArtistParamsAll = [*songArtistParams, *songArtistParams2]

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

def get_user_params(
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
) -> list[dict[Any, Any]]:
	global users_params
	users_params = [
		{
			"pk": primaryUser.id,
			"username": primaryUser.username,
			"displayName": None,
			"hashedPW": testPassword,
			"email": primaryUser.email,
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"dirRoot": ""
		},
		{
			"pk": bravo_user_id,
			"username": "testUser_bravo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test2@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": charlie_user_id,
			"username": "testUser_charlie",
			"displayName": None,
			"hashedPW": None,
			"email": "test3@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": delta_user_id,
			"username": "testUser_delta",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test4@test.com",
			"isDisabled": True,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": echo_user_id,
			"username": "testUser_echo",
			"displayName": None,
			"hashedPW": None,
			"email": None,
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": foxtrot_user_id,
			"username": "testUser_foxtrot",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test6@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": golf_user_id,
			"username": "testUser_golf",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test7@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": hotel_user_id,
			"username": "testUser_hotel",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test8@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": india_user_id,
			"username": "testUser_india",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test9@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": juliet_user_id,
			"username": "testUser_juliet",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test10@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": kilo_user_id,
			"username": "testUser_kilo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test11@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "/foo"
		},
		{
			"pk": lima_user_id,
			"username": "testUser_lima",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test12@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": mike_user_id,
			"username": "testUser_mike",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test13@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": november_user_id,
			"username": "testUser_november",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test14@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": oscar_user_id,
			"username": "testUser_oscar",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test15@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": papa_user_id,
			"username": "testUser_papa",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test16@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": quebec_user_id,
			"username": "testUser_quebec",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test17@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		}
	]
	return users_params

def get_user_role_params(
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
) -> list[dict[Any, Any]]:
	return [
		{
			"userFk": primaryUser.id,
			"role": UserRoleDef.ADMIN.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": bravo_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": charlie_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": delta_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": delta_user_id,
			"role": UserRoleDef.SONG_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": foxtrot_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": golf_user_id,
			"role": f"name={UserRoleDef.USER_LIST.value}",
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": juliet_user_id,
			"role": UserRoleDef.STATION_EDIT(),
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": quebec_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":300,
			"count":15,
			"priority": None
		}
	]

def get_station_permission_params(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:
	return [
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

def get_path_permission_params(
	orderedTestDates: List[datetime]
)  -> list[dict[Any, Any]]:
	return [
		{
			"pk":1,
			"userFk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":2,
			"userFk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":3,
			"userFk": kilo_user_id,
			"path": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userFk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":5,
			"userFk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
	]

