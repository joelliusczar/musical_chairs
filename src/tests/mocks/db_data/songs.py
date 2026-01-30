from typing import Any
try:
	from .test_guids import song_guids
except:
	from test_guids import song_guids
try:
	from .special_strings_reference import chinese1, irish1
except:
	#for if I try to import file from interactive
	from special_strings_reference import chinese1, irish1



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
#			foo/dude/alpha_bravo/
#			foo/dude/alpha-bravo/
#			foo/dude/al%bravo/
#			foo/dude/alphajanerobravo/
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
#				jazz/overloop/spoon/bash_bang
#				jazz/overloop/spoon/bling_book
#				jazz/overloop/spoon/barn_soup
# blitz/
# 	blitz/mar/
# 		blitz/mar/wall/
# 			blitz/mar/wall/whiskey3
# 			blitz/mar/wall/xray3
# 	blitz/rhino/
# 		blitz/rhino/rhina/
# 			blitz/rhino/rhina/zulu3
#		blitz/how well are we handling/
#			blitz/how well are we handling/ünicode/
#			blitz/how well are we handling/ünicode/inourpathnames
#			blitz/how well are we handling/spaces in our/
#				blitz/how well are we handling/spaces in our/path names
#			blitz/how well are we handling/dirs ending with space  /
#				blitz/how well are we handling/dirs ending with space  /path
#		blitz/  are we handling/
#			blitz/  are we handling/ dirs beginning with space  /
#				blitz/  are we handling/ dirs beginning with space  /path
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


song_params: list[dict[str, Any]] = [
	{ "pk": 1,
		"internalpath": str(song_guids[1]),
		"treepath": "foo/goo/boo/sierra",
		"name": "sierra_song",
		"albumfk": 11,
		"track": 1,
		"discnum": 1,
		"genre": "pop",
		"explicit": 0,
		"bitrate": 144,
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 2,
		"internalpath": str(song_guids[2]),
		"treepath": "foo/goo/boo/tango",
		"name": "tango_song",
		"albumfk": 11,
		"track": 2,
		"discnum": 1,
		"genre": "pop",
		"explicit": 0,
		"bitrate": 144,
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 3,
		"internalpath": str(song_guids[3]),
		"treepath": "foo/goo/boo/uniform",
		"name": "uniform_song",
		"albumfk": 11,
		"track": 3,
		"discnum": 1,
		"genre": "pop",
		"explicit": 1,
		"bitrate": 144,
		"notes": "Kazoos make good parrallel parkers"
	},
	{ "pk": 4,
		"internalpath": str(song_guids[4]),
		"treepath": "foo/goo/boo/victor",
		"name": "victor_song",
		"albumfk": 11,
		"track": 4,
		"discnum": 1,
		"genre": "pop",
		"bitrate": 144,
		"notes": "Kazoos make bad swimmers"
	},
	{ "pk": 5,
		"internalpath": str(song_guids[5]),
		"treepath": "foo/goo/boo/victor_2",
		"name": "victor_song",
		"albumfk": 11,
		"track": 5,
		"discnum": 1,
		"genre": "pop",
		"bitrate": 144,
		"notes": "Kazoos make good hood rats"
	},
	{ "pk": 6,
		"internalpath": str(song_guids[6]),
		"treepath": "foo/goo/who_1/whiskey",
		"name": "whiskey_song",
		"albumfk": 10,
		"track": 1,
		"discnum": 1,
		"genre": "pop",
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 7,
		"internalpath": str(song_guids[7]),
		"treepath": "foo/goo/who_1/xray",
		"name": "xray_song",
		"albumfk": 10,
		"track": 2,
		"discnum": 1,
		"genre": "pop",
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 8,
		"internalpath": str(song_guids[8]),
		"treepath": "foo/goo/who_1/yankee",
		"name": "yankee_song",
		"albumfk": 10,
		"track": 3,
		"discnum": 1,
		"genre": "pop",
		"notes": "guitars make good swimmers"
	},
	{ "pk": 9,
		"internalpath": str(song_guids[9]),
		"treepath": "foo/goo/who_1/zulu",
		"name": "zulu_song",
		"albumfk": 10,
		"track": 4,
		"discnum": 1,
		"genre": "pop",
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 10,
		"internalpath": str(song_guids[10]),
		"treepath": "foo/goo/who_1/alpha",
		"name": "alpha_song",
		"albumfk": 10,
		"track": 5,
		"discnum": 1,
		"genre": "pop",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 11,
		"internalpath": str(song_guids[11]),
		"treepath": "foo/goo/who_2/bravo",
		"name": "bravo_song",
		"albumfk": 9,
		"track": 1,
		"discnum": 2,
		"genre": "pop",
		"notes": "hamburgers make flat swimmers"
	},
	{ "pk": 12,
		"internalpath": str(song_guids[12]),
		"treepath": "foo/goo/who_2/charlie",
		"name": "charlie_song",
		"albumfk": 9,
		"track": 2,
		"discnum": 2,
		"genre": "pop",
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 13,
		"internalpath": str(song_guids[13]),
		"treepath": "foo/goo/who_2/delta",
		"name": "delta_song",
		"albumfk": 9,
		"track": 3,
		"discnum": 2,
		"genre": "pop",
		"notes": "Kazoos make good swimmers"
	},
	{ "pk": 14,
		"internalpath": str(song_guids[14]),
		"treepath": "foo/goo/who_2/foxtrot",
		"name": "foxtrot_song",
		"albumfk": 9,
		"track": 4,
		"discnum": 2,
		"genre": "pop",
	},
	{ "pk": 15,
		"internalpath": str(song_guids[15]),
		"treepath": "foo/goo/who_2/golf",
		"name": "golf_song",
		"albumfk": 9,
		"track": 5,
		"discnum": 2,
		"genre": "pop",
	},
	{ "pk": 16,
		"internalpath": str(song_guids[16]),
		"treepath": "foo/goo/shoo/hotel",
		"name": "hotel_song",
		"albumfk": 8,
		"track": 1,
		"discnum": 1,
	},
	{ "pk": 17,
		"internalpath": str(song_guids[17]),
		"treepath": "foo/goo/shoo/india",
		"name": "india_song",
		"albumfk": 8,
		"track": 2,
		"discnum": 1,
	},
	{ "pk": 18,
		"internalpath": str(song_guids[18]),
		"treepath": "foo/goo/shoo/juliet",
		"name": "juliet_song",
		"albumfk": 8,
		"track": 3,
		"discnum": 1,
	},
	{ "pk": 19,
		"internalpath": str(song_guids[19]),
		"treepath": "foo/goo/shoo/kilo",
		"name": "kilo_song",
		"albumfk": 8,
		"track": 4,
		"discnum": 1,
	},
	{ "pk": 20,
		"internalpath": str(song_guids[20]),
		"treepath": "foo/goo/koo/lima",
		"name": "lima_song",
		"albumfk": 7,
		"track": 1,
	},
	{ "pk": 21,
		"internalpath": str(song_guids[21]),
		"treepath": "foo/goo/koo/mike",
		"name": "mike_song",
		"albumfk": 7,
		"track": 2,
	},
	{ "pk": 22,
		"internalpath": str(song_guids[22]),
		"treepath": "foo/goo/koo/november",
		"name": "november_song",
		"albumfk": 7,
		"track": 3,
	},
	{ "pk": 23,
		"internalpath": str(song_guids[23]),
		"treepath": "foo/goo/roo/oscar",
		"name": "oscar_song",
		"albumfk": 6,
	},
	{ "pk": 24,
		"internalpath": str(song_guids[24]),
		"treepath": "foo/goo/roo/papa",
		"name": "papa_song",
		"albumfk": 6,
	},
	{ "pk": 25,
		"internalpath": str(song_guids[25]),
		"treepath": "foo/goo/roo/romeo",
		"name": "romeo_song",
		"albumfk": 6,
	},
	{ "pk": 26,
		"internalpath": str(song_guids[26]),
		"treepath": "foo/goo/roo/sierra2",
		"name": "sierra2_song",
		"albumfk": 6,
	},
	{ "pk": 27,
		"internalpath": str(song_guids[27]),
		"treepath": "foo/goo/roo/tango2",
		"name": "tango2_song",
	},
	{ "pk": 28,
		"internalpath": str(song_guids[28]),
		"treepath": "foo/goo/roo/uniform2",
		"name": "uniform2_song",
	},
	{ "pk": 29,
		"internalpath": str(song_guids[29]),
		"treepath": "foo/goo/roo/victor2",
		"name": "victor2_song",
		"albumfk": 4,
	},
	{ "pk": 30,
		"internalpath": str(song_guids[30]),
		"treepath": "foo/goo/roo/whiskey2",
		"name": "whiskey2_song",
	},
	{ "pk": 31,
		"internalpath": str(song_guids[31]),
		"treepath": "foo/goo/roo/xray2",
		"name": "xray2_song",
	},
	{ "pk": 32,
		"internalpath": str(song_guids[32]),
		"treepath": "foo/goo/doo/yankee2",
		"name": "yankee2_song",
		"albumfk": 5,
		"genre": "bop",
		"explicit": 0,
		"bitrate": 121,
	},
	{ "pk": 33,
		"internalpath": str(song_guids[33]),
		"treepath": "foo/goo/doo/zulu2",
		"name": "zulu2_song",
		"albumfk": 5,
		"genre": "bop",
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": 34,
		"internalpath": str(song_guids[34]),
		"treepath": "foo/goo/soo/alpha2",
		"name": "alpha2_song",
		"albumfk": 4,
		"track": 1,
		"explicit": 1,
		"bitrate": 121,
	},
	{ "pk": 35,
		"internalpath": str(song_guids[35]),
		"treepath": "foo/goo/soo/bravo2",
		"name": "bravo2_song",
		"albumfk": 4,
		"track": 2,
		"explicit": 1,
	},
	{ "pk": 36,
		"internalpath": str(song_guids[36]),
		"treepath": "foo/goo/soo/charlie2",
		"name": "charlie2_song",
		"albumfk": 4,
		"track": 3,
		"notes": "Boot 'n' scoot"
	},
	{ "pk": 37,
		"internalpath": str(song_guids[37]),
		"treepath": "foo/goo/moo/delta2",
		"name": "delta2_song",
		"albumfk": 2,
		"track": 1,
	},
	{ "pk": 38,
		"internalpath": str(song_guids[38]),
		"treepath": "foo/goo/moo/echo2",
		"name": "echo2_song",
		"albumfk": 2,
		"track": 2,
	},
	{ "pk": 39,
		"internalpath": str(song_guids[39]),
		"treepath": "foo/goo/moo/foxtrot2",
		"name": "foxtrot2_song",
		"albumfk": 2,
		"track": 3,
	},
	{ "pk": 40,
		"internalpath": str(song_guids[40]),
		"treepath": "foo/goo/moo/golf2",
		"name": "golf2_song",
		"albumfk": 2,
		"track": 4,
	},
	{ "pk": 41,
		"internalpath": str(song_guids[41]),
		"treepath": "foo/goo/broo/hotel2",
		"name": "hotel2_song",
		"albumfk": 1,
	},
	{ "pk": 42,
		"internalpath": str(song_guids[42]),
		"treepath": "foo/goo/broo/india2",
		"name": "india2_song",
		"albumfk": 1,
	},
	{ "pk": 43,
		"internalpath": str(song_guids[43]),
		"treepath": "foo/goo/broo/juliet2",
		"name": "juliet2_song",
		"albumfk": 1,
	},
	{ "pk": 44,
		"internalpath": str(song_guids[44]),
		"treepath": "foo/rude/bog/kilo2",
	},
	{ "pk": 45,
		"internalpath": str(song_guids[45]),
		"treepath": "foo/rude/bog/lima2",
	},
	{ "pk": 46,
		"internalpath": str(song_guids[46]),
		"treepath": "foo/rude/rog/mike2",
	},
	{ "pk": 47,
		"internalpath": str(song_guids[47]),
		"treepath": "foo/rude/rog/november2",
	},
	{ "pk": 48,
		"name": "munchopuncho",
		"internalpath": str(song_guids[48]),
		"treepath": "foo/rude/rog/oscar2",
	},
	{ "pk": 49,
		"internalpath": str(song_guids[49]),
		"treepath": "foo/dude/dog/papa2",
	},
	{ "pk": 50,
		"internalpath": str(song_guids[50]),
		"treepath": "foo/bar/baz/romeo2",
		"name": chinese1,
	},
	{ "pk": 51,
		"internalpath": str(song_guids[51]),
		"treepath": "foo/bar/baz/sierra3",
		"name": irish1,
	},
	{ "pk": 52,
		"internalpath": str(song_guids[52]),
		"name": "tango3",
		"treepath": "jazz/rude/rog/tango3",
	},
	{ "pk": 53,
		"internalpath": str(song_guids[53]),
		"name": "uniform3",
		"treepath": "jazz/rude/rog/uniform3",
	},
	{ "pk": 54,
		"internalpath": str(song_guids[54]),
		"name": "victor3",
		"treepath": "jazz/cat/kitten/victor3",
	},
	{ "pk": 55,
		"internalpath": str(song_guids[55]),
		"name": "whiskey3",
		"treepath": "blitz/mar/wall/whiskey3",
	},
	{ "pk": 56,
		"internalpath": str(song_guids[56]),
		"name": "xray3",
		"treepath": "blitz/mar/wall/xray3",
	},
	{ "pk": 57,
		"internalpath": str(song_guids[57]),
		"name": "zulu3",
		"treepath": "blitz/rhino/rhina/zulu3",
	},
	{ "pk": 58,
		"internalpath": str(song_guids[58]),
		"name": "alpha4_song",
		"treepath": "jazz/lurk/toot/alpha4_song",
		"albumfk": 7,
	},
	{ "pk": 59,
		"internalpath": str(song_guids[59]),
		"treepath": "foo/goo/looga/alpha",
		"name": "looga_alpha_song",
		"albumfk": 14,
		"track": 5,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 60,
		"internalpath": str(song_guids[60]),
		"treepath": "tossedSlash/goo/looga/alpha",
		"name": "looga_alpha_song",
		"genre": "bam",
		"notes": "Banana Soup"
	},
	{ "pk": 61,
		"internalpath": str(song_guids[61]),
		"treepath": "tossedSlash/goo/looga/bravo",
		"name": "looga_bravo_song",
		"genre": "bam",
		"notes": "Banana Soup"
	},
	{ "pk": 62,
		"internalpath": str(song_guids[62]),
		"treepath": "tossedSlash/guess/gold/jar",
		"name": "jar_song",
		"albumfk": 14,
		"track": 5,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 63,
		"internalpath": str(song_guids[63]),
		"treepath": "tossedSlash/guess/gold/bar",
		"name": "bar_song",
		"albumfk": 14,
		"track": 6,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 64,
		"internalpath": str(song_guids[64]),
		"treepath": "tossedSlash/guess/gold/run",
		"name": "run_song",
		"albumfk": 14,
		"track": 7,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 65,
		"internalpath": str(song_guids[65]),
		"treepath": "tossedSlash/band/bun",
		"name": "bun_song",
		"albumfk": 14,
		"track": 8,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 66,
		"internalpath": str(song_guids[66]),
		"treepath": "tossedSlash/band/hun",
		"name": "hun_song",
		"albumfk": 14,
		"track": 8,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 67,
		"internalpath": str(song_guids[67]),
		"treepath": "tossedSlash/guess/silver/run",
		"name": "run_song",
		"albumfk": 14,
		"track": 7,
		"discnum": 1,
		"genre": "bam",
		"notes": "hotdogs make good lava swimmers"
	},
	{ "pk": 68,
		"internalpath": str(song_guids[68]),
		"treepath": "tossedSlash/guess/silver/plastic",
		"name": "plastic_tune",
		"albumfk": 12,
		"track": 8,
		"discnum": 1,
		"genre": "bam",
	},
	{ "pk": 69,
		"internalpath": str(song_guids[69]),
		"treepath": "tossedSlash/guess/silver/salt",
		"name": "salt_tune",
		"albumfk": 12,
		"track": 8,
		"discnum": 1,
		"genre": "bam",
	},
	{ "pk": 70,
		"internalpath": str(song_guids[70]),
		"treepath": "tossedSlash/guess/silver/green",
		"name": "green_tune",
		"albumfk": 12,
		"track": 8,
		"discnum": 1,
		"genre": "bam",
	},
	{ "pk": 71,
		"internalpath": str(song_guids[71]),
		"treepath": "tossedSlash/trap/bang(pow)_1/boo",
		"name": "grass_tune",
	},
	{ "pk": 72,
		"internalpath": str(song_guids[72]),
		"treepath": "jazz/overlap/toon/car_song",
		"name": "car_song",
	},
	{ "pk": 73,
		"internalpath": str(song_guids[73]),
		"treepath": "jazz/overlap/toon/bar_song",
		"name": "bar_song",
	},
	{ "pk": 74,
		"internalpath": str(song_guids[74]),
		"treepath": "jazz/overlaper/soon/carb_song",
		"name": "carb_song",
	},
	{ "pk": 76,
		"internalpath": str(song_guids[76]),
		"treepath": "jazz/overlaper/soon/barb_song",
		"name": "barb_song",
	},
	{ "pk": 77,
		"internalpath": str(song_guids[77]),
		"treepath": "jazz/overlaper/toon/car_song",
		"name": "car_song",
	},
	{ "pk": 78,
		"internalpath": str(song_guids[78]),
		"treepath": "jazz/overlaper/toon/bar_song",
		"name": "bar_song",
	},
	{ "pk": 79,
		"internalpath": str(song_guids[79]),
		"treepath": "jazz/overloop/spoon/cargo_song",
		"name": "cargo_song",
	},
	{ "pk": 80,
		"internalpath": str(song_guids[80]),
		"treepath": "jazz/overloop/spoon/embargo_song",
		"name": "embargo_song",
	},
	{ "pk": 81,
		"internalpath": str(song_guids[81]),
		"treepath": "blitz/how well are we handling/spaces in our/path names",
		"name": "Song with spaces",
	},
	{ "pk": 82,
		"internalpath": str(song_guids[82]),
		"treepath": "blitz/how well are we handling/dirs ending with space  /path",
		"name": "Song ending in spaces",
	},
	{ "pk": 83,
		"internalpath": str(song_guids[83]),
		"treepath": "blitz/  are we handling/ dirs beginning with space  /path",
		"name": "Song beginning in spaces",
	},
	{ "pk": 84,
		"internalpath": str(song_guids[84]),
		"treepath": "jazz/overloop/spoon/bash_bang",
		"name": "bash_bang_song",
	},
	{ "pk": 85,
		"internalpath": str(song_guids[85]),
		"treepath": "jazz/overloop/spoon/bling_book",
		"name": "bling_book_song",
	},
	{ "pk": 86,
		"internalpath": str(song_guids[86]),
		"treepath": "jazz/overloop/spoon/barn_soup",
		"name": "barn_soup_song",
	},
	{ "pk": 87,
		"internalpath": str(song_guids[87]),
		"treepath": "foo/dude/alpha_bravo/",
		"name": "underbar_song",
	},
	{ "pk": 88,
		"internalpath": str(song_guids[88]),
		"treepath": "foo/dude/alpha-bravo/",
		"name": "dash_song",
	},
	{ "pk": 89,
		"internalpath": str(song_guids[89]),
		"treepath": "foo/dude/al%bravo/",
		"name": "wild_song",
	},
	{ "pk": 90,
		"internalpath": str(song_guids[90]),
		"treepath": "foo/dude/alphajanerobravo/",
		"name": "normal_song",
	},
	{ "pk": 91,
		"internalpath": str(song_guids[91]),
		"treepath": "blitz/how well are we handling/ünicode/inourpathnames",
		"name": "Song with ünicode",
	},
]

