import dataclasses
import json
import uuid
from datetime import datetime
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	EventRecord,
	get_datetime,
)
from .events_query_service import (EventsQueryService)
from musical_chairs_libs.protocols import (
	TrackingInfoProvider,
	UserProvider
)
from typing import Callable, Optional




class EventsLoggingService(EventsQueryService):

	def __init__(
		self,
		trackingInfoProvider: TrackingInfoProvider,
		userProvider: UserProvider,
	) -> None:
		self.get_datetime = get_datetime
		self.tracking_info_provider = trackingInfoProvider
		self.user_provider = userProvider

	@staticmethod
	def current_log_name(get_datetime: Callable[[], datetime]):
		datetime = get_datetime()
		formattedDate = datetime.strftime("%Y-%j_%H:%M")
		return f"{ConfigAcessors.event_log_dir()}/{formattedDate}_events.jsonl"


	def add_user_action_history_item(
			self,
			action: str,
			domain: str,
			path: Optional[str] = None,
			extraInfo: str = ""
		):
		userId = self.user_provider.current_user().id
		userAgentId = self.tracking_info_provider.user_agent_id()
		logFileName = EventsLoggingService.current_log_name(self.get_datetime)
		with open(logFileName, "a", 1) as f:
			timestamp = self.get_datetime().timestamp()
			record = EventRecord(
				str(uuid.uuid4()),
				str(userId),
				action,
				userAgentId,
				timestamp,
				path,
				domain,
				extraInfo,
			)
			f.write(json.dumps(dataclasses.asdict(record)) + "\n")



