from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	StationInfo,
	TrackingInfo
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
		user: AccountInfo,
		trackingInfo: TrackingInfo,
		stationItemType: StationRequestTypes=StationRequestTypes.PLAYLIST
	):
		...

	def remove_song_from_queue(self,
		songId: int,
		queuedTimestamp: float,
		stationId: int
	) -> Optional[CurrentPlayingInfo]:
		...

	def get_catalogue(
		self,
		stationId: int,
		page: int = 0,
		name: str = "",
		parentName: str = "",
		creator: str = "",
		limit: Optional[int]=None,
		user: Optional[AccountInfo]=None
	) -> Tuple[list[CatalogueItem], int]:
		...