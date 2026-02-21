import uuid
from musical_chairs_libs.protocols import (
	EventsLogger,
	EventsQueryer,
	TrackingInfoProvider,
	UserProvider
)
from musical_chairs_libs.dtos_and_utilities import (
	EventRecord,
	get_datetime,
	InMemEventRecordMap,
	VisitRecord,
)
from typing import (
	Iterator,
	Optional
)


class InMemEventsLoggingService(EventsLogger, EventsQueryer):

	def __init__(
		self,
		trackingInfoProvider: TrackingInfoProvider,
		userProvider: UserProvider,
		globalStore: InMemEventRecordMap | None = None
	) -> None:
		self.get_datetime = get_datetime
		self.user_provider = userProvider
		self.tracking_info_provider = trackingInfoProvider
		if globalStore is not None:
			self.__store__ = globalStore
		else:
			self.__store__ = InMemEventRecordMap()

	def add_event_record(self, record: EventRecord):
		self.__store__\
			.userEvents[record.userId][record.sphere][record.keypath][record.action]\
			.append(record)


	def add_event(
		self,
		action: str,
		sphere: str,
		keypath: Optional[str] = None,
		extraInfo: str = ""
	) -> EventRecord:
		userId = self.user_provider.current_user().id
		visitorId = self.tracking_info_provider.visitor_id()
		url = self.tracking_info_provider.tracking_info().url
		timestamp = self.get_datetime().timestamp()
		record = EventRecord(
			id=str(uuid.uuid4()),
			userId=str(userId),
			action=action,
			visitorId=visitorId,
			timestamp=timestamp,
			keypath=keypath,
			sphere=sphere,
			url=url.path,
			extraInfo=extraInfo,
		)
		self.add_event_record(record)
		return record


	def get_user_events(
		self,
		userId: int | None,
		fromTimestamp: float,
		actions: set[str] | None = None,
		sphere: str | None = None,
		keypath: str | None = None,
		limit: int | None = None
	) -> Iterator[EventRecord]:
		eventsIter = InMemEventRecordMap.events_for_userId(
			self.__store__.userEvents,
			actions,
			keypath,
			sphere,
			str(userId)
		)
		yield from (e for i,e in enumerate(eventsIter)\
			if e.timestamp >= fromTimestamp\
			if (i < limit if limit is not None else True)
		)


	def get_visitor_events(
		self,
		visitorId: int,
		fromTimestamp: float,
		url: Optional[str] = None,
		limit: Optional[int] = None
	)-> Iterator[VisitRecord]:
		eventsIter = InMemEventRecordMap.get_visits(
			self.__store__.vistorEvents,
			visitorId,
			url
		)
		yield from (e for i,e in enumerate(eventsIter)\
			if e.timestamp >= fromTimestamp\
			if (i < limit if limit is not None else True)
		)


	def add_visit_record(self, record: VisitRecord):
		self.__store__\
			.vistorEvents[record.visitorId][record.url][record.method]\
			.append(record)


	def add_visit(self, extraInfo: str = "") -> VisitRecord:
		visitorId = self.tracking_info_provider.visitor_id()
		url = self.tracking_info_provider.tracking_info().url
		method = self.tracking_info_provider.tracking_info().method
		timestamp = self.get_datetime().timestamp()
		record = VisitRecord(
			id=str(uuid.uuid4()),
			visitorId=visitorId,
			timestamp=timestamp,
			url=url.path,
			method=method,
			extraInfo=extraInfo,
		)
		self.add_visit_record(record)
		return record
