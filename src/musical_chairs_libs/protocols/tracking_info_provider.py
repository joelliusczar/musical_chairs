from typing import Optional, Protocol

class TrackingInfoProvider(Protocol):

	def user_agent_id(self) -> Optional[int]:
		...