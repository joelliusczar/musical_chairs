from musical_chairs_libs.dtos_and_utilities import (InternalUser)
from typing import Any, Literal, overload, Protocol

class UserProvider(Protocol):

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
		...

	def set_session_user(self, user: InternalUser):
		...


	def is_loggedIn(self) -> bool:
		...


	def optional_user_id(self) -> int | None:
		...


	def impersonate(self, user: InternalUser) -> Any:
		...