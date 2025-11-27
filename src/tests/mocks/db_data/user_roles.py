from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	RulePriorityLevel,
)
try:
	from . import user_ids
except:
	import user_ids



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
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.charlie_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 15,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 120,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.golf_user_id,
			"role": UserRoleDef.USER_LIST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.STATION_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.quebec_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":300,
			"count":15,
			"priority": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.PLAYLIST_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span": 0,
			"count": 0,
			"priority": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.PLAYLIST_CREATE.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": user_ids.tango_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value + 1
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.STATION_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"creationtimestamp": orderedTestDates[0].timestamp(),
			"span":0,
			"count":0,
			"priority": None
		},
		{
			"userfk": user_ids.november_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":10,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.lima_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.mike_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.oscar_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"count":5,
			"priority": RulePriorityLevel.STATION_PATH.value + 1,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.papa_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.alice_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":20,
			"priority": RulePriorityLevel.SITE.value - 2,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.paul_bear_user_id,
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.quirky_admin_user_id,
			"role": UserRoleDef.ADMIN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.radical_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.super_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SUPER.value,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"userfk": user_ids.unruled_station_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		}
	]