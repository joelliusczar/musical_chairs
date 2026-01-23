from musical_chairs_libs.dtos_and_utilities import (
	TrackingInfo
)
from musical_chairs_libs.protocols import TrackingInfoProvider
from typing import Optional
from .user_agent_service import UserAgentService

class CurrentUserTrackingService(TrackingInfoProvider):

	def __init__(
		self,
		trackingInfo: TrackingInfo,
		userAgentService: UserAgentService
	) -> None:
		self.__tracking_info__ = trackingInfo
		self.user_agent_service = userAgentService


	def tracking_info(self) -> TrackingInfo:
		return self.__tracking_info__
	
	def user_agent_id(self) -> Optional[int]:
		userAgentId = self.user_agent_service.add_user_agent(
			self.__tracking_info__
		)

		return userAgentId