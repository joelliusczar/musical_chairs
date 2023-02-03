from enum import Enum
from typing import (
	Union,
	Set,
	Tuple,
	Sequence,
	Iterator,
	Iterable,
	Optional
)
from collections import Counter
from .type_aliases import (
	s2sDict,
	simpleDict
)

def _kvpSplit(kvp: str) -> Tuple[str, str]:
	eqSplit = kvp.split("=")
	if len(eqSplit) < 2:
		return "name", kvp
	return eqSplit[0], eqSplit[1]

class UserRoleDef(Enum):
	ADMIN = "admin"
	SONG_EDIT = "song:edit"
	SONG_DOWNLOAD = "song:download"
	SONG_TREE_LIST = "songtree:list"
	STATION_EDIT = "station:edit"
	STATION_DELETE = "station:delete"
	STATION_REQUEST = "station:request"
	STATION_FLIP = "station:flip"
	STATION_SKIP = "station:skip"
	USER_LIST = "user:list"
	USER_EDIT = "user:edit"

	def __call__(self, **kwargs: Union[str, int]) -> str:
		return self.modded_value(**kwargs)

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.nameValue)

	@property
	def nameValue(self):
		return f"name={self.value}"

	@staticmethod
	def as_set() -> Set[str]:
		return {r.value for r in UserRoleDef}

	@staticmethod
	def role_dict(role: str) -> s2sDict:
		return {p[0]:p[1] for p in (_kvpSplit(k) for k in role.split(";"))}

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

	@staticmethod
	def remove_repeat_roles(roles: Sequence[str]) -> Iterator[str]:
		if not roles or not len(roles):
			return iter(())
		roleDupChecker: dict[str, s2sDict] = {}
		for role in roles:
			roleDict = UserRoleDef.role_dict(role)
			if roleDict["name"] in roleDupChecker:
				previousRoleDict = roleDupChecker[roleDict["name"]]
				if int(roleDict.get("span",0)) < int(previousRoleDict.get("span",0)):
					roleDupChecker[roleDict["name"]] = roleDict
			else:
				roleDupChecker[roleDict["name"]] = roleDict
		return (UserRoleDef.role_str(r) for r in roleDupChecker.values())

	@staticmethod
	def count_repeat_roles(roles: Iterable[str]) -> dict[str, int]:
		return Counter(UserRoleDef.role_dict(r)['name'] for r in roles)

	def modded_value(
		self,
		**kwargs: Optional[Union[str, int]]
	) -> str:
		if "name" in kwargs and kwargs["name"] != self.value:
			raise RuntimeError("Name should not be provided.")
		kwargs["name"] = self.value
		return UserRoleDef.role_str(kwargs)