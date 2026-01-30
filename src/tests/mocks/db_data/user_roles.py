from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	RulePriorityLevel,
)
from sqlalchemy.engine import Connection
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from musical_chairs_libs.tables import (
	userRoles,
)
from sqlalchemy import insert

try:
	from . import user_ids
except:
	import user_ids



def get_user_role_params(
	datetimeProvider: MockDatetimeProvider,
	primaryUser: AccountInfo,
) -> list[dict[Any, Any]]:
	return [
		{
			"userfk": primaryUser.id,
			"role": UserRoleDef.ADMIN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.charlie_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.delta_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 15,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 120,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.foxtrot_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.golf_user_id,
			"role": UserRoleDef.USER_LIST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.STATION_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.quebec_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":300,
			"quota":15,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.juliet_user_id,
			"role": UserRoleDef.PLAYLIST_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span": 0,
			"quota": 0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.bravo_user_id,
			"role": UserRoleDef.PLAYLIST_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.tango_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.india_user_id,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.hotel_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.STATION_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.whiskey_user_id,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": None,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.november_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.lima_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.mike_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.mike_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.oscar_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":120,
			"quota":5,
			"priority": RulePriorityLevel.STATION_PATH.value + 1,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.papa_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":20,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.alice_user_id,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"quota":20,
			"priority": RulePriorityLevel.SITE.value - 2,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.paul_bear_user_id,
			"role": UserRoleDef.PATH_LIST.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.quirky_admin_user_id,
			"role": UserRoleDef.ADMIN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.radical_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.super_path_user_id,
			"role": UserRoleDef.PATH_EDIT.value,
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SUPER.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.unruled_station_user_id,
			"role": UserRoleDef.STATION_CREATE.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
		{
			"userfk": user_ids.sierra_user_id,
			"role": UserRoleDef.ALBUM_EDIT.value,
			"creationtimestamp": datetimeProvider[0].timestamp(),
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.SITE.value + 1,
			"sphere": UserRoleSphere.Site.value,
			"keypath": None
		},
	]


def populate_user_roles(
	conn: Connection,
	datetimeProvider: MockDatetimeProvider,
	primaryUser: AccountInfo,
):
	userRoleParams = get_user_role_params(datetimeProvider, primaryUser)
	stmt = insert(userRoles)
	conn.execute(stmt, userRoleParams) #pyright: ignore [reportUnknownMemberType]