from pydantic import (
	field_validator,
	ValidationInfo,
	Field,
)
from typing import (
	Optional,
	Any,
	Iterator,
)
from .simple_functions import get_non_simple_chars
from .validation_functions import min_length_validator_factory
from .generic_dtos import (
	MCBaseClass,
	RuledEntity
)
from .account_dtos import OwnerType
from .user_role_def import RulePriorityLevel
from .constants.constants import StationTypes

class StationInfo(RuledEntity):
	id: int=Field(frozen=True)
	name: str=Field(frozen=True)
	displayname: str=Field(default="", frozen=False)
	isrunning: bool=Field(default=False, frozen=False)
	#don't expect this to ever actually null
	owner: Optional[OwnerType]=Field(default=None, frozen=False)
	requestsecuritylevel: Optional[int]=Field(
		default=RulePriorityLevel.ANY_USER.value, frozen=False
	)
	typeid: int=Field(default=StationTypes.SONGS_ONLY.value)
	bitratekps: Optional[int]=Field(default=None)

	playnum: int=Field(default=1)


	def __hash__(self) -> int:
		return hash((self.id, self.name, self.typeid))
	
	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.id == other.id \
			and self.name == other.name \
			and self.typeid == other.typeid


class StationCreationInfo(MCBaseClass):
	name: str
	displayname: Optional[str]=""
	viewsecuritylevel: Optional[int]=Field(default=0)
	requestsecuritylevel: Optional[int]=Field(
		default=RulePriorityLevel.OWENER_USER.value
	)
	typeid: int=Field(default=StationTypes.SONGS_ONLY.value)
	bitratekps: Optional[int]=Field(default=None)
	playnum: int=Field(default=1)

	@field_validator("requestsecuritylevel")
	@classmethod
	def check_requestSecurityLevel(
		cls,
		v: int,
		validationInfo: ValidationInfo
	) -> int:
		if v < validationInfo.data["viewsecuritylevel"] \
			or v == RulePriorityLevel.PUBLIC.value:
			raise ValueError(
				"Request Security cannot be public or lower than view security"
			)
		return v


class ValidatedStationCreationInfo(StationCreationInfo):

	_name_len = field_validator(
		"name"
	)(min_length_validator_factory(2, "Station name"))

	@field_validator("name")
	@classmethod
	def check_name_for_illegal_chars(cls, v: str) -> str:
		if not v:
			return ""

		m = get_non_simple_chars(v)
		if m:
			raise ValueError(f"Illegal character used in station name: {m}")
		return v
	
class StationSongTuple:

	def __init__(
		self,
		songid: int,
		stationid: Optional[int],
		islinked: bool=False
	) -> None:
		self.songid = songid
		self.stationid = stationid
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songid
		yield self.stationid

	def __hash__(self) -> int:
		return hash((self.songid, self.stationid))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.songid == other.songid \
			and self.stationid == other.stationid

	def __str__(self) -> str:
		return f"(songid={self.songid}, stationid={self.stationid})"
	
	def __repr__(self) -> str:
		return str(self)
	
class StationAlbumTuple:

	def __init__(
		self,
		albumid: int,
		stationid: Optional[int],
		islinked: bool=False
	) -> None:
		self.albumid = albumid
		self.stationid = stationid
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Optional[int]]:
		yield self.albumid
		yield self.stationid

	def __hash__(self) -> int:
		return hash((self.albumid, self.stationid))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.albumid == other.albumid \
			and self.stationid == other.stationid
	
	def __str__(self) -> str:
		return f"(albumid={self.albumid}, stationid={self.stationid})"
	
	def __repr__(self) -> str:
		return str(self)


class StationPlaylistTuple:

	def __init__(
		self,
		playlistid: int,
		stationid: Optional[int],
		islinked: bool=False
	) -> None:
		self.playlistid = playlistid
		self.stationid = stationid
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Optional[int]]:
		yield self.playlistid
		yield self.stationid

	def __hash__(self) -> int:
		return hash((self.playlistid, self.stationid))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.playlistid == other.playlistid \
			and self.stationid == other.stationid
	
	def __str__(self) -> str:
		return f"(playlistid={self.playlistid}, stationid={self.stationid})"
	
	def __repr__(self) -> str:
		return str(self)