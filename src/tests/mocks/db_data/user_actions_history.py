from datetime import datetime
from typing import Any, List
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
)

try:
	from . import user_ids
except:
	import user_ids


def get_actions_history(
	orderedTestDates: List[datetime]
) -> list[dict[Any, Any]]:

	return [
		{
			"pk": 1,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp(),
			"queuedtimestamp": orderedTestDates[0].timestamp(),
		},
		{
			"pk": 2,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 1000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 1000,
		},
		{
			"pk": 3,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 2000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 2000,
		},
		{
			"pk": 4,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 3000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 3000,
		},
		{
			"pk": 5,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 4000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 4000,
		},
		{
			"pk": 6,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 5000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 5000,
		},
		{
			"pk": 7,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_ASSIGN.value,
			"timestamp": orderedTestDates[0].timestamp() + 6000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 6000,
		},
		{
			"pk": 8,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 7000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 7000,
		},
		{
			"pk": 9,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 8000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 8000,
		},
		{
			"pk": 10,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 9000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 9000,
		},
		{
			"pk": 11,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 10000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 10000,
		},
		{
			"pk": 12,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 11000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 11000,
		},
		{
			"pk": 13,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 12000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 12000,
		},
		{
			"pk": 14,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 13000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 13000,
		},
		{
			"pk": 15,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 14000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 14000,
		},
		{
			"pk": 16,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 15000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 15000
		},
		{
			"pk": 17,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_CREATE.value,
			"timestamp": orderedTestDates[0].timestamp() + 16000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 16000,
		},
		{
			"pk": 18,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 18000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 18000,
		},
		{
			"pk": 19,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 19000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 19000,
		},
		{
			"pk": 20,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 20000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 20000,
		},
		{
			"pk": 21,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 21000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 21000,
		},
		{
			"pk": 22,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 22000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 22000,
		},
		{
			"pk": 23,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 23000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 23000,
		},
		{
			"pk": 24,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_REQUEST.value,
			"timestamp": orderedTestDates[0].timestamp() + 24000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 24000,
		},
		{
			"pk": 25,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_EDIT.value,
			"timestamp": orderedTestDates[0].timestamp() + 25000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 25000,
		},
		{
			"pk": 26,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 26000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 26000,
		},
		{
			"pk": 27,
			"userfk": user_ids.juliet_user_id,
			"action": UserRoleDef.STATION_FLIP.value,
			"timestamp": orderedTestDates[0].timestamp() + 27000,
			"queuedtimestamp": orderedTestDates[0].timestamp() + 27000,
		},
	]