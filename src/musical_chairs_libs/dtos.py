#pyright: reportMissingTypeStubs=false
import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Iterable, Set, Tuple, TypeVar, Generic
from enum import Enum
from pydantic import BaseModel, validator
from email_validator import validate_email #pyright: ignore reportUnknownVariableType



class UserRoleDef(Enum):
	ADMIN = "admin::"
	SONG_ADD = "song:add:"
	SONG_REQUEST = "song:request:"
	USER_LIST = "user:list:"

	@classmethod
	def as_set(cls) -> Set[str]:
		return {r.value for r in UserRoleDef}

	@staticmethod
	def extract_role_segments(role: str) -> Tuple[str, int]:
		match = re.search(r"(^[a-z]+:[a-z]*:)(\d+)?", role)
		if match:
			t = match.groups()
			return (t[0], int(t[1]) if t[1] else -1)
		return ("", 0)

	@staticmethod
	def remove_repeat_roles(roles: List[str]) -> Iterator[str]:
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
	def count_repeat_roles(roles: List[str]) -> dict[str, int]:
		countDict: dict[str, int] = {}
		for role in roles:
			extracted = UserRoleDef.extract_role_segments(role)
			count = countDict.get(extracted[0], 0)
			countDict[extracted[0]] = count + 1
		return countDict


T = TypeVar("T")

@dataclass
class TableData(Generic[T]):
	totalRows: int
	items: List[T]

@dataclass
class AuthenticatedAccount:
	access_token: str
	token_type: str
	username: str
	roles: List[str]
	lifetime: int

@dataclass
class AccountInfo:
	id: int
	userName: str
	hash: Optional[bytes]
	email: Optional[str]
	displayName: Optional[str]=None
	isAuthenticated: bool=False
	roles: List[str]=field(default_factory=list)

	@property
	def preferredName(self) -> str:
		return self.displayName or self.userName

	@property
	def isAdmin(self) -> bool:
		return UserRoleDef.ADMIN.value in self.roles

class SaveAccountInfo(BaseModel):
	username: str
	email: str
	password: str
	displayName: Optional[str]=None
	isNew: bool=True
	roles: List[str]=[]

	@validator("email")
	def check_email(cls, v: str) -> str:
		valid = validate_email(v) #pyright: ignore reportUnknownMemberType
		return valid.email #pyright: ignore reportUnknownMemberType

	@validator("password")
	def check_password(cls, v: str) -> str:
		minPassLen = 6
		if len(v) < minPassLen:
			raise ValueError("Password does not meet the length requirement\n"
				f"Mininum Length {minPassLen}. your password length: {len(v)}"
			)
		return v

	@validator("roles")
	def are_all_roles_allowed(cls, v: List[str]) -> List[str]:
		roleSet = UserRoleDef.as_set()
		roleCounts = UserRoleDef.count_repeat_roles(v)
		violations = { k:v for (k,v) in roleCounts.items() if v > 1 }
		if any(violations):
			keyIter = iter(violations.keys())
			key = next(keyIter)
			raise ValueError(
				f"{key} has been added {violations[key]} times "
				"but it is only legal to add it once."
			)
		for role in v:
			extracted = UserRoleDef.extract_role_segments(role)[0]
			if extracted not in roleSet:
				raise ValueError(f"{role} is an illegal role")
		return v






@dataclass
class SongItem:
	id: int
	name: str
	album: str
	artist: str


@dataclass
class QueueItem(SongItem):
	path: str
	queuedTimestamp: float
	requestedTimestamp: Optional[float]=None

@dataclass
class HistoryItem(SongItem):
	playedTimestamp: float

@dataclass
class CurrentPlayingInfo:
	nowPlaying: Optional[HistoryItem]
	items: Iterable[QueueItem]

@dataclass
class Tag:
	id: int
	name: str

@dataclass
class StationInfo:
	id: int
	name: str
	tags: Iterable[Tag]