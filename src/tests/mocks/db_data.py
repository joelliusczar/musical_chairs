from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	RulePriorityLevel,
	MinItemSecurityLevel
)
try:
	from . import test_guids
	from .special_strings_reference import chinese1, irish1
except:
	#for if I try to import file from interactive
	import test_guids
	from special_strings_reference import chinese1, irish1


fooDirOwnerId = test_guids.user_guids[11]
jazzDirOwnerId = test_guids.user_guids[11]
blitzDirOwnerId = test_guids.user_guids[11]

bravo_user_id = test_guids.user_guids[2] #no path rules
charlie_user_id = test_guids.user_guids[3]
delta_user_id = test_guids.user_guids[4]
echo_user_id = test_guids.user_guids[5] #can't use. No password
foxtrot_user_id = test_guids.user_guids[6]
golf_user_id = test_guids.user_guids[7]
hotel_user_id = test_guids.user_guids[8]
india_user_id = test_guids.user_guids[9]
juliet_user_id = test_guids.user_guids[10]
kilo_user_id = test_guids.user_guids[11]
lima_user_id = test_guids.user_guids[12]
mike_user_id = test_guids.user_guids[13]
november_user_id = test_guids.user_guids[14]
oscar_user_id = test_guids.user_guids[15]
papa_user_id = test_guids.user_guids[16]
quebec_user_id = test_guids.user_guids[17]
romeo_user_id = test_guids.user_guids[18] #designated no roles user
sierra_user_id = test_guids.user_guids[19]
tango_user_id = test_guids.user_guids[20]
uniform_user_id = test_guids.user_guids[21]
victor_user_id = test_guids.user_guids[22]
whiskey_user_id = test_guids.user_guids[23]
xray_user_id = test_guids.user_guids[24]
yankee_user_id = test_guids.user_guids[25]
zulu_user_id = test_guids.user_guids[26]
alice_user_id = test_guids.user_guids[27]
bertrand_user_id = test_guids.user_guids[28]
carl_user_id = test_guids.user_guids[29]
dan_user_id = test_guids.user_guids[30]
felix_user_id = test_guids.user_guids[31]
foxman_user_id = test_guids.user_guids[32]
foxtrain_user_id = test_guids.user_guids[33]
george_user_id = test_guids.user_guids[34]
hamburger_user_id = test_guids.user_guids[35]
horsetel_user_id = test_guids.user_guids[36]
ingo_user_id = test_guids.user_guids[37]
ned_land_user_id = test_guids.user_guids[38]
narlon_user_id = test_guids.user_guids[39]
number_user_id = test_guids.user_guids[40]
oomdwell_user_id = test_guids.user_guids[41]
paul_bear_user_id = test_guids.user_guids[42]
quirky_admin_user_id = test_guids.user_guids[43]
radical_path_user_id = test_guids.user_guids[44]
station_saver_user_id = test_guids.user_guids[45]
super_path_user_id = test_guids.user_guids[46]
tossed_slash_user_id = test_guids.user_guids[47]
unruled_station_user_id = test_guids.user_guids[48]


artist_params = [
	{
		"pk": test_guids.artist_guids[1],
		"name": "alpha_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[2],
		"name": "bravo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[3],
		"name": "charlie_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[4],
		"name": "delta_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[5],
		"name": "echo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[6],
		"name": "foxtrot_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[7],
		"name": "golf_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[8],
		"name": "hotel_artist",
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[9],
		"name": "india_artist",
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[10],
		"name": "juliet_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[11],
		"name": "kilo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[12],
		"name": "lima_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[13],
		"name": "november_artist",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[14],
		"name": "oscar_artist",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[15],
		"name": "papa_artist",
		"ownerfk": november_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[16],
		"name": "romeo_artist",
		"ownerfk": india_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": test_guids.artist_guids[17],
		"name": "sierra_artist",
		"ownerfk": hotel_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
]

albumParams1 = [
	{
		"pk": test_guids.album_guids[1],
		"name": "broo_album",
		"albumartistfk": test_guids.artist_guids[7],
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[2],
		"name": "moo_album",
		"albumartistfk": test_guids.artist_guids[7],
		"year": 2003,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[8],
		"name": "shoo_album",
		"albumartistfk": test_guids.artist_guids[6],
		"year": 2003,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[9],
		"name": "who_2_album",
		"albumartistfk": test_guids.artist_guids[6],
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[10],
		"name": "who_1_album",
		"albumartistfk": test_guids.artist_guids[5],
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[11],
		"name": "boo_album",
		"albumartistfk": test_guids.artist_guids[4],
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams2 = [
	{
		"pk": test_guids.album_guids[4],
		"name": "soo_album",
		"year": 2004,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[7],
		"name": "koo_album",
		"year": 2010,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[13],
		"name": "koo_album",
		"year": 2010,
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams3 = [
	{
		"pk": test_guids.album_guids[5],
		"name": "doo_album",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[6],
		"name": "roo_album",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[12],
		"name": "garoo_album",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	}
]

albumParams4 = [
	{
		"pk": test_guids.album_guids[3],
		"name": "juliet_album",
		"albumartistfk": test_guids.artist_guids[7],
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": test_guids.album_guids[14],
		"name": "grunt_album",
		"ownerfk": juliet_user_id,
		"albumartistfk": test_guids.artist_guids[7],
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

album_params = [
	*albumParams1,
	*albumParams2,
	*albumParams3,
	*albumParams4
]

song_params = [
	{ "pk": test_guids.song_guids[1],
		"path": "foo/goo/boo/sierra",
		"name": "sierra_song",
		"albumfk": test_guids.album_guids[11],
		"track": 1,
		"disc": 1,
		"genre": "pop",
		"explicit": 0,
		"bitrate": 144,
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[2],
		"path": "foo/goo/boo/tango",
		"name": "tango_song",
		"albumfk": test_guids.album_guids[11],
		"track": 2,
		"disc": 1,
		"genre": "pop",
		"explicit": 0,
		"bitrate": 144,
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[3],
		"path": "foo/goo/boo/uniform",
		"name": "uniform_song",
		"albumfk": test_guids.album_guids[11],
		"track": 3,
		"disc": 1,
		"genre": "pop",
		"explicit": 1,
		"bitrate": 144,
		"comment": "Kazoos make good parrallel parkers"
	},
	{ "pk": test_guids.song_guids[4],
		"path": "foo/goo/boo/victor",
		"name": "victor_song",
		"albumfk": test_guids.album_guids[11],
		"track": 4,
		"disc": 1,
		"genre": "pop",
		"bitrate": 144,
		"comment": "Kazoos make bad swimmers"
	},
	{ "pk": test_guids.song_guids[5],
		"path": "foo/goo/boo/victor_2",
		"name": "victor_song",
		"albumfk": test_guids.album_guids[11],
		"track": 5,
		"disc": 1,
		"genre": "pop",
		"bitrate": 144,
		"comment": "Kazoos make good hood rats"
	},
	{ "pk": test_guids.song_guids[6],
		"path": "foo/goo/who_1/whiskey",
		"name": "whiskey_song",
		"albumfk": test_guids.album_guids[10],
		"track": 1,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[7],
		"path": "foo/goo/who_1/xray",
		"name": "xray_song",
		"albumfk": test_guids.album_guids[10],
		"track": 2,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[8],
		"path": "foo/goo/who_1/yankee",
		"name": "yankee_song",
		"albumfk": test_guids.album_guids[10],
		"track": 3,
		"disc": 1,
		"genre": "pop",
		"comment": "guitars make good swimmers"
	},
	{ "pk": test_guids.song_guids[9],
		"path": "foo/goo/who_1/zulu",
		"name": "zulu_song",
		"albumfk": test_guids.album_guids[10],
		"track": 4,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[10],
		"path": "foo/goo/who_1/alpha",
		"name": "alpha_song",
		"albumfk": test_guids.album_guids[10],
		"track": 5,
		"disc": 1,
		"genre": "pop",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[11],
		"path": "foo/goo/who_2/bravo",
		"name": "bravo_song",
		"albumfk": test_guids.album_guids[9],
		"track": 1,
		"disc": 2,
		"genre": "pop",
		"comment": "hamburgers make flat swimmers"
	},
	{ "pk": test_guids.song_guids[12],
		"path": "foo/goo/who_2/charlie",
		"name": "charlie_song",
		"albumfk": test_guids.album_guids[9],
		"track": 2,
		"disc": 2,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[13],
		"path": "foo/goo/who_2/delta",
		"name": "delta_song",
		"albumfk": test_guids.album_guids[9],
		"track": 3,
		"disc": 2,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": test_guids.song_guids[14],
		"path": "foo/goo/who_2/foxtrot",
		"name": "foxtrot_song",
		"albumfk": test_guids.album_guids[9],
		"track": 4,
		"disc": 2,
		"genre": "pop",
	},
	{ "pk": test_guids.song_guids[15],
		"path": "foo/goo/who_2/golf",
		"name": "golf_song",
		"albumfk": test_guids.album_guids[9],
		"track": 5,
		"disc": 2,
		"genre": "pop",
	},
	{ "pk": test_guids.song_guids[16],
		"path": "foo/goo/shoo/hotel",
		"name": "hotel_song",
		"albumfk": test_guids.album_guids[8],
		"track": 1,
		"disc": 1,
	},
	{ "pk": test_guids.song_guids[17],
		"path": "foo/goo/shoo/india",
		"name": "india_song",
		"albumfk": test_guids.album_guids[8],
		"track": 2,
		"disc": 1,
	},
	{ "pk": test_guids.song_guids[18],
		"path": "foo/goo/shoo/juliet",
		"name": "juliet_song",
		"albumfk": test_guids.album_guids[8],
		"track": 3,
		"disc": 1,
	},
	{ "pk": test_guids.song_guids[19],
		"path": "foo/goo/shoo/kilo",
		"name": "kilo_song",
		"albumfk": test_guids.album_guids[8],
		"track": 4,
		"disc": 1,
	},
	{ "pk": test_guids.song_guids[20],
		"path": "foo/goo/koo/lima",
		"name": "lima_song",
		"albumfk": test_guids.album_guids[7],
		"track": 1,
	},
	{ "pk": test_guids.song_guids[21],
		"path": "foo/goo/koo/mike",
		"name": "mike_song",
		"albumfk": test_guids.album_guids[7],
		"track": 2,
	},
	{ "pk": test_guids.song_guids[22],
		"path": "foo/goo/koo/november",
		"name": "november_song",
		"albumfk": test_guids.album_guids[7],
		"track": 3,
	},
	{ "pk": test_guids.song_guids[23],
		"path": "foo/goo/roo/oscar",
		"name": "oscar_song",
		"albumfk": test_guids.album_guids[6],
	},
	{ "pk": test_guids.song_guids[24],
		"path": "foo/goo/roo/papa",
		"name": "papa_song",
		"albumfk": test_guids.album_guids[6],
	},
	{ "pk": test_guids.song_guids[25],
		"path": "foo/goo/roo/romeo",
		"name": "romeo_song",
		"albumfk": test_guids.album_guids[6],
	},
	{ "pk": test_guids.song_guids[26],
		"path": "foo/goo/roo/sierra2",
		"name": "sierra2_song",
		"albumfk": test_guids.album_guids[6],
	},
	{ "pk": test_guids.song_guids[27],
		"path": "foo/goo/roo/tango2",
		"name": "tango2_song",
	},
	{ "pk": test_guids.song_guids[28],
		"path": "foo/goo/roo/uniform2",
		"name": "uniform2_song",
	},
	{ "pk": test_guids.song_guids[29],
		"path": "foo/goo/roo/victor2",
		"name": "victor2_song",
		"albumfk": test_guids.album_guids[4],
	},
	{ "pk": test_guids.song_guids[30],
		"path": "foo/goo/roo/whiskey2",
		"name": "whiskey2_song",
	},
	{ "pk": test_guids.song_guids[31],
		"path": "foo/goo/roo/xray2",
		"name": "xray2_song",
	},
	{ "pk": test_guids.song_guids[32],
		"path": "foo/goo/doo/yankee2",
		"name": "yankee2_song",
		"albumfk": test_guids.album_guids[5],
		"genre": "bop",
		"explicit": 0,
		"bitrate": 121,
	},
	{ "pk": test_guids.song_guids[33],
		"path": "foo/goo/doo/zulu2",
		"name": "zulu2_song",
		"albumfk": test_guids.album_guids[5],
		"genre": "bop",
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": test_guids.song_guids[34],
		"path": "foo/goo/soo/alpha2",
		"name": "alpha2_song",
		"albumfk": test_guids.album_guids[4],
		"track": 1,
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": test_guids.song_guids[35],
		"path": "foo/goo/soo/bravo2",
		"name": "bravo2_song",
		"albumfk": test_guids.album_guids[4],
		"track": 2,
		"explicit": 1,
	},
	{ "pk": test_guids.song_guids[36],
		"path": "foo/goo/soo/charlie2",
		"name": "charlie2_song",
		"albumfk": test_guids.album_guids[4],
		"track": 3,
		"comment": "Boot 'n' scoot"
	},
	{ "pk": test_guids.song_guids[37],
		"path": "foo/goo/moo/delta2",
		"name": "delta2_song",
		"albumfk": test_guids.album_guids[2],
		"track": 1,
	},
	{ "pk": test_guids.song_guids[38],
		"path": "foo/goo/moo/echo2",
		"name": "echo2_song",
		"albumfk": test_guids.album_guids[2],
		"track": 2,
	},
	{ "pk": test_guids.song_guids[39],
		"path": "foo/goo/moo/foxtrot2",
		"name": "foxtrot2_song",
		"albumfk": test_guids.album_guids[2],
		"track": 3,
	},
	{ "pk": test_guids.song_guids[40],
		"path": "foo/goo/moo/golf2",
		"name": "golf2_song",
		"albumfk": test_guids.album_guids[2],
		"track": 4,
	},
	{ "pk": test_guids.song_guids[41],
		"path": "foo/goo/broo/hotel2",
		"name": "hotel2_song",
		"albumfk": test_guids.album_guids[1],
	},
	{ "pk": test_guids.song_guids[42],
		"path": "foo/goo/broo/india2",
		"name": "india2_song",
		"albumfk": test_guids.album_guids[1],
	},
	{ "pk": test_guids.song_guids[43],
		"path": "foo/goo/broo/juliet2",
		"name": "juliet2_song",
		"albumfk": test_guids.album_guids[1],
	},
	{ "pk": test_guids.song_guids[44],
		"path": "foo/rude/bog/kilo2",
	},
	{ "pk": test_guids.song_guids[45],
		"path": "foo/rude/bog/lima2",
	},
	{ "pk": test_guids.song_guids[46],
		"path": "foo/rude/rog/mike2",
	},
	{ "pk": test_guids.song_guids[47],
		"path": "foo/rude/rog/november2",
	},
	{ "pk": test_guids.song_guids[48],
		"path": "foo/rude/rog/oscar2",
	},
	{ "pk": test_guids.song_guids[49],
		"path": "foo/dude/dog/papa2",
	},
	{ "pk": test_guids.song_guids[50],
		"path": "foo/bar/baz/romeo2",
		"name": chinese1,
	},
	{ "pk": test_guids.song_guids[51],
		"path": "foo/bar/baz/sierra3",
		"name": irish1,
	},
	{ "pk": test_guids.song_guids[52],
		"name": "tango3",
		"path": "jazz/rude/rog/tango3",
	},
	{ "pk": test_guids.song_guids[53],
		"name": "uniform3",
		"path": "jazz/rude/rog/uniform3",
	},
	{ "pk": test_guids.song_guids[54],
		"name": "victor3",
		"path": "jazz/cat/kitten/victor3",
	},
	{ "pk": test_guids.song_guids[55],
		"name": "whiskey3",
		"path": "blitz/mar/wall/whiskey3",
	},
	{ "pk": test_guids.song_guids[56],
		"name": "xray3",
		"path": "blitz/mar/wall/xray3",
	},
	{ "pk": test_guids.song_guids[57],
		"name": "zulu3",
		"path": "blitz/rhino/rhina/zulu3",
	},
	{ "pk": test_guids.song_guids[58],
		"name": "alpha4_song",
		"path": "jazz/lurk/toot/alpha4_song",
		"albumfk": test_guids.album_guids[7],
	},
	{ "pk": test_guids.song_guids[59],
		"path": "foo/goo/looga/alpha",
		"name": "looga_alpha_song",
		"albumfk": test_guids.album_guids[14],
		"track": 5,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[60],
		"path": "tossedSlash/goo/looga/alpha",
		"name": "looga_alpha_song",
		"genre": "bam",
		"comment": "Banana Soup"
	},
	{ "pk": test_guids.song_guids[61],
		"path": "tossedSlash/goo/looga/bravo",
		"name": "looga_bravo_song",
		"genre": "bam",
		"comment": "Banana Soup"
	},
	{ "pk": test_guids.song_guids[62],
		"path": "tossedSlash/guess/gold/jar",
		"name": "jar_song",
		"albumfk": test_guids.album_guids[14],
		"track": 5,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[63],
		"path": "tossedSlash/guess/gold/bar",
		"name": "bar_song",
		"albumfk": test_guids.album_guids[14],
		"track": 6,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[64],
		"path": "tossedSlash/guess/gold/run",
		"name": "run_song",
		"albumfk": test_guids.album_guids[14],
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[65],
		"path": "tossedSlash/band/bun",
		"name": "bun_song",
		"albumfk": test_guids.album_guids[14],
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[66],
		"path": "tossedSlash/band/hun",
		"name": "hun_song",
		"albumfk": test_guids.album_guids[14],
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[67],
		"path": "tossedSlash/guess/silver/run",
		"name": "run_song",
		"albumfk": test_guids.album_guids[14],
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": test_guids.song_guids[68],
		"path": "tossedSlash/guess/silver/plastic",
		"name": "plastic_tune",
		"albumfk": test_guids.album_guids[12],
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": test_guids.song_guids[69],
		"path": "tossedSlash/guess/silver/salt",
		"name": "salt_tune",
		"albumfk": test_guids.album_guids[12],
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": test_guids.song_guids[70],
		"path": "tossedSlash/guess/silver/green",
		"name": "green_tune",
		"albumfk": test_guids.album_guids[12],
		"track": 8,
		"disc": 1,
		"genre": "bam",
	}
]

songArtistParams = [
	{ "pk": test_guids.song_artist_guids[1], "songfk": test_guids.song_guids[40], "artistfk": test_guids.artist_guids[7] },
	{ "pk": test_guids.song_artist_guids[2], "songfk": test_guids.song_guids[39], "artistfk": test_guids.artist_guids[7] },
	{ "pk": test_guids.song_artist_guids[3], "songfk": test_guids.song_guids[38], "artistfk": test_guids.artist_guids[7] },
	{ "pk": test_guids.song_artist_guids[4], "songfk": test_guids.song_guids[37], "artistfk": test_guids.artist_guids[7] },
	{ "pk": test_guids.song_artist_guids[5], "songfk": test_guids.song_guids[36], "artistfk": test_guids.artist_guids[2] },
	{ "pk": test_guids.song_artist_guids[6], "songfk": test_guids.song_guids[35], "artistfk": test_guids.artist_guids[1] },
	{ "pk": test_guids.song_artist_guids[7], "songfk": test_guids.song_guids[34], "artistfk": test_guids.artist_guids[3] },
	{ "pk": test_guids.song_artist_guids[8], "songfk": test_guids.song_guids[33], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[9], "songfk": test_guids.song_guids[32], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[10], "songfk": test_guids.song_guids[31], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[11], "songfk": test_guids.song_guids[30], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[12], "songfk": test_guids.song_guids[29], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[13], "songfk": test_guids.song_guids[28], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[14], "songfk": test_guids.song_guids[27], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[15], "songfk": test_guids.song_guids[26], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[16], "songfk": test_guids.song_guids[25], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[17], "songfk": test_guids.song_guids[24], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[18], "songfk": test_guids.song_guids[23], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[19], "songfk": test_guids.song_guids[22], "artistfk": test_guids.artist_guids[2] },
	{ "pk": test_guids.song_artist_guids[20], "songfk": test_guids.song_guids[21], "artistfk": test_guids.artist_guids[2] },
	{ "pk": test_guids.song_artist_guids[21], "songfk": test_guids.song_guids[20], "artistfk": test_guids.artist_guids[2] },
	{ "pk": test_guids.song_artist_guids[22], "songfk": test_guids.song_guids[19], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[23], "songfk": test_guids.song_guids[18], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[24], "songfk": test_guids.song_guids[17], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[25], "songfk": test_guids.song_guids[16], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[26], "songfk": test_guids.song_guids[15], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[27], "songfk": test_guids.song_guids[14], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[28], "songfk": test_guids.song_guids[13], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[29], "songfk": test_guids.song_guids[12], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[30], "songfk": test_guids.song_guids[11], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[31], "songfk": test_guids.song_guids[10], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[32], "songfk": test_guids.song_guids[9], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[33], "songfk": test_guids.song_guids[8], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[34], "songfk": test_guids.song_guids[7], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[35], "songfk": test_guids.song_guids[6], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[36], "songfk": test_guids.song_guids[5], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[37], "songfk": test_guids.song_guids[4], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[38], "songfk": test_guids.song_guids[3], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[39], "songfk": test_guids.song_guids[2], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[40], "songfk": test_guids.song_guids[1], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[45], "songfk": test_guids.song_guids[21], "artistfk": test_guids.artist_guids[4] },
	{ "pk": test_guids.song_artist_guids[46], "songfk": test_guids.song_guids[21], "artistfk": test_guids.artist_guids[6] },
	{ "pk": test_guids.song_artist_guids[47], "songfk": test_guids.song_guids[17], "artistfk": test_guids.artist_guids[10] },
	{ "pk": test_guids.song_artist_guids[48], "songfk": test_guids.song_guids[17], "artistfk": test_guids.artist_guids[5] },
	{ "pk": test_guids.song_artist_guids[49], "songfk": test_guids.song_guids[17], "artistfk": test_guids.artist_guids[2] },
	{ "pk": test_guids.song_artist_guids[50], "songfk": test_guids.song_guids[17], "artistfk": test_guids.artist_guids[11] },
	{ "pk": test_guids.song_artist_guids[51], "songfk": test_guids.song_guids[35], "artistfk": test_guids.artist_guids[12] },
	{ "pk": test_guids.song_artist_guids[52], "songfk": test_guids.song_guids[59], "artistfk": test_guids.artist_guids[16] },
	{ "pk": test_guids.song_artist_guids[54], "songfk": test_guids.song_guids[59], "artistfk": test_guids.artist_guids[17] },
]

songArtistParams2 = [
	{ "pk": test_guids.song_artist_guids[41], "songfk": test_guids.song_guids[43], "artistfk": test_guids.artist_guids[7], "isprimaryartist": 1 },
	{ "pk": test_guids.song_artist_guids[42], "songfk": test_guids.song_guids[42], "artistfk": test_guids.artist_guids[7], "isprimaryartist": 1 },
	{ "pk": test_guids.song_artist_guids[43], "songfk": test_guids.song_guids[41], "artistfk": test_guids.artist_guids[7], "isprimaryartist": 1 },
	{ "pk": test_guids.song_artist_guids[44], "songfk": test_guids.song_guids[1], "artistfk": test_guids.artist_guids[6], "isprimaryartist": 1 },
	{ "pk": test_guids.song_artist_guids[53], "songfk": test_guids.song_guids[59], "artistfk": test_guids.artist_guids[15], "isprimaryartist": 1 },
]

songArtistParamsAll = [*songArtistParams, *songArtistParams2]

station_params = [
	{ "pk": test_guids.station_guids[1],
		"name": "oscar_station",
		"displayname": "Oscar the grouch",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[2],
		"name": "papa_station",
		"displayname": "Come to papa",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[3],
		"name": "romeo_station",
		"displayname": "But soft, what yonder wind breaks",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[4],
		"name": "sierra_station",
		"displayname": "The greatest lie the devil ever told",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[5],
		"name": "tango_station",
		"displayname": "Nuke the whales",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[6],
		"name": "yankee_station",
		"displayname": "Blurg the blergos",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[7],
		"name": "uniform_station",
		"displayname": "Asshole at the wheel",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[8],
		"name": "victor_station",
		"displayname": "Fat, drunk, and stupid",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[9],
		"name": "whiskey_station",
		"displayname": "Chris-cross apple sauce",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[10],
		"name": "xray_station",
		"displayname": "Pentagular",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[11],
		"name": "zulu_station",
		"displayname": "Hammer time",
		"ownerfk": juliet_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": test_guids.station_guids[12],
		"name": "alpha_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.RULED_USER.value
	},
	{ "pk": test_guids.station_guids[13],
		"name": "bravo_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.ANY_USER.value
	},
	{ "pk": test_guids.station_guids[14],
		"name": "charlie_station_rerun",
		"displayname": "The Wide World of Sports",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": test_guids.station_guids[15],
		"name": "delta_station_rerun",
		"displayname": "Dookie Dan strikes again",
		"ownerfk": yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": test_guids.station_guids[16],
		"name": "foxtrot_station_rerun",
		"displayname": "fucked six ways to Sunday",
		"ownerfk": yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.LOCKED.value
	},
	{ "pk": test_guids.station_guids[17],
		"name": "golf_station_rerun",
		"displayname": "goliath bam bam",
		"ownerfk": ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": test_guids.station_guids[18],
		"name": "hotel_station_rerun",
		"displayname": "hella cool radio station",
		"ownerfk": ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": test_guids.station_guids[19],
		"name": "india_station_rerun",
		"displayname": "bitchingly fast!",
		"ownerfk": station_saver_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": test_guids.station_guids[20],
		"name": "juliet_station_rerun",
		"displayname": "Neptune, how could you?",
		"ownerfk": unruled_station_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	}
]

stationSongParams = [
	{ "songfk": test_guids.song_guids[43], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[43], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[43], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[41], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[40], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[38], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[37], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[36], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[35], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[34], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[33], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[32], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[31], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[30], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[29], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[28], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[27], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[26], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[25], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[24], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[23], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[22], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[21], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[20], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[19], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[18], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[17], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[17], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[16], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[15], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[15], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[14], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[13], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[12], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[11], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[10], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[9], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[8], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[7], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[6], "stationfk": test_guids.station_guids[3] },
	{ "songfk": test_guids.song_guids[5], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[4], "stationfk": test_guids.station_guids[4] },
	{ "songfk": test_guids.song_guids[3], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[2], "stationfk": test_guids.station_guids[1] },
	{ "songfk": test_guids.song_guids[1], "stationfk": test_guids.station_guids[2] },
	{ "songfk": test_guids.song_guids[1], "stationfk": test_guids.station_guids[6] },
	{ "songfk": test_guids.song_guids[4], "stationfk": test_guids.station_guids[6] },
	{ "songfk": test_guids.song_guids[50], "stationfk": test_guids.station_guids[6] },
	{ "songfk": test_guids.song_guids[44], "stationfk": test_guids.station_guids[8] },
	{ "songfk": test_guids.song_guids[45], "stationfk": test_guids.station_guids[8] },
	{ "songfk": test_guids.song_guids[46], "stationfk": test_guids.station_guids[8] },
	{ "songfk": test_guids.song_guids[47], "stationfk": test_guids.station_guids[8] },
	{ "songfk": test_guids.song_guids[59], "stationfk": test_guids.station_guids[10] },
	{ "songfk": test_guids.song_guids[59], "stationfk": test_guids.station_guids[11] },
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
			"displayname": None,
			"hashedpw": testPassword,
			"email": primaryUser.email,
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"dirroot": ""
		},
		{
			"pk": bravo_user_id,
			"username": "testUser_bravo",
			"displayname": "Bravo Test User",
			"hashedpw": testPassword,
			"email": "test2@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": charlie_user_id,
			"username": "testUser_charlie",
			"displayname": "charlie the user of tests",
			"hashedpw": None,
			"email": "test3@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": delta_user_id,
			"username": "testUser_delta",
			"displayname": "DELTA USER",
			"hashedpw": testPassword,
			"email": "test4@test.com",
			"isdisabled": True,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": echo_user_id, #can't use. No password
			"username": "testUser_echo",
			"displayname": "ECHO, ECHO",
			"hashedpw": None,
			"email": None,
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": foxtrot_user_id,
			"username": "testUser_foxtrot",
			"displayname": "\uFB00 ozotroz",
			"hashedpw": testPassword,
			"email": "test6@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": golf_user_id,
			"username": "testUser_golf",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test7@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": hotel_user_id,
			"username": "testUser_hotel",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test8@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": india_user_id,
			"username": "testUser_india",
			"displayname": "IndiaDisplay",
			"hashedpw": testPassword,
			"email": "test9@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": juliet_user_id,
			"username": "testUser_juliet",
			"displayname": "julietDisplay",
			"hashedpw": testPassword,
			"email": "test10@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": kilo_user_id,
			"username": "testUser_kilo",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test11@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "/foo"
		},
		{
			"pk": lima_user_id,
			"username": "testUser_lima",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test12@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": mike_user_id,
			"username": "testUser_mike",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test13@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": november_user_id,
			"username": "testUser_november",
			"displayname": "\u006E\u0303ovoper",
			"hashedpw": testPassword,
			"email": "test14@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": oscar_user_id,
			"username": "testUser_oscar",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test15@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": papa_user_id,
			"username": "testUser_papa",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test16@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": quebec_user_id,
			"username": "testUser_quebec",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test17@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": romeo_user_id,
			"username": "testUser_romeo",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test18@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": sierra_user_id,
			"username": "testUser_sierra",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test19@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": tango_user_id,
			"username": "testUser_tango",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test20@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": uniform_user_id,
			"username": "testUser_uniform",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test21@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": victor_user_id,
			"username": "testUser_victor",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test22@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": whiskey_user_id,
			"username": "testUser_whiskey",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test23@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": xray_user_id,
			"username": "testUser_xray",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test24@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": yankee_user_id,
			"username": "testUser_yankee",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test25@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": zulu_user_id,
			"username": "testUser_zulu",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test26@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": alice_user_id,
			"username": "testUser_alice",
			"displayname": "Alice is my name",
			"hashedpw": testPassword,
			"email": "test27@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": bertrand_user_id,
			"username": "bertrand",
			"displayname": "Bertrance",
			"hashedpw": testPassword,
			"email": "test28@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": carl_user_id,
			"username": "carl",
			"displayname": "Carl the Cactus",
			"hashedpw": testPassword,
			"email": "test29@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": dan_user_id,
			"username": "dan",
			"displayname": "Dookie Dan",
			"hashedpw": testPassword,
			"email": "test30@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": felix_user_id,
			"username": "felix",
			"displayname": "Felix the man",
			"hashedpw": testPassword,
			"email": "test31@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": foxman_user_id,
			"username": "foxman",
			"displayname": None,
			"hashedpw": testPassword,
			"email": "test32@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": foxtrain_user_id,
			"username": "foxtrain",
			"displayname": "Foxtrain chu",
			"hashedpw": testPassword,
			"email": "test33@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": george_user_id,
			"username": "george",
			"displayname": "George Costanza",
			"hashedpw": testPassword,
			"email": "test35@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": hamburger_user_id,
			"username": "hamburger",
			"displayname": "HamBurger",
			"hashedpw": testPassword,
			"email": "test36@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": horsetel_user_id,
			"username": "horsetel",
			"displayname": "horsetelophone",
			"hashedpw": testPassword,
			"email": "test37@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": ingo_user_id,
			"username": "ingo",
			"displayname": "Ingo      is a bad man",
			"hashedpw": testPassword,
			"email": "test38@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": ned_land_user_id,
			"username": "ned_land",
			"displayname": "Ned Land of the Spear",
			"hashedpw": testPassword,
			"email": "test39@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": narlon_user_id,
			"username": "narlon",
			"displayname": "Narloni",
			"hashedpw": testPassword,
			"email": "test40@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": number_user_id,
			"username": "7",
			"displayname": "seven",
			"hashedpw": testPassword,
			"email": "test41@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": oomdwell_user_id,
			"username": "testUser_oomdwell",
			"displayname": "Oomdwellmit",
			"hashedpw": testPassword,
			"email": "test42@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": None
		},
		{
			"pk": paul_bear_user_id,
			"username": "paulBear_testUser",
			"displayname": "Paul Bear",
			"hashedpw": testPassword,
			"email": "test43@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "paulBear_testUser"
		},
		{
			"pk": quirky_admin_user_id,
			"username": "quirkyAdmon_testUser",
			"displayname": "Quirky Admin",
			"hashedpw": testPassword,
			"email": "test44@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "quirkyAdmon_testUser"
		},
		{
			"pk": radical_path_user_id,
			"username": "radicalPath_testUser",
			"displayname": "Radical Path",
			"hashedpw": testPassword,
			"email": "test45@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "radicalPath_testUser"
		},
		{
			"pk": station_saver_user_id,
			"username": "stationSaver_testUser",
			"displayname": "Station Saver",
			"hashedpw": testPassword,
			"email": "test46@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "stationSaver_testUser"
		},
		{
			"pk": super_path_user_id,
			"username": "superPath_testUser",
			"displayname": "Super Pathouser",
			"hashedpw": testPassword,
			"email": "test47@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "superPath_testUser"
		},
		{
			"pk": tossed_slash_user_id,
			"username": "tossedSlash_testUser",
			"displayname": "Tossed Slash",
			"hashedpw": testPassword,
			"email": "test48@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "tossedSlash"
		},
		{
			"pk": unruled_station_user_id,
			"username": "unruledStation_testUser",
			"displayname": "Unruled Station User",
			"hashedpw": testPassword,
			"email": "test49@test.com",
			"isdisabled": False,
			"creationtimestamp": orderedTestDates[1].timestamp(),
			"dirroot": "unruledStation"
		}
	]
	return users_params

def get_user_role_params(
	orderedTestDates: List[datetime],
	primaryUser: AccountInfo,
) -> list[dict[Any, Any]]:
	return [
		{
			"userfk": primaryUser.id,
			"role": UserRoleDef.ADMIN.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": bravo_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": charlie_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": delta_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": delta_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 15,
			"count": 0,
			"priority": None
		},
		{
			"userfk": foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 120,
			"count": 0,
			"priority": None
		},
		{
			"userfk": foxtrot_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": golf_user_id,
			"role": UserRoleDef.USER_LIST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": juliet_user_id,
			"role": UserRoleDef.STATION_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": quebec_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":300,
			"count":15,
			"priority": None
		},
		{
			"userfk": bravo_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": tango_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": india_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": india_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": india_user_id,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": hotel_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": hotel_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": whiskey_user_id,
			"role": UserRoleDef.STATION_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": november_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": lima_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": mike_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": oscar_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"count":5,
			"priority": RulePriorityLevel.STATION_PATH.value + 1,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": papa_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": alice_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": RulePriorityLevel.SITE.value - 2,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": paul_bear_user_id,
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": quirky_admin_user_id,
			"role": UserRoleDef.ADMIN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": radical_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": super_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SUPER.value,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": unruled_station_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		}
	]

def get_station_permission_params(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:
	return [
		{
			"pk":test_guids.station_user_permission_guid[1],
			"userfk": kilo_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[4],
			"userfk": mike_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[6],
			"userfk": november_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":5,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[8],
			"userfk": oscar_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"count":5,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[10],
			"userfk": papa_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[12],
			"userfk": quebec_user_id,
			"stationfk": test_guids.station_guids[3],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[13],
			"userfk": juliet_user_id,
			"stationfk": test_guids.station_guids[9],
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[14],
			"userfk": juliet_user_id,
			"stationfk": test_guids.station_guids[5],
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[15],
			"userfk": juliet_user_id,
			"stationfk": test_guids.station_guids[9],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[16],
			"userfk": hotel_user_id,
			"stationfk": test_guids.station_guids[9],
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[17],
			"userfk": xray_user_id,
			"stationfk": test_guids.station_guids[14],
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[18],
			"userfk": zulu_user_id,
			"stationfk": test_guids.station_guids[14],
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[19],
			"userfk": narlon_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[20],
			"userfk": narlon_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[21],
			"userfk": narlon_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":5,
			"count":300,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[22],
			"userfk": narlon_user_id,
			"stationfk": test_guids.station_guids[18],
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[23],
			"userfk": narlon_user_id,
			"stationfk": test_guids.station_guids[18],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":100,
			"count":300,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[24],
			"userfk": horsetel_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[25],
			"userfk": george_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[26],
			"userfk": george_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[27],
			"userfk": george_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[28],
			"userfk": carl_user_id,
			"stationfk": test_guids.station_guids[17],
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[29],
			"userfk": oomdwell_user_id,
			"stationfk": test_guids.station_guids[11],
			"role": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.station_user_permission_guid[30],
			"userfk": unruled_station_user_id,
			"stationfk": test_guids.station_guids[20],
			"role": UserRoleDef.STATION_FLIP.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
	]

def get_path_permission_params(
	orderedTestDates: List[datetime]
)  -> list[dict[Any, Any]]:
	pathPermissions = [
		{
			"pk":test_guids.path_user_permission_guids[1],
			"userfk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[2],
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[3],
			"userfk": kilo_user_id,
			"path": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[4],
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[5],
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[6],
			"userfk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[7],
			"userfk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[8],
			"userfk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[9],
			"userfk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[10],
			"userfk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[11],
			"userfk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[12],
			"userfk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[13],
			"userfk": foxtrot_user_id,
			"path": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[14],
			"userfk": uniform_user_id,
			"path": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[15],
			"userfk": uniform_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[16],
			"userfk": station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":test_guids.path_user_permission_guids[17],
			"userfk": station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		}
	]
	return pathPermissions

def get_actions_history(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:

	return [
		{
			"pk": test_guids.user_action_history_guids[1],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp(),
			"queuedtimestamp": orderedTestDates[0].timestamp(),
			"requestedtimestamp":orderedTestDates[0].timestamp()
		},
		{
			"pk": test_guids.user_action_history_guids[2],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 1000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 1000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 1000
		},
		{
			"pk": test_guids.user_action_history_guids[3],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 2000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 2000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 2000
		},
		{
			"pk": test_guids.user_action_history_guids[4],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 3000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 3000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 3000
		},
		{
			"pk": test_guids.user_action_history_guids[5],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 4000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 4000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 4000
		},
		{
			"pk": test_guids.user_action_history_guids[6],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 5000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 5000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 5000
		},
		{
			"pk": test_guids.user_action_history_guids[7],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 6000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 6000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 6000
		},
		{
			"pk": test_guids.user_action_history_guids[8],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 7000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 7000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 7000
		},
		{
			"pk": test_guids.user_action_history_guids[9],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 8000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 8000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 8000
		},
		{
			"pk": test_guids.user_action_history_guids[10],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 9000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 9000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 9000
		},
		{
			"pk": test_guids.user_action_history_guids[11],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 10000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 10000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 10000
		},
		{
			"pk": test_guids.user_action_history_guids[12],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 11000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 11000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 11000
		},
		{
			"pk": test_guids.user_action_history_guids[13],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 12000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 12000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 12000
		},
		{
			"pk": test_guids.user_action_history_guids[14],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 13000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 13000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 13000
		},
		{
			"pk": test_guids.user_action_history_guids[15],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 14000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 14000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 14000
		},
		{
			"pk": test_guids.user_action_history_guids[16],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 15000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 15000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 15000
		},
		{
			"pk": test_guids.user_action_history_guids[17],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 16000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 16000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 16000
		},
		{
			"pk": test_guids.user_action_history_guids[18],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 18000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 18000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 18000
		},
		{
			"pk": test_guids.user_action_history_guids[19],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 19000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 19000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 19000
		},
		{
			"pk": test_guids.user_action_history_guids[20],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 20000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 20000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 20000
		},
		{
			"pk": test_guids.user_action_history_guids[21],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 21000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 21000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 21000
		},
		{
			"pk": test_guids.user_action_history_guids[22],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 22000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 22000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 22000
		},
		{
			"pk": test_guids.user_action_history_guids[23],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 23000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 23000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 23000
		},
		{
			"pk": test_guids.user_action_history_guids[24],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 24000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 24000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 24000
		},
		{
			"pk": test_guids.user_action_history_guids[25],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_EDIT.value,
			"timestamp": orderedTestDates[0].timestamp() + 25000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 25000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 25000
		},
		{
			"pk": test_guids.user_action_history_guids[26],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 26000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 26000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 26000
		},
		{
			"pk": test_guids.user_action_history_guids[27],
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 27000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 27000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 27000
		},
	]

def get_station_queue() -> list[dict[Any, Any]]:
	return [
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[1],
			"stationfk": test_guids.station_guids[2],
			"songfk": test_guids.song_guids[3],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[2],
			"stationfk": test_guids.station_guids[2],
			"songfk": test_guids.song_guids[4],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[3],
			"stationfk": test_guids.station_guids[2],
			"songfk": test_guids.song_guids[5],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[8],
			"stationfk": test_guids.station_guids[5],
			"songfk": None,
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[9],
			"stationfk": test_guids.station_guids[5],
			"songfk": None,
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[10],
			"stationfk": test_guids.station_guids[5],
			"songfk": None,
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[11],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[5],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[12],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[6],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[13],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[7],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[14],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[8],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[15],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[9],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[16],
			"stationfk": test_guids.station_guids[5],
			"songfk": test_guids.song_guids[10],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[18],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[10],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[19],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[11],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[20],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[12],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[21],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[13],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[22],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[14],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[23],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[15],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[24],
			"stationfk": test_guids.station_guids[6],
			"songfk": test_guids.song_guids[16],
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[25],
			"stationfk": test_guids.station_guids[6],
			"songfk": None,
		},
		{
			"useractionhistoryfk": test_guids.user_action_history_guids[26],
			"stationfk": test_guids.station_guids[6],
			"songfk": None,
		}
	]