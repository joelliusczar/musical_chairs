from musical_chairs_libs.dtos_and_utilities import (AccountInfo)
from typing import Protocol

class UserProvider(Protocol):

	def current_user(self) -> AccountInfo:
		...