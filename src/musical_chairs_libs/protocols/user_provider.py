from musical_chairs_libs.dtos_and_utilities import (AccountInfo)
from typing import Literal, Optional, overload, Protocol

class UserProvider(Protocol):

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
		...

	def is_loggedIn(self) -> bool:
		...