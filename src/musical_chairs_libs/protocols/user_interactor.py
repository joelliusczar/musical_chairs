from typing import Protocol
from .tracking_info_provider import TrackingInfoProvider
from .user_provider import UserProvider

class UserInteractor(TrackingInfoProvider, UserProvider, Protocol):

	pass