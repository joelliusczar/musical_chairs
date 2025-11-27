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
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 2,
		"name": "moo_album",
		"albumartistfk": 7,
		"year": 2003,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 8,
		"name": "shoo_album",
		"albumartistfk": 6,
		"year": 2003,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 9,
		"name": "who_2_album",
		"albumartistfk": 6,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 10,
		"name": "who_1_album",
		"albumartistfk": 5,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 11,
		"name": "boo_album",
		"albumartistfk": 4,
		"year": 2001,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams2: list[dict[str, Any]] = [
	{
		"pk": 4,
		"name": "soo_album",
		"year": 2004,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 7,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 13,
		"name": "koo_album",
		"year": 2010,
		"ownerfk": user_ids.jazzDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.jazzDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

albumParams3: list[dict[str, Any]] = [
	{
		"pk": 5,
		"name": "doo_album",
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 6,
		"name": "roo_album",
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 12,
		"name": "garoo_album",
		"ownerfk": user_ids.blitzDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	}
]

albumParams4: list[dict[str, Any]] = [
	{
		"pk": 3,
		"name": "juliet_album",
		"albumartistfk": 7,
		"ownerfk": user_ids.fooDirOwnerId,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
	{
		"pk": 14,
		"name": "grunt_album",
		"ownerfk": user_ids.juliet_user_id,
		"albumartistfk": 7,
		"lastmodifiedbyuserfk": user_ids.fooDirOwnerId,
		"lastmodifiedtimestamp": 0
	},
]

album_params = [
	*albumParams1,
	*albumParams2,
	*albumParams3,
	*albumParams4
]