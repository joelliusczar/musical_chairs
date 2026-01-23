from musical_chairs_libs.protocols import TrackingInfoProvider
from typing import Optional


class EmptyUserTrackingService(TrackingInfoProvider):

	
	def user_agent_id(self) -> Optional[int]:
		return None