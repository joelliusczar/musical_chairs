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

class RulePriorityLevel(Enum):
	NONE = 0
	SITE = 10
	ANY_STATION = 20
	STATION_PATH = 30
	OWNER = 40
	SUPER = 50

class UserRoleDomain(Enum):
	Site = "site"
	Station = "station"
	Path = "path"

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)


class UserRoleDef(Enum):
	ADMIN = "admin"
	SONG_EDIT = "song:edit"
	SONG_DOWNLOAD = "song:download"
	SONG_TREE_LIST = "songtree:list"
	STATION_VIEW = f"{UserRoleDomain.Station.value}:view"
	STATION_CREATE = f"{UserRoleDomain.Station.value}:create"
	STATION_EDIT = f"{UserRoleDomain.Station.value}:edit"
	STATION_DELETE = f"{UserRoleDomain.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleDomain.Station.value}:request"
	STATION_FLIP = f"{UserRoleDomain.Station.value}:flip"
	STATION_SKIP = f"{UserRoleDomain.Station.value}:skip"
	STATION_ASSIGN = f"{UserRoleDomain.Station.value}:assign"
	USER_LIST = "user:list"
	USER_EDIT = "user:edit"
	USER_IMPERSONATE = "user:impersonate"
	PATH_LIST = f"{UserRoleDomain.Path.value}:list"
	PATH_EDIT = f"{UserRoleDomain.Path.value}:edit"
	PATH_VIEW = f"{UserRoleDomain.Path.value}:view"
	PATH_DOWNLOAD = f"{UserRoleDomain.Path.value}:download"

	def __call__(self, **kwargs: Union[str, int]) -> str:
		return self.modded_value(**kwargs)

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)

	@property
	def nameValue(self):
		return self.value

	@staticmethod
	def as_set() -> Set[str]:
		return {r.value for r in UserRoleDef}

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