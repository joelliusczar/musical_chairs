import re
from enum import Enum
from typing import\
	Optional,\
	Union,\
	Set,\
	Tuple,\
	Sequence,\
	Iterator,\
	Iterable
from collections import Counter

class UserRoleDef(Enum):
	ADMIN = "admin::"
	ARTIST_EDIT = "artist:edit:"
	SONG_EDIT = "song:edit:"
	SONG_DOWNLOAD = "song:download:"
	SONG_TREE_LIST = "songtree:list:"
	STATION_EDIT = "station:edit:"
	STATION_DELETE = "station:delete:"
	STATION_REQUEST = "station:request:"
	STATION_FLIP = "station:flip:"
	STATION_SKIP = "station:skip:"
	USER_LIST = "user:list:"
	USER_EDIT = "user:edit:"

	def __call__(self, mod: Optional[Union[str, int]]=None) -> str:
		return self.modded_value(mod)

	@staticmethod
	def as_set() -> Set[str]:
		return {r.value for r in UserRoleDef}

	@staticmethod
	def extract_role_segments(role: str) -> Tuple[str, int]:
		match = re.search(r"(^[a-z]+:[a-z]*:)(\d+)?", role)
		if match:
			t = match.groups()
			return (t[0], int(t[1]) if t[1] else -1)
		return ("", 0)

	@staticmethod
	def remove_repeat_roles(roles: Sequence[str]) -> Iterator[str]:
		if not roles or not len(roles):
			return iter(())
		rolesDict: dict[str, str] = {}
		for role in roles:
			extracted = UserRoleDef.extract_role_segments(role)
			if extracted[0] in rolesDict:
				previousRole = rolesDict[extracted[0]]
				extractedPrev = UserRoleDef.extract_role_segments(previousRole)
				if extracted[1] < extractedPrev[1]:
					rolesDict[extracted[0]] = role
			else:
				rolesDict[extracted[0]] = role
		return (r for r in rolesDict.values())

	@staticmethod
	def count_repeat_roles(roles: Iterable[str]) -> dict[str, int]:
		return Counter(UserRoleDef.extract_role_segments(r)[0] for r in roles)

	def modded_value(self, mod: Optional[Union[str, int]]=None) -> str:
		if not mod:
			return self.value
		return f"{self.value}{mod}"