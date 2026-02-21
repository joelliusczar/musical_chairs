from musical_chairs_libs.dtos_and_utilities import (
	EventRecord,
	VisitRecord
)
from typing import (
	Protocol
)


class EventsLogger(Protocol):

	def add_event_record(self, record: EventRecord):
		...


	def add_event(
		self,
		action: str,
		sphere: str,
		keypath: str | None = None,
		extraInfo: str = ""
	) -> EventRecord:
		...


	def add_visit_record(self, record: VisitRecord):
		...


	def add_visit(self, extraInfo: str = "") -> VisitRecord:
		...

