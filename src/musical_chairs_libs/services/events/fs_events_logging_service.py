import dataclasses
import json
import uuid
from datetime import datetime
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	EventRecord,
	get_datetime,
)
from .fs_events_query_service import (FSEventsQueryService)
from musical_chairs_libs.protocols import (
	EventsLogger,
	TrackingInfoProvider,
	UserProvider
)
from typing import Callable, Optional




class FSEventsLoggingService(EventsLogger,FSEventsQueryService):

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
		formattedDate = datetime.strftime("%Y-%j_%H")
		return f"{ConfigAcessors.event_log_dir()}/{formattedDate}_events.jsonl"


	def add_event_record(self, record: EventRecord):
		logFileName = FSEventsLoggingService.current_log_name(self.get_datetime)
		with open(logFileName, "a", 1) as f:
			
			
			f.write(json.dumps(dataclasses.asdict(record)) + "\n")


	def add_event(
		self,
		action: str,
		domain: str,
		path: Optional[str] = None,
		extraInfo: str = ""
	) -> EventRecord:
		userId = self.user_provider.current_user().id
		visitorId = self.tracking_info_provider.visitor_id()
		url = self.tracking_info_provider.tracking_info().url
		timestamp = self.get_datetime().timestamp()
		record = EventRecord(
				str(uuid.uuid4()),
				str(userId),
				action,
				visitorId,
				timestamp,
				path,
				domain,
				url,
				extraInfo,
			)
		self.add_event_record(record)
		return record

