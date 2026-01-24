from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	RulePriorityLevel,
)
from sqlalchemy.engine import Connection
from ..mock_datetime_provider import MockDatetimeProvider
from musical_chairs_libs.tables import (
	station_user_permissions,
)
from sqlalchemy import insert
try:
	from . import user_ids
except:
	import user_ids


def get_station_permission_params(
	datetimeProvider: MockDatetimeProvider
) -> list[dict[Any, Any]]:
	return [
		{
			"pk":1,
			"userfk": user_ids.kilo_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":4,
			"userfk": user_ids.mike_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":6,
			"userfk": user_ids.november_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":5,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":8,
			"userfk": user_ids.oscar_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":60,
			"count":5,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":10,
			"userfk": user_ids.papa_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":12,
			"userfk": user_ids.quebec_user_id,
			"stationfk": 3,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":300,
			"count":25,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":13,
			"userfk": user_ids.juliet_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":14,
			"userfk": user_ids.juliet_user_id,
			"stationfk": 5,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":15,
			"userfk": user_ids.juliet_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":16,
			"userfk": user_ids.hotel_user_id,
			"stationfk": 9,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":17,
			"userfk": user_ids.xray_user_id,
			"stationfk": 14,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":18,
			"userfk": user_ids.zulu_user_id,
			"stationfk": 14,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value - 5,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":19,
			"userfk": user_ids.narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":20,
			"userfk": user_ids.narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":21,
			"userfk": user_ids.narlon_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":5,
			"count":300,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":22,
			"userfk": user_ids.narlon_user_id,
			"stationfk": 18,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":23,
			"userfk": user_ids.narlon_user_id,
			"stationfk": 18,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":100,
			"count":300,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":24,
			"userfk": user_ids.horsetel_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":25,
			"userfk": user_ids.george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":26,
			"userfk": user_ids.george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_REQUEST.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":27,
			"userfk": user_ids.george_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":28,
			"userfk": user_ids.carl_user_id,
			"stationfk": 17,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":70,
			"count":10,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":29,
			"userfk": user_ids.oomdwell_user_id,
			"stationfk": 11,
			"role": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
		{
			"pk":30,
			"userfk": user_ids.unruled_station_user_id,
			"stationfk": 20,
			"role": UserRoleDef.STATION_FLIP.value,
			"span":0,
			"count":0,
			"priority": None,
			"creationtimestamp": datetimeProvider[0].timestamp()
		},
	]


def populate_station_permissions(
	conn: Connection,
	datetimeProvider: MockDatetimeProvider
):
	stationPermissionParams = get_station_permission_params(datetimeProvider)
	stmt = insert(station_user_permissions)
	conn.execute(stmt, stationPermissionParams) #pyright: ignore [reportUnknownMemberType]