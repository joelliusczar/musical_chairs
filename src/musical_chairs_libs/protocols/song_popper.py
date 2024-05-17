from typing import (
	Optional,
	Protocol,
	Tuple
)

class SongPopper(Protocol):

	def pop_next_queued(
		self,
		stationId: int
	) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
		...