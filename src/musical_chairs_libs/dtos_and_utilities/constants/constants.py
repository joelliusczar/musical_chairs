from enum import Enum
from typing import Optional

class UserActions(Enum):
	CHANGE_PASS = "change-password"
	LOGIN = "login"
	ACCOUNT_UPDATE = "account-update"
	ADD_SITE_RULE = "add-site-rule"
	REMOVE_SITE_RULE = "remove-site-rule"

class DbUsers(Enum):
	OWNER_USER = "mc_owner"
	API_USER = "api_user"
	RADIO_USER = "radio_user"
	JANITOR_USER = "janitor_user"

	def format_user(self, host:str="localhost") -> str:
		return f"'{self.value}'@'{host}'"

	def __call__(self, host:Optional[str]=None) -> str:
		if host:
			return self.format_user(host)
		return self.value
	
class JobTypes(Enum):
	SONG_DELETE = "song-delete"