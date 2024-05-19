from musical_chairs_libs.dtos_and_utilities import (
	SongListDisplayItem
)
from typing import (
	Protocol
)

class SongPopper(Protocol):

	def pop_next_queued(
		self,
		stationId: int,
		offset: int=0
	) -> SongListDisplayItem:
		...

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> bool:
		...