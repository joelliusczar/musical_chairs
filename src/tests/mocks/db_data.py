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
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 2,
		"name": "bravo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 3,
		"name": "charlie_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 4,
		"name": "delta_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 5,
		"name": "echo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 6,
		"name": "foxtrot_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 7,
		"name": "golf_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 8,
		"name": "hotel_artist",
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 9,
		"name": "india_artist",
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 10,
		"name": "juliet_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 11,
		"name": "kilo_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 12,
		"name": "lima_artist",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 13,
		"name": "november_artist",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 14,
		"name": "oscar_artist",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 15,
		"name": "papa_artist",
		"ownerfk": november_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 16,
		"name": "romeo_artist",
		"ownerfk": india_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
	{
		"pk": 17,
		"name": "sierra_artist",
		"ownerfk": hotel_user_id,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
	},
]

albumParams1 = [
	{
		"pk": 1,
		"name": "broo_album",
		"albumartistfk": 7,
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 2,
		"name": "moo_album",
		"albumartistfk": 7,
		"year": 2003,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 8,
		"name": "shoo_album",
		"albumartistfk": 6,
		"year": 2003,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 9,
		"name": "who_2_album",
		"albumartistfk": 6,
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 10,
		"name": "who_1_album",
		"albumartistfk": 5,
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 11,
		"name": "boo_album",
		"albumartistfk": 4,
		"year": 2001,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams2 = [
	{
		"pk": 4,
		"name": "soo_album",
		"year": 2004,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 7,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 13,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": jazzDirOwnerId,
		"lastmodifiedbyuserfk": jazzDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams3 = [
	{
		"pk": 5,
		"name": "doo_album",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 6,
		"name": "roo_album",
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 12,
		"name": "garoo_album",
		"ownerfk": blitzDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	}
]

albumParams4 = [
	{
		"pk": 3,
		"name": "juliet_album",
		"albumartistfk": 7,
		"ownerfk": fooDirOwnerId,
		"lastmodifiedbyuserfk": fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 14,
		"name": "grunt_album",
		"ownerfk": juliet_user_id,
		"albumartistfk": 7,
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

# foo/
# 	foo/goo/
# 		foo/goo/boo/
# 			foo/goo/boo/sierra
# 			foo/goo/boo/tango
# 			foo/goo/boo/uniform
# 			foo/goo/boo/victor
# 			foo/goo/boo/victor_2
# 		foo/goo/who_1/
# 			foo/goo/who_1/whiskey
# 			foo/goo/who_1/xray
# 			foo/goo/who_1/yankee
# 			foo/goo/who_1/zulu
# 			foo/goo/who_1/alpha
# 		foo/goo/who_2/
# 			foo/goo/who_2/bravo
# 			foo/goo/who_2/charlie
# 			foo/goo/who_2/delta
# 			foo/goo/who_2/foxtrot
# 			foo/goo/who_2/golf
# 		foo/goo/shoo/
# 			foo/goo/shoo/hotel
# 			foo/goo/shoo/india
# 			foo/goo/shoo/juliet
# 			foo/goo/shoo/kilo
# 		foo/goo/koo/
# 			foo/goo/koo/lima
# 			foo/goo/koo/mike
# 			foo/goo/koo/november
# 		foo/goo/roo/
# 			foo/goo/roo/oscar
# 			foo/goo/roo/papa
# 			foo/goo/roo/romeo
# 			foo/goo/roo/sierra2
# 			foo/goo/roo/tango2
# 			foo/goo/roo/uniform2
# 			foo/goo/roo/victor2
# 			foo/goo/roo/whiskey2
# 			foo/goo/roo/xray2
# 		foo/goo/doo/
# 			foo/goo/doo/yankee2
# 			foo/goo/doo/zulu2
# 		foo/goo/soo/
# 			foo/goo/soo/alpha2
# 			foo/goo/soo/bravo2
# 			foo/goo/soo/charlie2
# 		foo/goo/moo/
# 			foo/goo/moo/delta2
# 			foo/goo/moo/echo2
# 			foo/goo/moo/foxtrot2
# 			foo/goo/moo/golf2
# 		foo/goo/broo/
# 			foo/goo/broo/hotel2
# 			foo/goo/broo/india2
# 			foo/goo/broo/juliet2
# 		foo/goo/looga/
# 			foo/goo/looga/alpha
# 	foo/rude/
# 		foo/rude/bog/
# 			foo/rude/bog/kilo2
# 			foo/rude/bog/lima2
# 		foo/rude/rog/
# 			foo/rude/rog/mike2
# 			foo/rude/rog/november2
# 			foo/rude/rog/oscar2
# 	foo/dude/
# 		foo/dude/dog/
# 			foo/dude/dog/papa2
# 	foo/bar/
# 		foo/bar/baz/
# 			foo/bar/baz/romeo2
# 			foo/bar/baz/sierra3
# jazz/
# 	jazz/rude/
# 		jazz/rude/rog/
# 			jazz/rude/rog/tango3
# 			jazz/rude/rog/uniform3
# 	jazz/cat/
# 		jazz/cat/kitten/
# 			jazz/cat/kitten/victor3
# 	jazz/lurk/
# 		jazz/lurk/toot/
# 			jazz/lurk/toot/alpha4_song
#		jazz/overlap/
#			jazz/overlap/toon
#				jazz/overlap/toon/car_song
#				jazz/overlap/toon/bar_song
#		jazz/overlaper/
#			jazz/overlaper/soon
#				jazz/overlaper/soon/carb_song
#				jazz/overlaper/soon/barb_song
#			jazz/overlaper/toon
#				jazz/overlaper/toon/car_song
#				jazz/overlaper/toon/bar_song
#		jazz/overloop/
#			jazz/overloop/spoon
#				jazz/overloop/spoon/cargo_song
#				jazz/overloop/spoon/embargo_song
# blitz/
# 	blitz/mar/
# 		blitz/mar/wall/
# 			blitz/mar/wall/whiskey3
# 			blitz/mar/wall/xray3
# 	blitz/rhino/
# 		blitz/rhino/rhina/
# 			blitz/rhino/rhina/zulu3
#		blitz/how well are we handing/
#			blitz/how well are we handing/spaces in our/
#				blitz/how well are we handing/spaces in our/path names
#		blitz/how well are we handing/
#			blitz/how well are we handing/dirs ending with space  /
#				blitz/how well are we handing/dirs ending with space  /path
#		blitz/  are we handling/
#			blitz/  are we handling/ dirs beginning with space  /
#				blitz/  are we handling/ dirs beginning with space  /path"
# tossedSlash/
# 	tossedSlash/goo/
# 		tossedSlash/goo/looga/
# 			tossedSlash/goo/looga/alpha
# 			tossedSlash/goo/looga/bravo
# 	tossedSlash/guess/
# 		tossedSlash/guess/gold/
# 			tossedSlash/guess/gold/jar
# 			tossedSlash/guess/gold/bar
# 			tossedSlash/guess/gold/run
# 		tossedSlash/guess/silver/
# 			tossedSlash/guess/silver/run
# 			tossedSlash/guess/silver/plastic
# 			tossedSlash/guess/silver/salt
# 			tossedSlash/guess/silver/green
# 	tossedSlash/band
# 		tossedSlash/band/bun
# 		tossedSlash/band/hun
# 	tossedSlash/trap/
# 		tossedSlash/trap/bang(pow)_1
# 			tossedSlash/trap/bang(pow)_1/boo


song_params = [
	{ "pk": 1,
		"path": "foo/goo/boo/sierra",
		"name": "sierra_song",
		"albumfk": 11,
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
		"albumfk": 11,
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
		"albumfk": 11,
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
		"albumfk": 11,
		"track": 4,
		"disc": 1,
		"genre": "pop",
		"bitrate": 144,
		"comment": "Kazoos make bad swimmers"
	},
	{ "pk": 5,
		"path": "foo/goo/boo/victor_2",
		"name": "victor_song",
		"albumfk": 11,
		"track": 5,
		"disc": 1,
		"genre": "pop",
		"bitrate": 144,
		"comment": "Kazoos make good hood rats"
	},
	{ "pk": 6,
		"path": "foo/goo/who_1/whiskey",
		"name": "whiskey_song",
		"albumfk": 10,
		"track": 1,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": 7,
		"path": "foo/goo/who_1/xray",
		"name": "xray_song",
		"albumfk": 10,
		"track": 2,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": 8,
		"path": "foo/goo/who_1/yankee",
		"name": "yankee_song",
		"albumfk": 10,
		"track": 3,
		"disc": 1,
		"genre": "pop",
		"comment": "guitars make good swimmers"
	},
	{ "pk": 9,
		"path": "foo/goo/who_1/zulu",
		"name": "zulu_song",
		"albumfk": 10,
		"track": 4,
		"disc": 1,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": 10,
		"path": "foo/goo/who_1/alpha",
		"name": "alpha_song",
		"albumfk": 10,
		"track": 5,
		"disc": 1,
		"genre": "pop",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 11,
		"path": "foo/goo/who_2/bravo",
		"name": "bravo_song",
		"albumfk": 9,
		"track": 1,
		"disc": 2,
		"genre": "pop",
		"comment": "hamburgers make flat swimmers"
	},
	{ "pk": 12,
		"path": "foo/goo/who_2/charlie",
		"name": "charlie_song",
		"albumfk": 9,
		"track": 2,
		"disc": 2,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": 13,
		"path": "foo/goo/who_2/delta",
		"name": "delta_song",
		"albumfk": 9,
		"track": 3,
		"disc": 2,
		"genre": "pop",
		"comment": "Kazoos make good swimmers"
	},
	{ "pk": 14,
		"path": "foo/goo/who_2/foxtrot",
		"name": "foxtrot_song",
		"albumfk": 9,
		"track": 4,
		"disc": 2,
		"genre": "pop",
	},
	{ "pk": 15,
		"path": "foo/goo/who_2/golf",
		"name": "golf_song",
		"albumfk": 9,
		"track": 5,
		"disc": 2,
		"genre": "pop",
	},
	{ "pk": 16,
		"path": "foo/goo/shoo/hotel",
		"name": "hotel_song",
		"albumfk": 8,
		"track": 1,
		"disc": 1,
	},
	{ "pk": 17,
		"path": "foo/goo/shoo/india",
		"name": "india_song",
		"albumfk": 8,
		"track": 2,
		"disc": 1,
	},
	{ "pk": 18,
		"path": "foo/goo/shoo/juliet",
		"name": "juliet_song",
		"albumfk": 8,
		"track": 3,
		"disc": 1,
	},
	{ "pk": 19,
		"path": "foo/goo/shoo/kilo",
		"name": "kilo_song",
		"albumfk": 8,
		"track": 4,
		"disc": 1,
	},
	{ "pk": 20,
		"path": "foo/goo/koo/lima",
		"name": "lima_song",
		"albumfk": 7,
		"track": 1,
	},
	{ "pk": 21,
		"path": "foo/goo/koo/mike",
		"name": "mike_song",
		"albumfk": 7,
		"track": 2,
	},
	{ "pk": 22,
		"path": "foo/goo/koo/november",
		"name": "november_song",
		"albumfk": 7,
		"track": 3,
	},
	{ "pk": 23,
		"path": "foo/goo/roo/oscar",
		"name": "oscar_song",
		"albumfk": 6,
	},
	{ "pk": 24,
		"path": "foo/goo/roo/papa",
		"name": "papa_song",
		"albumfk": 6,
	},
	{ "pk": 25,
		"path": "foo/goo/roo/romeo",
		"name": "romeo_song",
		"albumfk": 6,
	},
	{ "pk": 26,
		"path": "foo/goo/roo/sierra2",
		"name": "sierra2_song",
		"albumfk": 6,
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
		"albumfk": 4,
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
		"albumfk": 5,
		"genre": "bop",
		"explicit": 0,
		"bitrate": 121,
	},
	{ "pk": 33,
		"path": "foo/goo/doo/zulu2",
		"name": "zulu2_song",
		"albumfk": 5,
		"genre": "bop",
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": 34,
		"path": "foo/goo/soo/alpha2",
		"name": "alpha2_song",
		"albumfk": 4,
		"track": 1,
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": 35,
		"path": "foo/goo/soo/bravo2",
		"name": "bravo2_song",
		"albumfk": 4,
		"track": 2,
		"explicit": 1,
	},
	{ "pk": 36,
		"path": "foo/goo/soo/charlie2",
		"name": "charlie2_song",
		"albumfk": 4,
		"track": 3,
		"comment": "Boot 'n' scoot"
	},
	{ "pk": 37,
		"path": "foo/goo/moo/delta2",
		"name": "delta2_song",
		"albumfk": 2,
		"track": 1,
	},
	{ "pk": 38,
		"path": "foo/goo/moo/echo2",
		"name": "echo2_song",
		"albumfk": 2,
		"track": 2,
	},
	{ "pk": 39,
		"path": "foo/goo/moo/foxtrot2",
		"name": "foxtrot2_song",
		"albumfk": 2,
		"track": 3,
	},
	{ "pk": 40,
		"path": "foo/goo/moo/golf2",
		"name": "golf2_song",
		"albumfk": 2,
		"track": 4,
	},
	{ "pk": 41,
		"path": "foo/goo/broo/hotel2",
		"name": "hotel2_song",
		"albumfk": 1,
	},
	{ "pk": 42,
		"path": "foo/goo/broo/india2",
		"name": "india2_song",
		"albumfk": 1,
	},
	{ "pk": 43,
		"path": "foo/goo/broo/juliet2",
		"name": "juliet2_song",
		"albumfk": 1,
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
		"albumfk": 7,
	},
	{ "pk": 59,
		"path": "foo/goo/looga/alpha",
		"name": "looga_alpha_song",
		"albumfk": 14,
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
		"albumfk": 14,
		"track": 5,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 63,
		"path": "tossedSlash/guess/gold/bar",
		"name": "bar_song",
		"albumfk": 14,
		"track": 6,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 64,
		"path": "tossedSlash/guess/gold/run",
		"name": "run_song",
		"albumfk": 14,
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 65,
		"path": "tossedSlash/band/bun",
		"name": "bun_song",
		"albumfk": 14,
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 66,
		"path": "tossedSlash/band/hun",
		"name": "hun_song",
		"albumfk": 14,
		"track": 8,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 67,
		"path": "tossedSlash/guess/silver/run",
		"name": "run_song",
		"albumfk": 14,
		"track": 7,
		"disc": 1,
		"genre": "bam",
		"comment": "hotdogs make good lava swimmers"
	},
	{ "pk": 68,
		"path": "tossedSlash/guess/silver/plastic",
		"name": "plastic_tune",
		"albumfk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": 69,
		"path": "tossedSlash/guess/silver/salt",
		"name": "salt_tune",
		"albumfk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": 70,
		"path": "tossedSlash/guess/silver/green",
		"name": "green_tune",
		"albumfk": 12,
		"track": 8,
		"disc": 1,
		"genre": "bam",
	},
	{ "pk": 71,
		"path": "tossedSlash/trap/bang(pow)_1/boo",
		"name": "grass_tune",
	},
	{ "pk": 72,
		"path": "jazz/overlap/toon/car_song",
		"name": "car_song",
	},
	{ "pk": 73,
		"path": "jazz/overlap/toon/bar_song",
		"name": "bar_song",
	},
	{ "pk": 74,
		"path": "jazz/overlaper/soon/carb_song",
		"name": "carb_song",
	},
	{ "pk": 75,
		"path": "jazz/overlaper/soon/barb_song",
		"name": "barb_song",
	},
	{ "pk": 76,
		"path": "jazz/overlaper/soon/barb_song",
		"name": "barb_song",
	},
	{ "pk": 77,
		"path": "jazz/overlaper/toon/car_song",
		"name": "car_song",
	},
	{ "pk": 78,
		"path": "jazz/overlaper/toon/bar_song",
		"name": "bar_song",
	},
	{ "pk": 79,
		"path": "jazz/overloop/spoon/cargo_song",
		"name": "cargo_song",
	},
	{ "pk": 80,
		"path": "jazz/overloop/spoon/embargo_song",
		"name": "embargo_song",
	},
	{ "pk": 81,
		"path": "blitz/how well are we handing/spaces in our/path names",
		"name": "Song with spaces",
	},
	{ "pk": 82,
		"path": "blitz/how well are we handing/dirs ending with space  /path",
		"name": "Song ending in spaces",
	},
	{ "pk": 83,
		"path": "blitz/  are we handling/ dirs beginning with space  /path",
		"name": "Song beginning in spaces",
	}
]

songArtistParams = [
	{ "pk": 1, "songfk": 40, "artistfk": 7 },
	{ "pk": 2, "songfk": 39, "artistfk": 7 },
	{ "pk": 3, "songfk": 38, "artistfk": 7 },
	{ "pk": 4, "songfk": 37, "artistfk": 7 },
	{ "pk": 5, "songfk": 36, "artistfk": 2 },
	{ "pk": 6, "songfk": 35, "artistfk": 1 },
	{ "pk": 7, "songfk": 34, "artistfk": 3 },
	{ "pk": 8, "songfk": 33, "artistfk": 4 },
	{ "pk": 9, "songfk": 32, "artistfk": 4 },
	{ "pk": 10, "songfk": 31, "artistfk": 5 },
	{ "pk": 11, "songfk": 30, "artistfk": 5 },
	{ "pk": 12, "songfk": 29, "artistfk": 6 },
	{ "pk": 13, "songfk": 28, "artistfk": 6 },
	{ "pk": 14, "songfk": 27, "artistfk": 6 },
	{ "pk": 15, "songfk": 26, "artistfk": 6 },
	{ "pk": 16, "songfk": 25, "artistfk": 6 },
	{ "pk": 17, "songfk": 24, "artistfk": 6 },
	{ "pk": 18, "songfk": 23, "artistfk": 6 },
	{ "pk": 19, "songfk": 22, "artistfk": 2 },
	{ "pk": 20, "songfk": 21, "artistfk": 2 },
	{ "pk": 21, "songfk": 20, "artistfk": 2 },
	{ "pk": 22, "songfk": 19, "artistfk": 6 },
	{ "pk": 23, "songfk": 18, "artistfk": 6 },
	{ "pk": 24, "songfk": 17, "artistfk": 6 },
	{ "pk": 25, "songfk": 16, "artistfk": 6 },
	{ "pk": 26, "songfk": 15, "artistfk": 6 },
	{ "pk": 27, "songfk": 14, "artistfk": 6 },
	{ "pk": 28, "songfk": 13, "artistfk": 6 },
	{ "pk": 29, "songfk": 12, "artistfk": 6 },
	{ "pk": 30, "songfk": 11, "artistfk": 6 },
	{ "pk": 31, "songfk": 10, "artistfk": 5 },
	{ "pk": 32, "songfk": 9, "artistfk": 5 },
	{ "pk": 33, "songfk": 8, "artistfk": 5 },
	{ "pk": 34, "songfk": 7, "artistfk": 5 },
	{ "pk": 35, "songfk": 6, "artistfk": 5 },
	{ "pk": 36, "songfk": 5, "artistfk": 4 },
	{ "pk": 37, "songfk": 4, "artistfk": 4 },
	{ "pk": 38, "songfk": 3, "artistfk": 4 },
	{ "pk": 39, "songfk": 2, "artistfk": 4 },
	{ "pk": 40, "songfk": 1, "artistfk": 4 },
	{ "pk": 45, "songfk": 21, "artistfk": 4 },
	{ "pk": 46, "songfk": 21, "artistfk": 6 },
	{ "pk": 47, "songfk": 17, "artistfk": 10 },
	{ "pk": 48, "songfk": 17, "artistfk": 5 },
	{ "pk": 49, "songfk": 17, "artistfk": 2 },
	{ "pk": 50, "songfk": 17, "artistfk": 11 },
	{ "pk": 51, "songfk": 35, "artistfk": 12 },
	{ "pk": 52, "songfk": 59, "artistfk": 16 },
	{ "pk": 54, "songfk": 59, "artistfk": 17 },
]

songArtistParams2 = [
	{ "pk": 41, "songfk": 43, "artistfk": 7, "isprimaryartist": 1 },
	{ "pk": 42, "songfk": 42, "artistfk": 7, "isprimaryartist": 1 },
	{ "pk": 43, "songfk": 41, "artistfk": 7, "isprimaryartist": 1 },
	{ "pk": 44, "songfk": 1, "artistfk": 6, "isprimaryartist": 1 },
	{ "pk": 53, "songfk": 59, "artistfk": 15, "isprimaryartist": 1 },
]

songArtistParamsAll = [*songArtistParams, *songArtistParams2]

station_params = [
	{ "pk": 1,
		"name": "oscar_station",
		"displayname": "Oscar the grouch",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 2,
		"name": "papa_station",
		"displayname": "Come to papa",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 3,
		"name": "romeo_station",
		"displayname": "But soft, what yonder wind breaks",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 4,
		"name": "sierra_station",
		"displayname": "The greatest lie the devil ever told",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 5,
		"name": "tango_station",
		"displayname": "Nuke the whales",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 6,
		"name": "yankee_station",
		"displayname": "Blurg the blergos",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 7,
		"name": "uniform_station",
		"displayname": "Asshole at the wheel",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 8,
		"name": "victor_station",
		"displayname": "Fat, drunk, and stupid",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 9,
		"name": "whiskey_station",
		"displayname": "Chris-cross apple sauce",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 10,
		"name": "xray_station",
		"displayname": "Pentagular",
		"ownerfk": bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 11,
		"name": "zulu_station",
		"displayname": "Hammer time",
		"ownerfk": juliet_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 12,
		"name": "alpha_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.RULED_USER.value
	},
	{ "pk": 13,
		"name": "bravo_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.ANY_USER.value
	},
	{ "pk": 14,
		"name": "charlie_station_rerun",
		"displayname": "The Wide World of Sports",
		"ownerfk": victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 15,
		"name": "delta_station_rerun",
		"displayname": "Dookie Dan strikes again",
		"ownerfk": yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 16,
		"name": "foxtrot_station_rerun",
		"displayname": "fucked six ways to Sunday",
		"ownerfk": yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.LOCKED.value
	},
	{ "pk": 17,
		"name": "golf_station_rerun",
		"displayname": "goliath bam bam",
		"ownerfk": ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 18,
		"name": "hotel_station_rerun",
		"displayname": "hella cool radio station",
		"ownerfk": ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 19,
		"name": "india_station_rerun",
		"displayname": "bitchingly fast!",
		"ownerfk": station_saver_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 20,
		"name": "juliet_station_rerun",
		"displayname": "Neptune, how could you?",
		"ownerfk": unruled_station_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	}
]

stationSongParams = [
	{ "songfk": 43, "stationfk": 1 },
	{ "songfk": 43, "stationfk": 2 },
	{ "songfk": 43, "stationfk": 3 },
	{ "songfk": 41, "stationfk": 2 },
	{ "songfk": 40, "stationfk": 2 },
	{ "songfk": 38, "stationfk": 2 },
	{ "songfk": 37, "stationfk": 2 },
	{ "songfk": 36, "stationfk": 3 },
	{ "songfk": 35, "stationfk": 4 },
	{ "songfk": 34, "stationfk": 3 },
	{ "songfk": 33, "stationfk": 4 },
	{ "songfk": 32, "stationfk": 4 },
	{ "songfk": 31, "stationfk": 2 },
	{ "songfk": 30, "stationfk": 1 },
	{ "songfk": 29, "stationfk": 1 },
	{ "songfk": 28, "stationfk": 1 },
	{ "songfk": 27, "stationfk": 3 },
	{ "songfk": 26, "stationfk": 3 },
	{ "songfk": 25, "stationfk": 3 },
	{ "songfk": 24, "stationfk": 3 },
	{ "songfk": 23, "stationfk": 1 },
	{ "songfk": 22, "stationfk": 2 },
	{ "songfk": 21, "stationfk": 1 },
	{ "songfk": 20, "stationfk": 2 },
	{ "songfk": 19, "stationfk": 1 },
	{ "songfk": 18, "stationfk": 1 },
	{ "songfk": 17, "stationfk": 1 },
	{ "songfk": 17, "stationfk": 3 },
	{ "songfk": 16, "stationfk": 3 },
	{ "songfk": 15, "stationfk": 4 },
	{ "songfk": 15, "stationfk": 1 },
	{ "songfk": 14, "stationfk": 4 },
	{ "songfk": 13, "stationfk": 4 },
	{ "songfk": 12, "stationfk": 1 },
	{ "songfk": 11, "stationfk": 3 },
	{ "songfk": 10, "stationfk": 2 },
	{ "songfk": 9, "stationfk": 1 },
	{ "songfk": 8, "stationfk": 2 },
	{ "songfk": 7, "stationfk": 1 },
	{ "songfk": 6, "stationfk": 3 },
	{ "songfk": 5, "stationfk": 2 },
	{ "songfk": 4, "stationfk": 4 },
	{ "songfk": 3, "stationfk": 1 },
	{ "songfk": 2, "stationfk": 1 },
	{ "songfk": 1, "stationfk": 2 },
	{ "songfk": 1, "stationfk": 6 },
	{ "songfk": 4, "stationfk": 6 },
	{ "songfk": 50, "stationfk": 6 },
	{ "songfk": 44, "stationfk": 8 },
	{ "songfk": 45, "stationfk": 8 },
	{ "songfk": 46, "stationfk": 8 },
	{ "songfk": 47, "stationfk": 8 },
	{ "songfk": 59, "stationfk": 10 },
	{ "songfk": 59, "stationfk": 11 },
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
			"pk":1,
			"userfk": kilo_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userfk": mike_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":6,
			"userfk": november_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":5,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userfk": oscar_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"count":5,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userfk": papa_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userfk": quebec_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":13,
			"userfk": juliet_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userfk": juliet_user_id,
			"stationfk": 5,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":15,
			"userfk": juliet_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userfk": hotel_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userfk": xray_user_id,
			"stationfk": 14,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":18,
			"userfk": zulu_user_id,
			"stationfk": 14,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":19,
			"userfk": narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":20,
			"userfk": narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":21,
			"userfk": narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":5,
			"count":300,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":22,
			"userfk": narlon_user_id,
			"stationfk": 18,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":23,
			"userfk": narlon_user_id,
			"stationfk": 18,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":100,
			"count":300,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":24,
			"userfk": horsetel_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":25,
			"userfk": george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":26,
			"userfk": george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":27,
			"userfk": george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":28,
			"userfk": carl_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":29,
			"userfk": oomdwell_user_id,
			"stationfk": 11,
			"role": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":30,
			"userfk": unruled_station_user_id,
			"stationfk": 20,
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
			"pk":1,
			"userfk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":2,
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":3,
			"userfk": kilo_user_id,
			"path": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":5,
			"userfk": kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":6,
			"userfk": lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":7,
			"userfk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userfk": mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":9,
			"userfk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userfk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":11,
			"userfk": sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userfk": sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":13,
			"userfk": foxtrot_user_id,
			"path": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userfk": uniform_user_id,
			"path": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":15,
			"userfk": uniform_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userfk": station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
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
			"pk": 1,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp(),
			"queuedtimestamp": orderedTestDates[0].timestamp(),
			"requestedtimestamp":orderedTestDates[0].timestamp()
		},
		{
			"pk": 2,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 1000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 1000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 1000
		},
		{
			"pk": 3,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 2000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 2000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 2000
		},
		{
			"pk": 4,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 3000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 3000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 3000
		},
		{
			"pk": 5,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 4000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 4000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 4000
		},
		{
			"pk": 6,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 5000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 5000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 5000
		},
		{
			"pk": 7,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 6000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 6000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 6000
		},
		{
			"pk": 8,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 7000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 7000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 7000
		},
		{
			"pk": 9,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 8000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 8000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 8000
		},
		{
			"pk": 10,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 9000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 9000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 9000
		},
		{
			"pk": 11,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 10000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 10000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 10000
		},
		{
			"pk": 12,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 11000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 11000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 11000
		},
		{
			"pk": 13,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 12000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 12000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 12000
		},
		{
			"pk": 14,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 13000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 13000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 13000
		},
		{
			"pk": 15,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 14000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 14000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 14000
		},
		{
			"pk": 16,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 15000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 15000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 15000
		},
		{
			"pk": 17,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 16000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 16000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 16000
		},
		{
			"pk": 18,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 18000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 18000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 18000
		},
		{
			"pk": 19,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 19000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 19000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 19000
		},
		{
			"pk": 20,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 20000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 20000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 20000
		},
		{
			"pk": 21,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 21000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 21000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 21000
		},
		{
			"pk": 22,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 22000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 22000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 22000
		},
		{
			"pk": 23,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 23000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 23000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 23000
		},
		{
			"pk": 24,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 24000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 24000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 24000
		},
		{
			"pk": 25,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_EDIT.value,
			"timestamp": orderedTestDates[0].timestamp() + 25000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 25000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 25000
		},
		{
			"pk": 26,
			"userfk": juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 26000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 26000,
			"requestedtimestamp":orderedTestDates[0].timestamp() + 26000
		},
		{
			"pk": 27,
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
			"useractionhistoryfk": 1,
			"stationfk": 2,
			"songfk": 3,
		},
		{
			"useractionhistoryfk": 2,
			"stationfk": 2,
			"songfk": 4,
		},
		{
			"useractionhistoryfk": 3,
			"stationfk": 2,
			"songfk": 5,
		},
		{
			"useractionhistoryfk": 8,
			"stationfk": 5,
			"songfk": None,
		},
		{
			"useractionhistoryfk": 9,
			"stationfk": 5,
			"songfk": None,
		},
		{
			"useractionhistoryfk": 10,
			"stationfk": 5,
			"songfk": None,
		},
		{
			"useractionhistoryfk": 11,
			"stationfk": 5,
			"songfk": 5,
		},
		{
			"useractionhistoryfk": 12,
			"stationfk": 5,
			"songfk": 6,
		},
		{
			"useractionhistoryfk": 13,
			"stationfk": 5,
			"songfk": 7,
		},
		{
			"useractionhistoryfk": 14,
			"stationfk": 5,
			"songfk": 8,
		},
		{
			"useractionhistoryfk": 15,
			"stationfk": 5,
			"songfk": 9,
		},
		{
			"useractionhistoryfk": 16,
			"stationfk": 5,
			"songfk": 10,
		},
		{
			"useractionhistoryfk": 18,
			"stationfk": 6,
			"songfk": 10,
		},
		{
			"useractionhistoryfk": 19,
			"stationfk": 6,
			"songfk": 11,
		},
		{
			"useractionhistoryfk": 20,
			"stationfk": 6,
			"songfk": 12,
		},
		{
			"useractionhistoryfk": 21,
			"stationfk": 6,
			"songfk": 13,
		},
		{
			"useractionhistoryfk": 22,
			"stationfk": 6,
			"songfk": 14,
		},
		{
			"useractionhistoryfk": 23,
			"stationfk": 6,
			"songfk": 15,
		},
		{
			"useractionhistoryfk": 24,
			"stationfk": 6,
			"songfk": 16,
		},
		{
			"useractionhistoryfk": 25,
			"stationfk": 6,
			"songfk": None,
		},
		{
			"useractionhistoryfk": 26,
			"stationfk": 6,
			"songfk": None,
		}
	]