from musical_chairs_libs.protocols import (
	TrackingInfoProvider,
	UserProvider
)
import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.services as mcr
import typing

class NonUserProvider(UserProvider, TrackingInfoProvider):

	def __init__(self) -> None:
		self.empy_user_tracking = mcr.EmptyUserTrackingService()


	@typing.overload
	def current_user(self) -> dtos.InternalUser:
		return dtos.InternalUser(
			id=0,
			publictoken="",
			username="",
			displayname="",
			email="",
			hiddentoken=""
		)


	@typing.overload
	def current_user(self, optional: typing.Literal[False]) -> dtos.InternalUser:
		return self.current_user()


	@typing.overload
	def current_user(
		self,
		optional: typing.Literal[True]
	) -> dtos.InternalUser | None:
		return self.current_user()

	def current_user(self, optional: bool=False) -> dtos.InternalUser | None:
		return self.current_user()


	def is_loggedIn(self) -> bool:
		return False
	

	def tracking_info(self) -> dtos.TrackingInfo:
		return self.empy_user_tracking.tracking_info()


	def visitor_id(self) -> int:
		return self.empy_user_tracking.visitor_id()
	

	def optional_user_id(self) -> int | None:
		return None