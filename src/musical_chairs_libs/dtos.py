#pyright: reportMissingTypeStubs=false
import re
import unicodedata
from unidecode import unidecode
from dataclasses import dataclass
from typing import\
	Any,\
	Callable,\
	Iterator,\
	List,\
	Optional,\
	Iterable,\
	Sequence,\
	Set,\
	Tuple,\
	TypeVar,\
	Generic,\
	Union
from enum import Enum
from pydantic import BaseModel, validator
from email_validator import validate_email #pyright: ignore reportUnknownVariableType
from collections import Counter
from musical_chairs_libs.simple_functions import get_duplicates


def min_length_validator_factory(
	minLen: int,
	field: str
) -> Callable[[Any, str], str]:
	def _validator(cls: Any, v: str) -> str:
		if len(v) < minLen:
			raise ValueError(f"{field} does not meet the length requirement\n"
				f"Mininum Length {minLen}. your {field.lower()} length: {len(v)}"
			)
		return v
	return _validator

class SavedNameString:

	def __init__(self, value: Optional[str]) -> None:
		self._value = self.format_name_for_save(value)

	def __str__(self) -> str:
		return self._value

	def __len__(self) -> int:
		return len(self._value)

	def __eq__(self, o: Any) -> bool:
		return self._value == o

	@staticmethod
	def format_name_for_save(value: Optional[str]) -> str:
		if not value:
			return ""
		trimed = value.strip()
		return unicodedata.normalize("NFC", trimed)

class SearchNameString:

	def __init__(self, value: Optional[str]) -> None:
		self._value = self.format_name_for_search(value)

	def __str__(self) -> str:
		return self._value

	def __len__(self) -> int:
		return len(self._value)

	def __eq__(self, o: Any) -> bool:
		return self._value == o

	@staticmethod
	def format_name_for_search(
		value: Optional[str]
	) -> str:
		if not value:
			return ""
		transformed = unidecode(value, errors="preserve")
		trimed = transformed.strip()
		lower = trimed.lower()
		return lower

class UserRoleDef(Enum):
	ADMIN = "admin::"
	SONG_EDIT = "song:edit:"
	SONG_REQUEST = "song:request:"
	TAG_DELETE = "tag:delete:"
	TAG_EDIT = "tag:edit:"
	STATION_EDIT = "station:edit:"
	STATION_DELETE = "station:delete:"
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


T = TypeVar("T")

class TableData(BaseModel, Generic[T]):
	totalRows: int
	items: List[T]

class AccountInfoBase(BaseModel):
	username: str
	displayName: str=""
	email: str
	roles: List[str]=[]

	@property
	def preferredName(self) -> str:
		return self.displayName or self.username

	@property
	def isAdmin(self) -> bool:
		return UserRoleDef.ADMIN.value in \
			(UserRoleDef.extract_role_segments(r)[0] for r in self.roles)

class AccountInfo(AccountInfoBase):
	id: int

class AuthenticatedAccount(AccountInfoBase):
	'''
	This AccountInfo is only returned after successful authentication.
	'''
	access_token: str
	token_type: str
	lifetime: int

class AccountCreationInfo(AccountInfoBase):
	'''
	This AccountInfo is only to the server to create an account.
	Password is clear text here because it hasn't been hashed yet.
	No id property because no id has been assigned yet.
	This class also has validation on several of its properties.
	'''
	password: str

	@validator("email")
	def check_email(cls, v: str) -> str:
		valid = validate_email(v) #pyright: ignore reportUnknownMemberType
		return valid.email #pyright: ignore reportUnknownMemberType

	_pass_len = validator(
		"password",
		allow_reuse=True
	)(min_length_validator_factory(6, "Password"))


	@validator("roles")
	def are_all_roles_allowed(cls, v: List[str]) -> List[str]:
		roleSet = UserRoleDef.as_set()
		duplicate = next(get_duplicates(
			UserRoleDef.extract_role_segments(r)[0] for r in v
		), None)
		if duplicate:
			raise ValueError(
				f"{duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		for role in v:
			extracted = UserRoleDef.extract_role_segments(role)[0]
			if extracted not in roleSet:
				raise ValueError(f"{role} is an illegal role")
		return v


class ErrorInfo(BaseModel):
	msg: str

@dataclass
class RoleInfo:
	userPk: int
	role: str
	creationTimestamp: float

@dataclass
class SongItem:
	id: int
	name: str
	album: str
	artist: str

@dataclass
class SongItemPlumbing:
	id: int
	path: str
	name: Optional[str]=None
	albumPk: Optional[int]=None
	artistPk: Optional[int]=None
	composerPk: Optional[int]=None
	track: Optional[int]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	sampleRate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None

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

@dataclass(eq=True, frozen=True)
class Tag:
	id: int
	name: str

@dataclass
class StationInfo:
	id: int
	name: str
	displayName: str
	tags: list[Tag]

class StationCreationInfo(BaseModel):
	name: str
	displayName: Optional[str]
	tags: Optional[List[Tag]]

	_name_len = validator(
		"name",
		allow_reuse=True
	)(min_length_validator_factory(2, "Station name"))

	@validator("tags")
	def check_tags_duplicates(cls, v: List[Tag]) -> List[Tag]:
		if not v:
			return []

		duplicate = next(get_duplicates(t.id for t in v), None)
		if duplicate:
			raise ValueError(
				f"Tag with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return v