from musical_chairs_libs.dtos_and_utilities import (
	EventRecord,
)
from typing import (
	Protocol,
	Optional
)


class EventsLogger(Protocol):

	def add_event_record(self, record: EventRecord):
		...


	def add_event(
		self,
		action: str,
		domain: str,
		path: Optional[str] = None,
		extraInfo: str = ""
	) -> EventRecord:
		...