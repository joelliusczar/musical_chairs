from musical_chairs_libs.dtos_and_utilities import (
	InternalUser,
	NotLoggedInError
)
from musical_chairs_libs.protocols import (
	UserProvider
)
from typing import (Literal, Optional, overload)
from contextlib import contextmanager

class BasicUserProvider(UserProvider):

	def __init__(
		self,
		user: InternalUser | None,
	) -> None:
		self.__user__ = user


	@overload
	def current_user(self) -> InternalUser:
		...

	@overload
	def current_user(self, optional: Literal[False]) -> InternalUser:
		...

	@overload
	def current_user(self, optional: Literal[True]) -> InternalUser | None:
		...

	def current_user(self, optional: bool=False) -> InternalUser | None:
		if self.__user__:
			return self.__user__
		if optional:
			return None
		raise NotLoggedInError(
			"User was not supplied to this instance of CurrentUserProvider"
		)


	def is_loggedIn(self) -> bool:
		return self.__user__ != None


	def set_user(self, user: InternalUser):
		self.__user__ = user


	def optional_user_id(self) -> Optional[int]:
		return self.__user__.id if self.__user__ else None
	

	@contextmanager
	def impersonate(self, user: InternalUser):
		prev_user = self.__user__
		self.__user__ = user
		yield
		self.__user__ = prev_user
