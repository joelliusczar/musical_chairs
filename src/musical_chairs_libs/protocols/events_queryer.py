from typing import (
	Iterator,
	Protocol
)
from musical_chairs_libs.dtos_and_utilities import (
	EventRecord,
)

class EventsQueryer(Protocol):

	def get_user_events(
		self,
		userId: int | None,
		fromTimestamp: float,
		actions: set[str] | None = None,
		sphere: str | None = None,
		keypath: str | None = None,
		limit: int | None = None
	) -> Iterator[EventRecord]:
		...


	def get_visitor_events(
		self,
		visitorId: int,
		fromTimestamp: float,
		url: str | None = None,
		limit: int | None = None
	)-> Iterator[EventRecord]:
		...