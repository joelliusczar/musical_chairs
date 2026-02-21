from musical_chairs_libs.protocols import TrackingInfoProvider
from musical_chairs_libs.dtos_and_utilities import TrackingInfo
from starlette.datastructures import URL


class EmptyUserTrackingService(TrackingInfoProvider):

	def tracking_info(self) -> TrackingInfo:
		return TrackingInfo(URL())
	
	def visitor_id(self) -> int:
		return 0