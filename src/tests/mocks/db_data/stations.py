from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	MinItemSecurityLevel
)

try:
	from . import user_ids
except:
	import user_ids


station_params: list[dict[str, Any]] = [
	{ "pk": 1,
		"name": "oscar_station",
		"displayname": "Oscar the grouch",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 2,
		"name": "papa_station",
		"displayname": "Come to papa",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 3,
		"name": "romeo_station",
		"displayname": "But soft, what yonder wind breaks",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 4,
		"name": "sierra_station",
		"displayname": "The greatest lie the devil ever told",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 5,
		"name": "tango_station",
		"displayname": "Nuke the whales",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 6,
		"name": "yankee_station",
		"displayname": "Blurg the blergos",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 7,
		"name": "uniform_station",
		"displayname": "Asshole at the wheel",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 8,
		"name": "victor_station",
		"displayname": "Fat, drunk, and stupid",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 9,
		"name": "whiskey_station",
		"displayname": "Chris-cross apple sauce",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 10,
		"name": "xray_station",
		"displayname": "Pentagular",
		"ownerfk": user_ids.bravo_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 11,
		"name": "zulu_station",
		"displayname": "Hammer time",
		"ownerfk": user_ids.juliet_user_id,
		"viewsecuritylevel": None
	},
	{ "pk": 12,
		"name": "alpha_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": user_ids.victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.RULED_USER.value
	},
	{ "pk": 13,
		"name": "bravo_station_rerun",
		"displayname": "We rerun again and again",
		"ownerfk": user_ids.victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.ANY_USER.value
	},
	{ "pk": 14,
		"name": "charlie_station_rerun",
		"displayname": "The Wide World of Sports",
		"ownerfk": user_ids.victor_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 15,
		"name": "delta_station_rerun",
		"displayname": "Dookie Dan strikes again",
		"ownerfk": user_ids.yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 16,
		"name": "foxtrot_station_rerun",
		"displayname": "fucked six ways to Sunday",
		"ownerfk": user_ids.yankee_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.LOCKED.value
	},
	{ "pk": 17,
		"name": "golf_station_rerun",
		"displayname": "goliath bam bam",
		"ownerfk": user_ids.ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 18,
		"name": "hotel_station_rerun",
		"displayname": "hella cool radio station",
		"ownerfk": user_ids.ingo_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 19,
		"name": "india_station_rerun",
		"displayname": "bitchingly fast!",
		"ownerfk": user_ids.station_saver_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 20,
		"name": "juliet_station_rerun",
		"displayname": "Neptune, how could you?",
		"ownerfk": user_ids.unruled_station_user_id,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	},
	{ "pk": 21,
		"name": "kilo_station_rerun",
		"displayname": "kilo bam",
		"ownerfk": user_ids.jazzDirOwnerId,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 22,
		"name": "lima_station_rerun",
		"displayname": "Peruvian nuts",
		"ownerfk": user_ids.jazzDirOwnerId,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 23,
		"name": "mike_station_rerun",
		"displayname": "Milk",
		"ownerfk": user_ids.jazzDirOwnerId,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 24,
		"name": "november_station_rerun",
		"displayname": "Nancy",
		"ownerfk": user_ids.jazzDirOwnerId,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	},
	{ "pk": 25,
		"name": "oscar_station_rerun",
		"displayname": "oodle laylee",
		"ownerfk": user_ids.jazzDirOwnerId,
		"viewsecuritylevel": MinItemSecurityLevel.OWENER_USER.value
	}
]