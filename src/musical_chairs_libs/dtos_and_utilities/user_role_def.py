from enum import Enum
from typing import (
	Union,
	Set,
	Tuple,
	Optional
)
from .type_aliases import (
	s2sDict,
	simpleDict
)
from .simple_functions import role_dict

class MinItemSecurityLevel(Enum):
	#these values should align with RulePriorityLevel
	PUBLIC = 0
	# SITE permissions should be able to overpower ANY_USER level restrictions
	ANY_USER = 9
	# ANY_STATION should be able to overpower RULED_USER
	RULED_USER = 19
	FRIEND_USER = 29 # not used
	# STATION_PATH should be able to overpower INVITED_USER
	INVITED_USER = 39
	OWENER_USER = 49
	#only admins should be able to see these items
	LOCKED = 59

class RulePriorityLevel(Enum):
	NONE = 0
	USER = 10
	SITE = 20
	FRIEND_STATION = 30
	STATION_PATH = 40
	OWNER = 50
	SUPER = 60

class UserRoleDomain(Enum):
	Site = "site"
	Station = "station"
	Path = "path"

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)


class UserRoleDef(Enum):
	ADMIN = "admin"
	SITE_USER_ASSIGN = f"{UserRoleDomain.Site.value}:userassign"
	SITE_USER_LIST = f"{UserRoleDomain.Site.value}:userlist"
	SITE_PLACEHOLDER = f"{UserRoleDomain.Site.value}:placeholder"
	USER_EDIT = f"{UserRoleDomain.Site.value}:useredit"
	SONG_EDIT = "song:edit"
	SONG_DOWNLOAD = "song:download"
	SONG_TREE_LIST = "songtree:list"
	ALBUM_EDIT = "album:edit"
	ALBUM_VIEW_ALL = "album:view_all"
	ARTIST_EDIT = "artist:edit"
	ARTIST_VIEW_ALL = "artist:view_all"
	STATION_VIEW = f"{UserRoleDomain.Station.value}:view"
	STATION_CREATE = f"{UserRoleDomain.Station.value}:create"
	STATION_EDIT = f"{UserRoleDomain.Station.value}:edit"
	STATION_DELETE = f"{UserRoleDomain.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleDomain.Station.value}:request"
	STATION_FLIP = f"{UserRoleDomain.Station.value}:flip"
	STATION_SKIP = f"{UserRoleDomain.Station.value}:skip"
	STATION_ASSIGN = f"{UserRoleDomain.Station.value}:assign"
	STATION_USER_ASSIGN = f"{UserRoleDomain.Station.value}:userassign"
	STATION_USER_LIST = f"{UserRoleDomain.Station.value}:userlist"
	USER_LIST = "user:list"
	USER_IMPERSONATE = "user:impersonate"
	PATH_LIST = f"{UserRoleDomain.Path.value}:list"
	PATH_EDIT = f"{UserRoleDomain.Path.value}:edit"
	PATH_DELETE = f"{UserRoleDomain.Path.value}:delete"
	PATH_VIEW = f"{UserRoleDomain.Path.value}:view"
	PATH_USER_ASSIGN = f"{UserRoleDomain.Path.value}:userassign"
	PATH_USER_LIST = f"{UserRoleDomain.Path.value}:userlist"
	PATH_DOWNLOAD = f"{UserRoleDomain.Path.value}:download"
	PATH_UPLOAD = f"{UserRoleDomain.Path.value}:upload"
	PATH_MOVE = f"{UserRoleDomain.Path.value}:move"

	def __call__(self, **kwargs: Union[str, int]) -> str:
		return self.modded_value(**kwargs)

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)

	@property
	def nameValue(self):
		return self.value

	@staticmethod
	def as_set(domain: Optional[str]=None) -> Set[str]:
		return {r.value for r in UserRoleDef \
			if not domain or r.value.startswith(domain)}

	@staticmethod
	def role_dict(role: str) -> s2sDict:
		return role_dict(role)

	@staticmethod
	def role_str(roleDict: simpleDict) -> str:
		return ";".join(sorted(f"{k}={v}" for k,v in roleDict.items() if v != ""))

	@staticmethod
	def extract_role_segments(role: str) -> Tuple[str, int]:
		roleDict = UserRoleDef.role_dict(role)
		if "name" in roleDict:
			nameValue = roleDict["name"]
			mod = int(roleDict["mod"]) if "mod" in roleDict else -1
			return (nameValue, mod)
		return ("", 0)

	def modded_value(
		self,
		**kwargs: Optional[Union[str, int]]
	) -> str:
		if "name" in kwargs and kwargs["name"] != self.value:
			raise RuntimeError("Name should not be provided.")
		kwargs["name"] = self.value
		return UserRoleDef.role_str(kwargs)