from musical_chairs_libs.dtos_and_utilities import (
	TrackingInfo
)
from musical_chairs_libs.protocols import TrackingInfoProvider


class CurrentUserTrackingService(TrackingInfoProvider):

	def __init__(self, trackingInfo: TrackingInfo) -> None:
		self.__tracking_info__ = trackingInfo


	def tracking_info(self) -> TrackingInfo:
		return self.__tracking_info__