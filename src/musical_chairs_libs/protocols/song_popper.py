from musical_chairs_libs.dtos_and_utilities import (
	StreamQueuedItem
)
from typing import (
	Protocol,
	Set
)

class SongPopper(Protocol):

	def pop_next_queued(
		self,
		stationId: int,
		loaded: Set[StreamQueuedItem] | None=None
	) -> StreamQueuedItem | None:
		...

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> bool:
		...