from datetime import datetime
from typing import Any
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
)

try:
	from . import user_ids
except:
	import user_ids

def get_station_queue(
	baseDate: datetime
) -> list[dict[Any, Any]]:
	baseTimestamp = baseDate.timestamp()
	queue: list[dict[str, Any]] = [
		{
			"pk": 1,
			"stationfk": 2,
			"songfk": 3,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 2,
			"stationfk": 2,
			"songfk": 4,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 3,
			"stationfk": 2,
			"songfk": 5,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 8,
			"stationfk": 5,
			"songfk": None,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 9,
			"stationfk": 5,
			"songfk": None,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 10,
			"stationfk": 5,
			"songfk": None,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 11,
			"stationfk": 5,
			"songfk": 5,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 12,
			"stationfk": 5,
			"songfk": 6,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 13,
			"stationfk": 5,
			"songfk": 7,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 14,
			"stationfk": 5,
			"songfk": 8,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 15,
			"stationfk": 5,
			"songfk": 9,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 16,
			"stationfk": 5,
			"songfk": 10,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 18,
			"stationfk": 6,
			"songfk": 10,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 19,
			"stationfk": 6,
			"songfk": 11,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 20,
			"stationfk": 6,
			"songfk": 12,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 21,
			"stationfk": 6,
			"songfk": 13,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 22,
			"stationfk": 6,
			"songfk": 14,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 23,
			"stationfk": 6,
			"songfk": 15,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 24,
			"stationfk": 6,
			"songfk": 16,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 25,
			"stationfk": 6,
			"songfk": None,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		},
		{
			"pk": 26,
			"stationfk": 6,
			"songfk": None,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
		}
	]
	for i, entry in enumerate(queue):
		entry["timestamp"] = baseTimestamp + i * 1000
		entry["queuedtimestamp"] = baseTimestamp + i * 1000
	return queue