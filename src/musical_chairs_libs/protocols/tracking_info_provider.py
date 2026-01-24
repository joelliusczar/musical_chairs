from musical_chairs_libs.dtos_and_utilities import TrackingInfo
from typing import Protocol


class TrackingInfoProvider(Protocol):


	def tracking_info(self) -> TrackingInfo:
		...


	def visitor_id(self) -> int:
		...