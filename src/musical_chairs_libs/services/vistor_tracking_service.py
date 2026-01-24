from musical_chairs_libs.dtos_and_utilities import (
	TrackingInfo
)
from musical_chairs_libs.protocols import TrackingInfoProvider
from .visitor_service import VisitorService

class VisitorTrackingService(TrackingInfoProvider):

	def __init__(
		self,
		trackingInfo: TrackingInfo,
		visitorService: VisitorService
	) -> None:
		self.__tracking_info__ = trackingInfo
		self.visitor_service = visitorService


	def tracking_info(self) -> TrackingInfo:
		return self.__tracking_info__


	def visitor_id(self) -> int:
		visitorId = self.visitor_service.add_visitor(
			self.__tracking_info__
		)

		return visitorId