from musical_chairs_libs.dtos_and_utilities import (
	TrackingInfo
)
from musical_chairs_libs.protocols import TrackingInfoProvider


class EmptyUserTrackingService(TrackingInfoProvider):

	def tracking_info(self) -> TrackingInfo:
		return TrackingInfo("", "", "")