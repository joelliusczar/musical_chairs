from musical_chairs_libs.dtos_and_utilities import (
	SimpleQueryParameters,
	StationInfo,
)
from musical_chairs_libs.dtos_and_utilities import (
	CatalogueItem,
	CurrentPlayingInfo
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationRequestTypes
)
from typing import (
	Optional,
	Protocol,
	Tuple,
)

class RadioPusher(Protocol):

	def accepted_request_types(self) -> set[StationRequestTypes]:
		...

	def add_to_queue(
		self,
		itemId: int,
		station: StationInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		...

	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		station: StationInfo,
	) -> Optional[CurrentPlayingInfo]:
		...

	def get_catalogue(
		self,
		stationId: int,
		queryParams: SimpleQueryParameters,
		name: str = "",
		parentname: str = "",
		creator: str = "",
	) -> Tuple[list[CatalogueItem], int]:
		...