from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef
)
from sqlalchemy.engine import Connection
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.tables import (
	path_user_permissions,
)
from sqlalchemy import insert

try:
	from . import user_ids
except:
	import user_ids

def get_path_permission_params(
	datetimeProvider: MockDatetimeProvider
)  -> list[dict[Any, Any]]:
	keypathPermissions: list[dict[str, Any]] = [
		{
			"pk":1,
			"userfk": user_ids.lima_user_id,
			"keypath": "foo/goo/boo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":2,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":3,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/moo",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":4,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":5,
			"userfk": user_ids.kilo_user_id,
			"keypath": "foo/goo/shoo",
			"role": UserRoleDef.PATH_DOWNLOAD.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":6,
			"userfk": user_ids.lima_user_id,
			"keypath": "foo/goo/boo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":7,
			"userfk": user_ids.mike_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":8,
			"userfk": user_ids.mike_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":9,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":10,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":11,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":12,
			"userfk": user_ids.sierra_user_id,
			"keypath": "/foo/goo/who_1",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"quota":0, #blocked
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":13,
			"userfk": user_ids.foxtrot_user_id,
			"keypath": "/foo/goo/boo",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":1,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":14,
			"userfk": user_ids.uniform_user_id,
			"keypath": "/foo/d",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":15,
			"userfk": user_ids.uniform_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":16,
			"userfk": user_ids.station_saver_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":17,
			"userfk": user_ids.station_saver_user_id,
			"keypath": "/foo/b",
			"role": UserRoleDef.PATH_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		}
	]
	return keypathPermissions

def populate_path_permissions(
	conn: Connection,
	datetimeProvider: MockDatetimeProvider
):
	keypathPermissionParams = get_path_permission_params(datetimeProvider)
	stmt = insert(path_user_permissions)
	conn.execute(stmt, keypathPermissionParams) #pyright: ignore [reportUnknownMemberType]