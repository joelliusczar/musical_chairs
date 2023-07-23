from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	RulePriorityLevel,
	MinItemSecurityLevel
)
try:
	from .special_strings_reference import chinese1, irish1
except:
	#for if I try to import file from interactive
	from special_strings_reference import chinese1, irish1

fooDirOwnerId = 11
jazzDirOwnerId = 11
blitzDirOwnerId = 11

bravo_user_id = 2 #no path rules
charlie_user_id = 3
delta_user_id = 4
echo_user_id = 5 #can't use. No password
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
romeo_user_id = 18 #designated no roles user
sierra_user_id = 19
tango_user_id = 20
uniform_user_id = 21
victor_user_id = 22
whiskey_user_id = 23
xray_user_id = 24
yankee_user_id = 25
zulu_user_id = 26
alice_user_id = 27
bertrand_user_id = 28
carl_user_id = 29
dan_user_id = 30
felix_user_id = 31
foxman_user_id = 32
foxtrain_user_id = 33
george_user_id = 34
hamburger_user_id = 35
horsetel_user_id = 36
ingo_user_id = 37
ned_land_user_id = 38
narlon_user_id = 39
number_user_id = 40
oomdwell_user_id = 41
paul_bear_user_id = 42
quirky_admin_user_id = 43
radical_path_user_id = 44
station_saver_user_id = 45
super_path_user_id = 46
tossed_slash_user_id = 47
unruled_station_user_id = 48


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
	{
		"pk": 15,
		"name": "papa_artist",
		"ownerFk": november_user_id,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 16,
		"name": "romeo_artist",
		"ownerFk": india_user_id,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0,
	},
	{
		"pk": 17,
		"name": "sierra_artist",
		"ownerFk": hotel_user_id,
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
	}
]

albumParams4 = [
	{
		"pk": 3,
		"name": "juliet_album",
		"albumArtistFk": golf_user_id,
		"ownerFk": fooDirOwnerId,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
	{
		"pk": 14,
		"name": "grunt_album",
		"ownerFk": juliet_user_id,
		"albumArtistFk": golf_user_id,
		"lastModifiedByUserFk": fooDirOwnerId,
		"lastModifiedTimestamp": 0
	},
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
	{ "pk": 59,
		"path": "foo/goo/looga/alpha",
		"name": "looga_alpha_song",
		"albumFk": 14,
		"track": 5,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 60,
		"path": "tossedSlash/goo/looga/alpha",
		"name": "looga_alpha_song",
		"genre": "bam",
		"comment": "Banana Soup"
	},
	{ "pk": 61,
		"path": "tossedSlash/goo/looga/bravo",
		"name": "looga_bravo_song",
		"genre": "bam",
		"comment": "Banana Soup"
	},
	{ "pk": 62,
		"path": "tossedSlash/guess/gold/jar",
		"name": "jar_song",
		"albumFk": 14,
		"track": 5,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 63,
		"path": "tossedSlash/guess/gold/bar",
		"name": "bar_song",
		"albumFk": 14,
		"track": 6,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 64,
		"path": "tossedSlash/guess/gold/run",
		"name": "run_song",
		"albumFk": 14,
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 65,
		"path": "tossedSlash/band/bun",
		"name": "bun_song",
		"albumFk": 14,
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 66,
		"path": "tossedSlash/band/hun",
		"name": "hun_song",
		"albumFk": 14,
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 67,
		"path": "tossedSlash/guess/silver/run",
		"name": "run_song",
		"albumFk": 14,
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 68,
		"path": "tossedSlash/guess/silver/plastic",
		"name": "plastic_tune",
		"albumFk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": 69,
		"path": "tossedSlash/guess/silver/salt",
		"name": "salt_tune",
		"albumFk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": 70,
		"path": "tossedSlash/guess/silver/green",
		"name": "green_tune",
		"albumFk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	}
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
	{ "pk": 52, "songFk": 59, "artistFk": 16 },
	{ "pk": 54, "songFk": 59, "artistFk": 17 },
]

songArtistParams2 = [
	{ "pk": 41, "songFk": 43, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 42, "songFk": 42, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 43, "songFk": 41, "artistFk": 7, "isPrimaryArtist": 1 },
	{ "pk": 44, "songFk": 1, "artistFk": 6, "isPrimaryArtist": 1 },
	{ "pk": 53, "songFk": 59, "artistFk": 15, "isPrimaryArtist": 1 },
]

songArtistParamsAll = [*songArtistParams, *songArtistParams2]

station_params = [
	{ "pk": 1,
		"name": "oscar_station",
		"displayName": "Oscar the grouch",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 2,
		"name": "papa_station",
		"displayName": "Come to papa",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 3,
		"name": "romeo_station",
		"displayName": "But soft, what yonder wind breaks",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 4,
		"name": "sierra_station",
		"displayName": "The greatest lie the devil ever told",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 5,
		"name": "tango_station",
		"displayName": "Nuke the whales",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 6,
		"name": "yankee_station",
		"displayName": "Blurg the blergos",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 7,
		"name": "uniform_station",
		"displayName": "Asshole at the wheel",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 8,
		"name": "victor_station",
		"displayName": "Fat, drunk, and stupid",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 9,
		"name": "whiskey_station",
		"displayName": "Chris-cross apple sauce",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 10,
		"name": "xray_station",
		"displayName": "Pentagular",
		"ownerFk": bravo_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 11,
		"name": "zulu_station",
		"displayName": "Hammer time",
		"ownerFk": juliet_user_id,
		"viewSecurityLevel": None
	},
	{ "pk": 12,
		"name": "alpha_station_rerun",
		"displayName": "We rerun again and again",
		"ownerFk": victor_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.RULED_USER.value
	},
	{ "pk": 13,
		"name": "bravo_station_rerun",
		"displayName": "We rerun again and again",
		"ownerFk": victor_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.ANY_USER.value
	},
	{ "pk": 14,
		"name": "charlie_station_rerun",
		"displayName": "The Wide World of Sports",
		"ownerFk": victor_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 15,
		"name": "delta_station_rerun",
		"displayName": "Dookie Dan strikes again",
		"ownerFk": yankee_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 16,
		"name": "foxtrot_station_rerun",
		"displayName": "fucked six ways to Sunday",
		"ownerFk": yankee_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.LOCKED.value
	},
	{ "pk": 17,
		"name": "golf_station_rerun",
		"displayName": "goliath bam bam",
		"ownerFk": ingo_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 18,
		"name": "hotel_station_rerun",
		"displayName": "hella cool radio station",
		"ownerFk": ingo_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 19,
		"name": "india_station_rerun",
		"displayName": "bitchingly fast!",
		"ownerFk": station_saver_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 20,
		"name": "juliet_station_rerun",
		"displayName": "Neptune, how could you?",
		"ownerFk": unruled_station_user_id,
		"viewSecurityLevel": MinItemSecurityLevel.INVITED_USER.value
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
	{ "songFk": 59, "stationFk": 10 },
	{ "songFk": 59, "stationFk": 11 },
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
			"displayName": "Bravo Test User",
			"hashedPW": testPassword,
			"email": "test2@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": charlie_user_id,
			"username": "testUser_charlie",
			"displayName": "charlie the user of tests",
			"hashedPW": None,
			"email": "test3@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": delta_user_id,
			"username": "testUser_delta",
			"displayName": "DELTA USER",
			"hashedPW": testPassword,
			"email": "test4@test.com",
			"isDisabled": True,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": echo_user_id, #can't use. No password
			"username": "testUser_echo",
			"displayName": "ECHO, ECHO",
			"hashedPW": None,
			"email": None,
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": foxtrot_user_id,
			"username": "testUser_foxtrot",
			"displayName": "\uFB00 ozotroz",
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
			"displayName": "IndiaDisplay",
			"hashedPW": testPassword,
			"email": "test9@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": juliet_user_id,
			"username": "testUser_juliet",
			"displayName": "julietDisplay",
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
			"displayName": "\u006E\u0303ovoper",
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
		},
		{
			"pk": romeo_user_id,
			"username": "testUser_romeo",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test18@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": sierra_user_id,
			"username": "testUser_sierra",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test19@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": tango_user_id,
			"username": "testUser_tango",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test20@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": uniform_user_id,
			"username": "testUser_uniform",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test21@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": victor_user_id,
			"username": "testUser_victor",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test22@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": whiskey_user_id,
			"username": "testUser_whiskey",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test23@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": xray_user_id,
			"username": "testUser_xray",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test24@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": yankee_user_id,
			"username": "testUser_yankee",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test25@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": zulu_user_id,
			"username": "testUser_zulu",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test26@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": alice_user_id,
			"username": "testUser_alice",
			"displayName": "Alice is my name",
			"hashedPW": testPassword,
			"email": "test27@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": bertrand_user_id,
			"username": "bertrand",
			"displayName": "Bertrance",
			"hashedPW": testPassword,
			"email": "test28@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": carl_user_id,
			"username": "carl",
			"displayName": "Carl the Cactus",
			"hashedPW": testPassword,
			"email": "test29@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": dan_user_id,
			"username": "dan",
			"displayName": "Dookie Dan",
			"hashedPW": testPassword,
			"email": "test30@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": felix_user_id,
			"username": "felix",
			"displayName": "Felix the man",
			"hashedPW": testPassword,
			"email": "test31@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": foxman_user_id,
			"username": "foxman",
			"displayName": None,
			"hashedPW": testPassword,
			"email": "test32@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": foxtrain_user_id,
			"username": "foxtrain",
			"displayName": "Foxtrain chu",
			"hashedPW": testPassword,
			"email": "test33@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": george_user_id,
			"username": "george",
			"displayName": "George Costanza",
			"hashedPW": testPassword,
			"email": "test35@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": hamburger_user_id,
			"username": "hamburger",
			"displayName": "HamBurger",
			"hashedPW": testPassword,
			"email": "test36@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": horsetel_user_id,
			"username": "horsetel",
			"displayName": "horsetelophone",
			"hashedPW": testPassword,
			"email": "test37@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": ingo_user_id,
			"username": "ingo",
			"displayName": "Ingo      is a bad man",
			"hashedPW": testPassword,
			"email": "test38@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": ned_land_user_id,
			"username": "ned_land",
			"displayName": "Ned Land of the Spear",
			"hashedPW": testPassword,
			"email": "test39@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": narlon_user_id,
			"username": "narlon",
			"displayName": "Narloni",
			"hashedPW": testPassword,
			"email": "test40@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": number_user_id,
			"username": "7",
			"displayName": "seven",
			"hashedPW": testPassword,
			"email": "test41@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": oomdwell_user_id,
			"username": "testUser_oomdwell",
			"displayName": "Oomdwellmit",
			"hashedPW": testPassword,
			"email": "test42@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": None
		},
		{
			"pk": paul_bear_user_id,
			"username": "paulBear_testUser",
			"displayName": "Paul Bear",
			"hashedPW": testPassword,
			"email": "test43@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "paulBear_testUser"
		},
		{
			"pk": quirky_admin_user_id,
			"username": "quirkyAdmon_testUser",
			"displayName": "Quirky Admin",
			"hashedPW": testPassword,
			"email": "test44@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "quirkyAdmon_testUser"
		},
		{
			"pk": radical_path_user_id,
			"username": "radicalPath_testUser",
			"displayName": "Radical Path",
			"hashedPW": testPassword,
			"email": "test45@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "radicalPath_testUser"
		},
		{
			"pk": station_saver_user_id,
			"username": "stationSaver_testUser",
			"displayName": "Station Saver",
			"hashedPW": testPassword,
			"email": "test46@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "stationSaver_testUser"
		},
		{
			"pk": super_path_user_id,
			"username": "superPath_testUser",
			"displayName": "Super Pathouser",
			"hashedPW": testPassword,
			"email": "test47@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "superPath_testUser"
		},
		{
			"pk": tossed_slash_user_id,
			"username": "tossedSlash_testUser",
			"displayName": "Tossed Slash",
			"hashedPW": testPassword,
			"email": "test48@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "tossedSlash"
		},
		{
			"pk": unruled_station_user_id,
			"username": "unruledStation_testUser",
			"displayName": "Unruled Station User",
			"hashedPW": testPassword,
			"email": "test49@test.com",
			"isDisabled": False,
			"creationTimestamp": orderedTestDates[1].timestamp(),
			"dirRoot": "unruledStation"
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
			"role": UserRoleDef.PATH_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 15,
			"count": 0,
			"priority": None
		},
		{
			"userFk": foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 120,
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
			"role": UserRoleDef.USER_LIST.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userFk": juliet_user_id,
			"role": UserRoleDef.STATION_EDIT.value,
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
		},
		{
			"userFk": bravo_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userFk": tango_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userFk": india_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userFk": india_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userFk": india_user_id,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userFk": hotel_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userFk": hotel_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userFk": whiskey_user_id,
			"role": UserRoleDef.STATION_VIEW.value,
			"creationTimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userFk": november_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":10,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": lima_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": mike_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": oscar_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"count":5,
			"priority": RulePriorityLevel.STATION_PATH.value + 1,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": papa_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": alice_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": RulePriorityLevel.SITE.value - 2,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": paul_bear_user_id,
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": quirky_admin_user_id,
			"role": UserRoleDef.ADMIN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": radical_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": super_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SUPER.value,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userFk": unruled_station_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		}
	]

def get_station_permission_params(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:
	return [
		{
			"pk":1,
			"userFk": kilo_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userFk": mike_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":6,
			"userFk": november_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":5,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userFk": oscar_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"count":5,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userFk": papa_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userFk": quebec_user_id,
			"stationFk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":13,
			"userFk": juliet_user_id,
			"stationFk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userFk": juliet_user_id,
			"stationFk": 5,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":15,
			"userFk": juliet_user_id,
			"stationFk": 9,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userFk": hotel_user_id,
			"stationFk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userFk": xray_user_id,
			"stationFk": 14,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":18,
			"userFk": zulu_user_id,
			"stationFk": 14,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":19,
			"userFk": narlon_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":20,
			"userFk": narlon_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":21,
			"userFk": narlon_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":5,
			"count":300,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":22,
			"userFk": narlon_user_id,
			"stationFk": 18,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":23,
			"userFk": narlon_user_id,
			"stationFk": 18,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":100,
			"count":300,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":24,
			"userFk": horsetel_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":25,
			"userFk": george_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":26,
			"userFk": george_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":27,
			"userFk": george_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":28,
			"userFk": carl_user_id,
			"stationFk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":29,
			"userFk": oomdwell_user_id,
			"stationFk": 11,
			"role": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":30,
			"userFk": unruled_station_user_id,
			"stationFk": 20,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
	]

def get_path_permission_params(
	orderedTestDates: List[datetime]
)  -> list[dict[Any, Any]]:
	pathPermissions = [
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
		{
			"pk":6,
			"userFk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":7,
			"userFk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userFk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":9,
			"userFk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userFk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":11,
			"userFk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userFk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":13,
			"userFk": foxtrot_user_id,
			"path": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userFk": uniform_user_id,
			"path": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":15,
			"userFk": uniform_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userFk": station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userFk": station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationTimestamp": orderedTestDates[0].timestamp()
		}
	]
	return pathPermissions

def get_actions_history(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:

	return [
		{
			"pk": 1,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp(),
			"queuedTimestamp": orderedTestDates[0].timestamp(),
			"requestedTimestamp":orderedTestDates[0].timestamp()
		},
		{
			"pk": 2,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 1000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 1000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 1000
		},
		{
			"pk": 3,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 2000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 2000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 2000
		},
		{
			"pk": 4,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 3000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 3000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 3000
		},
		{
			"pk": 5,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 4000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 4000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 4000
		},
		{
			"pk": 6,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 5000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 5000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 5000
		},
		{
			"pk": 7,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 6000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 6000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 6000
		},
		{
			"pk": 8,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 7000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 7000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 7000
		},
		{
			"pk": 9,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 8000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 8000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 8000
		},
		{
			"pk": 10,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 9000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 9000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 9000
		},
		{
			"pk": 11,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 10000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 10000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 10000
		},
		{
			"pk": 12,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 11000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 11000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 11000
		},
		{
			"pk": 13,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 12000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 12000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 12000
		},
		{
			"pk": 14,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 13000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 13000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 13000
		},
		{
			"pk": 15,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 14000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 14000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 14000
		},
		{
			"pk": 16,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 15000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 15000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 15000
		},
		{
			"pk": 17,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 16000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 16000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 16000
		},
		{
			"pk": 18,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 18000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 18000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 18000
		},
		{
			"pk": 19,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 19000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 19000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 19000
		},
		{
			"pk": 20,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 20000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 20000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 20000
		},
		{
			"pk": 21,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 21000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 21000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 21000
		},
		{
			"pk": 22,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 22000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 22000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 22000
		},
		{
			"pk": 23,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 23000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 23000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 23000
		},
		{
			"pk": 24,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 24000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 24000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 24000
		},
		{
			"pk": 25,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_EDIT.value,
			"timestamp": orderedTestDates[0].timestamp() + 25000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 25000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 25000
		},
		{
			"pk": 26,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 26000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 26000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 26000
		},
		{
			"pk": 27,
			"userFk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 27000,
			"queuedTimestamp": orderedTestDates[0].timestamp() + 27000,
			"requestedTimestamp":orderedTestDates[0].timestamp() + 27000
		},
	]

def get_station_queue() -> list[dict[Any, Any]]:
	return [
		{
			"userActionHistoryFk": 1,
			"stationFk": 2,
			"songFk": 3,
		},
		{
			"userActionHistoryFk": 2,
			"stationFk": 2,
			"songFk": 4,
		},
		{
			"userActionHistoryFk": 3,
			"stationFk": 2,
			"songFk": 5,
		},
		{
			"userActionHistoryFk": 8,
			"stationFk": 5,
			"songFk": None,
		},
		{
			"userActionHistoryFk": 9,
			"stationFk": 5,
			"songFk": None,
		},
		{
			"userActionHistoryFk": 10,
			"stationFk": 5,
			"songFk": None,
		},
		{
			"userActionHistoryFk": 11,
			"stationFk": 5,
			"songFk": 5,
		},
		{
			"userActionHistoryFk": 12,
			"stationFk": 5,
			"songFk": 6,
		},
		{
			"userActionHistoryFk": 13,
			"stationFk": 5,
			"songFk": 7,
		},
		{
			"userActionHistoryFk": 14,
			"stationFk": 5,
			"songFk": 8,
		},
		{
			"userActionHistoryFk": 15,
			"stationFk": 5,
			"songFk": 9,
		},
		{
			"userActionHistoryFk": 16,
			"stationFk": 5,
			"songFk": 10,
		},
		{
			"userActionHistoryFk": 18,
			"stationFk": 6,
			"songFk": 10,
		},
		{
			"userActionHistoryFk": 19,
			"stationFk": 6,
			"songFk": 11,
		},
		{
			"userActionHistoryFk": 20,
			"stationFk": 6,
			"songFk": 12,
		},
		{
			"userActionHistoryFk": 21,
			"stationFk": 6,
			"songFk": 13,
		},
		{
			"userActionHistoryFk": 22,
			"stationFk": 6,
			"songFk": 14,
		},
		{
			"userActionHistoryFk": 23,
			"stationFk": 6,
			"songFk": 15,
		},
		{
			"userActionHistoryFk": 24,
			"stationFk": 6,
			"songFk": 16,
		},
		{
			"userActionHistoryFk": 25,
			"stationFk": 6,
			"songFk": None,
		},
		{
			"userActionHistoryFk": 26,
			"stationFk": 6,
			"songFk": None,
		}
	]