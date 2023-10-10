from pydantic import validator, root_validator #pyright: ignore [reportUnknownVariableType]
from pydantic.dataclasses import dataclass as pydanticDataclass
from dataclasses import dataclass, field
from typing import (
	Iterator,
	Optional,
	Iterable,
	List,
	Any
)
from itertools import chain
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates, get_non_simple_chars
from .generic_dtos import IdItem, TableData, T
from .account_dtos import OwnerType
from .action_rule_dtos import ActionRule, PathsActionRule
from .user_role_def import MinItemSecurityLevel


@dataclass(frozen=True)
class ArtistInfo:
	id: int
	name: str
	owner: OwnerType

@dataclass(frozen=True)
class AlbumCreationInfo:
	name: str
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None

@dataclass(frozen=True)
class AlbumInfo(IdItem):
	name: str
	owner: OwnerType
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None

@dataclass()
class SongBase:
	id: int
	name: str

@dataclass()
class SongListDisplayItem(SongBase):
	album: Optional[str]
	artist: Optional[str]
	path: str
	queuedtimestamp: float
	requestedtimestamp: Optional[float]=None
	playedtimestamp: Optional[float]=None
	rules: list[ActionRule]=field(default_factory=list)


@dataclass(frozen=True)
class ScanningSongItem:
	id: int
	path: str
	name: Optional[str]=None
	albumId: Optional[int]=None
	artistId: Optional[int]=None
	composerId: Optional[int]=None
	track: Optional[str]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	samplerate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None




@dataclass()
class StationTableData(TableData[T]):
	stationrules: list[ActionRule]

@dataclass()
class CurrentPlayingInfo(StationTableData[SongListDisplayItem]):
	nowplaying: Optional[SongListDisplayItem]

@dataclass(frozen=True)
class Tag:
	id: int
	name: str

@dataclass(unsafe_hash=True)
class StationInfo:
	id: int
	name: str
	displayname: str=field(default="", hash=False, compare=False)
	isrunning: bool=field(default=False, hash=False, compare=False)
	#don't expect this to ever actually null
	owner: Optional[OwnerType]=field(default=None, hash=False, compare=False)
	rules: list[ActionRule]=field(
		default_factory=list, hash=False, compare=False
	)
	requestsecuritylevel: Optional[int]=field(
		default=MinItemSecurityLevel.ANY_USER.value, hash=False, compare=False,
	)
	viewsecuritylevel: Optional[int]=field(default=0, hash=False, compare=False)

@dataclass()
class StationCreationInfo:
	name: str
	displayname: Optional[str]=""
	viewsecuritylevel: Optional[int]=field(default=0)
	requestsecuritylevel: Optional[int]=field(
		default=MinItemSecurityLevel.OWENER_USER.value
	)

	@validator("requestsecuritylevel")
	def check_requestSecurityLevel(cls, v: int, values: dict[Any, Any]) -> int:
		if v < values["viewsecuritylevel"] \
			or v == MinItemSecurityLevel.PUBLIC.value:
			raise ValueError(
				"Request Security cannot be public or lower than view security"
			)
		return v

@pydanticDataclass
class ValidatedStationCreationInfo(StationCreationInfo):

	_name_len = validator( #pyright: ignore [reportUnknownVariableType]
		"name",
		allow_reuse=True
	)(min_length_validator_factory(2, "Station name"))

	@validator("name")
	def check_name_for_illegal_chars(cls, v: str) -> str:
		if not v:
			return ""

		m = get_non_simple_chars(v)
		if m:
			raise ValueError(f"Illegal character used in station name: {m}")
		return v


@dataclass(frozen=True)
class SongTreeNode:
	path: str
	totalChildCount: int
	id: Optional[int]=None
	name: Optional[str]=None
	rules: list[PathsActionRule]=field(
		default_factory=list, hash=False, compare=False
	)

@dataclass()
class SongArtistGrouping:
	songId: int
	artists: List[ArtistInfo]=field(default_factory=list)

	def __iter__(self) -> Iterator[ArtistInfo]:
		return iter(self.artists or [])

@dataclass(frozen=True)
class StationSongTuple:
	songid: int
	stationid: int
	islinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songid
		yield self.stationid

@dataclass(frozen=True)
class SongArtistTuple:
	songid: int
	artistid: int
	isprimaryartist: bool=False
	islinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[int]:
		yield self.songid
		yield self.artistid

@dataclass()
class SongTagGrouping:
	songid: int
	tags: List[Tag]=field(default_factory=list)

	def __iter__(self) -> Iterator[Tag]:
		return iter(self.tags or [])

@dataclass()
class SongPathInfo:
	id: int
	path: str

@dataclass()
class SongAboutInfo:
	name: Optional[str]=None
	album: Optional[AlbumInfo]=None
	primaryartist: Optional[ArtistInfo]=None
	artists: Optional[list[ArtistInfo]]=field(default_factory=list)
	covers: Optional[list[int]]=field(default_factory=list)
	track: Optional[str]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	samplerate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None
	lyrics: Optional[str]=""
	stations: Optional[list[StationInfo]]=field(default_factory=list)
	touched: Optional[set[str]]=None

	@property
	def allArtists(self) -> Iterable[ArtistInfo]:
		if self.primaryartist:
			yield self.primaryartist
		yield from (a for a in self.artists or [])

@dataclass()
class SongEditInfo(SongAboutInfo, SongPathInfo):
	rules: list[ActionRule]=field(default_factory=list)



@pydanticDataclass
class ValidatedSongAboutInfo(SongAboutInfo):

	@validator("stations")
	def check_tags_duplicates(cls, v: List[StationInfo]) -> List[StationInfo]:
		if not v:
			return []

		duplicate = next(get_duplicates(t.id for t in v), None)
		if duplicate:
			raise ValueError(
				f"Station with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return v

	@root_validator
	def root_validator(cls, values: dict[Any, Any]) -> Any:
		artists = values.get("artists", [])
		primaryArtist = values.get("primaryartist", None)

		duplicate = next(get_duplicates(
			a.id for a in chain(artists, (primaryArtist,) if primaryArtist else ())),
			None
		)
		if duplicate:
			raise ValueError(
				f"Artist with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return values