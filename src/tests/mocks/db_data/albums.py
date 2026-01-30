from typing import Any
try:
	from . import user_ids
except:
	import user_ids

albumParams1: list[dict[str, Any]] = [
	{
		"pk": 1,
		"name": "broo_album",
		"albumartistfk": 7,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "broo_album".casefold()
	},
	{
		"pk": 2,
		"name": "moo_album",
		"albumartistfk": 7,
		"year": 2003,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "moo_album".casefold()
	},
	{
		"pk": 8,
		"name": "shoo_album",
		"albumartistfk": 6,
		"year": 2003,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "shoo_album".casefold()
	},
	{
		"pk": 9,
		"name": "who_2_album",
		"albumartistfk": 6,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "who_2_album".casefold()
	},
	{
		"pk": 10,
		"name": "who_1_album",
		"albumartistfk": 5,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "who_1_album".casefold()
	},
	{
		"pk": 11,
		"name": "boo_album",
		"albumartistfk": 4,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "boo_album".casefold()
	},
]

albumParams2: list[dict[str, Any]] = [
	{
		"pk": 4,
		"name": "soo_album",
		"year": 2004,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "soo_album".casefold()
	},
	{
		"pk": 7,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "koo_album".casefold()
	},
	{
		"pk": 13,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": user_ids.jazzDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.jazzDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "koo_album".casefold()
	},
]

albumParams3: list[dict[str, Any]] = [
	{
		"pk": 5,
		"name": "doo_album",
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "doo_album".casefold()
	},
	{
		"pk": 6,
		"name": "roo_album",
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "roo_album".casefold()
	},
	{
		"pk": 12,
		"name": "garoo_album",
		"ownerfk": user_ids.blitzDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "garoo_album".casefold()
	}
]

albumParams4: list[dict[str, Any]] = [
	{
		"pk": 3,
		"name": "juliet_album",
		"albumartistfk": 7,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "juliet_album".casefold()
	},
	{
		"pk": 14,
		"name": "grunt_album",
		"ownerfk": user_ids.juliet_user_id,
		"albumartistfk": 7,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0,
		"flatname": "grunt_album".casefold()
	},
]


album_params = [
	*albumParams1,
	*albumParams2,
	*albumParams3,
	*albumParams4
]