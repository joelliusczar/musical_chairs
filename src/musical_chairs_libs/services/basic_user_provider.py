from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	NotLoggedInError
)
from musical_chairs_libs.protocols import (
	UserProvider
)
from typing import (Any, Literal, Optional, overload)

class BasicUserProvider(UserProvider):

	def __init__(
		self,
		user: Optional[AccountInfo],
	) -> None:
		self.__user__ = user


	@overload
	def current_user(self) -> AccountInfo:
		...

	@overload
	def current_user(self, optional: Literal[False]) -> AccountInfo:
		...

	@overload
	def current_user(self, optional: Literal[True]) -> Optional[AccountInfo]:
		...

	def current_user(self, optional: bool=False) -> Optional[AccountInfo]:
		if self.__user__:
			return self.__user__
		if optional:
			return None
		raise NotLoggedInError(
			"User was not supplied to this instance of CurrentUserProvider"
		)
	
	def is_loggedIn(self) -> bool:
		return self.__user__ != None

	def set_user(self, user: AccountInfo):
		self.__user__ = user


	def optional_user_id(self) -> Optional[int]:
		return self.__user__.id if self.__user__ else None
	

	def impersonate(self, user: AccountInfo) -> "Impersonation":
		return Impersonation(self, user)
	


class Impersonation:

	def __init__(
		self,
		userProvider: "BasicUserProvider",
		user: AccountInfo,
	) -> None:
		self.prev_user = userProvider.current_user(optional=True)
		self.user_provider = userProvider
		self.impersonated = user

	def __enter__(
		self,
	):
		self.user_provider.__user__ = self.impersonated

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.user_provider.__user__ = self.prev_user