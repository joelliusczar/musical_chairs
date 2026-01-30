from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	RulePriorityLevel,
)
from sqlalchemy.engine import Connection
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.tables import (
	playlist_user_permissions,
)
from sqlalchemy import insert

try:
	from . import user_ids
except:
	import user_ids


def get_playlist_permission_params(
	orderedTestDates: MockDatetimeProvider
) -> list[dict[Any, Any]]:
	return [
		{
			"pk":13,
			"userfk": user_ids.juliet_user_id,
			"keypath": 9,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":14,
			"userfk": user_ids.juliet_user_id,
			"keypath": 5,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":16,
			"userfk": user_ids.hotel_user_id,
			"keypath": 9,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":17,
			"userfk": user_ids.xray_user_id,
			"keypath": 14,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":18,
			"userfk": user_ids.zulu_user_id,
			"keypath": 14,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":19,
			"userfk": user_ids.narlon_user_id,
			"keypath": 17,
			"role": UserRoleDef.PLAYLIST_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":20,
			"userfk": user_ids.narlon_user_id,
			"keypath": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":22,
			"userfk": user_ids.narlon_user_id,
			"keypath": 18,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":24,
			"userfk": user_ids.horsetel_user_id,
			"keypath": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":25,
			"userfk": user_ids.george_user_id,
			"keypath": 17,
			"role": UserRoleDef.PLAYLIST_VIEW.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
		{
			"pk":29,
			"userfk": user_ids.oomdwell_user_id,
			"keypath": 11,
			"role": UserRoleDef.PLAYLIST_USER_ASSIGN.value,
			"span":0,
			"quota":0,
			"priority": None,
			"creationtimestamp": orderedTestDates[0].timestamp()
		},
	]


def populate_playlist_permissions(
	conn: Connection,
	orderedTestDates: MockDatetimeProvider
):
	playlistPermissionParams = get_playlist_permission_params(orderedTestDates)
	stmt = insert(playlist_user_permissions)
	conn.execute(stmt, playlistPermissionParams) #pyright: ignore [reportUnknownMemberType]