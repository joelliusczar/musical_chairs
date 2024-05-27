from musical_chairs_libs.dtos_and_utilities import (
	SongListDisplayItem
)
from typing import (
	Optional,
	Protocol,
	Set
)

class SongPopper(Protocol):

	def pop_next_queued(
		self,
		stationId: int,
		loaded: Optional[Set[SongListDisplayItem]]=None
	) -> SongListDisplayItem:
		...

	def move_from_queue_to_history(
		self,
		stationId: int,
		songId: int,
		queueTimestamp: float
	) -> bool:
		...