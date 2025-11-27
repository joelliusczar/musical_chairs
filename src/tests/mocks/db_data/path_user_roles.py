from datetime import datetime
from typing import List, Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef
)
try:
	from . import user_ids
except:
	import user_ids

def get_path_permission_params(
	orderedTestDates: List[datetime]
)  -> list[dict[Any, Any]]:
	pathPermissions: list[dict[str, Any]] = [
		{
			"pk":1,
			"userfk": user_ids.lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":2,
			"userfk": user_ids.kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":3,
			"userfk": user_ids.kilo_user_id,
			"path": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":4,
			"userfk": user_ids.kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":5,
			"userfk": user_ids.kilo_user_id,
			"path": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":6,
			"userfk": user_ids.lima_user_id,
			"path": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":7,
			"userfk": user_ids.mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":8,
			"userfk": user_ids.mike_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":9,
			"userfk": user_ids.sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":10,
			"userfk": user_ids.sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":11,
			"userfk": user_ids.sierra_user_id,
			"path": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":12,
			"userfk": user_ids.sierra_user_id,
			"path": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":13,
			"userfk": user_ids.foxtrot_user_id,
			"path": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userfk": user_ids.uniform_user_id,
			"path": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":15,
			"userfk": user_ids.uniform_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userfk": user_ids.station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userfk": user_ids.station_saver_user_id,
			"path": "/foo/b",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		}
	]
	return pathPermissions
