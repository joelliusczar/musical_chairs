from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	RulePriorityLevel,
)
try:
	from . import user_ids
except:
	import user_ids


def get_playlist_permission_params(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:
	return [
		{
			"pk":13,
			"userfk": user_ids.juliet_user_id,
			"playlistfk": 9,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userfk": user_ids.juliet_user_id,
			"playlistfk": 5,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userfk": user_ids.hotel_user_id,
			"playlistfk": 9,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userfk": user_ids.xray_user_id,
			"playlistfk": 14,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":18,
			"userfk": user_ids.zulu_user_id,
			"playlistfk": 14,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":19,
			"userfk": user_ids.narlon_user_id,
			"playlistfk": 17,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":20,
			"userfk": user_ids.narlon_user_id,
			"playlistfk": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":22,
			"userfk": user_ids.narlon_user_id,
			"playlistfk": 18,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":24,
			"userfk": user_ids.horsetel_user_id,
			"playlistfk": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":25,
			"userfk": user_ids.george_user_id,
			"playlistfk": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":29,
			"userfk": user_ids.oomdwell_user_id,
			"playlistfk": 11,
			"role": UserRoleDef.PLAYLIST_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
	]