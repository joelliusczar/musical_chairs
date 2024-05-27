import os
from pydantic import (
	field_validator,
	model_validator,
	ValidationInfo,
	Field
)
from typing import (
	Iterator,
	Optional,
	Iterable,
	List,
	Any,
)
from itertools import chain
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates, get_non_simple_chars
from .generic_dtos import (
	FrozenIdItem,
	TableData,
	T,
	FrozenBaseClass,
	MCBaseClass,
	NamedIdItem,
	FrozenNamed,
	FrozenNamedIdItem,
	IdItem
)
from .account_dtos import OwnerType
from .action_rule_dtos import ActionRule, PathsActionRule
from .user_role_def import MinItemSecurityLevel
from pathlib import Path



class ArtistInfo(FrozenNamedIdItem):
	owner: OwnerType

class AlbumCreationInfo(FrozenNamed):
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None

class AlbumInfo(FrozenNamedIdItem):
	owner: OwnerType
	year: Optional[int]=None
	albumartist: Optional[ArtistInfo]=None

class QueuedItem(NamedIdItem):
	queuedtimestamp: float=Field(frozen=True)

	def __hash__(self) -> int:
		return hash((self.id, self.name, self.queuedtimestamp))
	
	def __eq__(self, value: Any) -> bool:
		if not value:
			return False
		return self.id == value.id \
			and self.name == value.name \
			and self.queuedtimestamp == value.queuedtimestamp

class SongListDisplayItem(QueuedItem):
	album: Optional[str]
	artist: Optional[str]
	path: str
	playedtimestamp: Optional[float]=None
	rules: list[ActionRule]=Field(default_factory=list, frozen=False)

	def display(self) -> str:	
		if self.name:
				display = f"{self.name} - {self.album} - {self.artist}"
		else:
			display = os.path.splitext(os.path.split(self.path)[1])[0]
		return display.replace("\n", "")


class ScanningSongItem(FrozenIdItem):
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



class StationTableData(TableData[T]):
	stationrules: list[ActionRule]


class CurrentPlayingInfo(StationTableData[SongListDisplayItem]):
	nowplaying: Optional[SongListDisplayItem]




class StationInfo(MCBaseClass):
	id: int=Field(frozen=True)
	name: str=Field(frozen=True)
	displayname: str=Field(default="", frozen=False)
	isrunning: bool=Field(default=False, frozen=False)
	#don't expect this to ever actually null
	owner: Optional[OwnerType]=Field(default=None, frozen=False)
	rules: list[ActionRule]=Field(
		default_factory=list, frozen=False
	)
	requestsecuritylevel: Optional[int]=Field(
		default=MinItemSecurityLevel.ANY_USER.value, frozen=False
	)
	viewsecuritylevel: Optional[int]=Field(default=0, frozen=False)

	def __hash__(self) -> int:
		return hash((self.id, self.name))
	
	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.id == other.id and self.name == other.name


class StationCreationInfo(MCBaseClass):
	name: str
	displayname: Optional[str]=""
	viewsecuritylevel: Optional[int]=Field(default=0)
	requestsecuritylevel: Optional[int]=Field(
		default=MinItemSecurityLevel.OWENER_USER.value
	)

	@field_validator("requestsecuritylevel")
	@classmethod
	def check_requestSecurityLevel(
		cls,
		v: int,
		validationInfo: ValidationInfo
	) -> int:
		if v < validationInfo.data["viewsecuritylevel"] \
			or v == MinItemSecurityLevel.PUBLIC.value:
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


class SongTreeNode(FrozenBaseClass):
	path: str
	totalChildCount: int
	id: Optional[int]=None
	name: Optional[str]=None
	directChildren: list["SongTreeNode"]=Field(default_factory=list)
	rules: list[PathsActionRule]=Field(
		default_factory=list, frozen=True
	)

	def __hash__(self) -> int:
		return hash(self.path)
	
	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.path == other.path
	
	@staticmethod
	def same_level_sort_key(node: "SongTreeNode") -> str:
		if node.name:
			return node.name
		return Path(node.path).stem
	


class StationSongTuple:

	def __init__(
		self,
		songid: int,
		stationid: int,
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

class SongArtistTuple:


	def __init__(
		self,
		songid: int,
		artistid: int,
		isprimaryartist: bool=False,
		islinked: bool=False
	) -> None:
		self.songid = songid
		self.artistid = artistid
		self.isprimaryartist = isprimaryartist
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[int]:
		yield self.songid
		yield self.artistid

	def __hash__(self) -> int:
		return hash((self.songid, self.artistid))
	
	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.songid == other.songid \
			and self.artistid == other.artistid


class SongPathInfo(IdItem):
	path: str


class SongAboutInfo(MCBaseClass):
	name: Optional[str]=None
	album: Optional[AlbumInfo]=None
	primaryartist: Optional[ArtistInfo]=None
	artists: Optional[list[ArtistInfo]]=Field(default_factory=list)
	covers: Optional[list[int]]=Field(default_factory=list)
	track: Optional[str]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	samplerate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None
	lyrics: Optional[str]=""
	stations: Optional[list[StationInfo]]=Field(default_factory=list)
	touched: Optional[set[str]]=None

	@property
	def allArtists(self) -> Iterable[ArtistInfo]:
		if self.primaryartist:
			yield self.primaryartist
		yield from (a for a in self.artists or [])

	

class SongEditInfo(SongAboutInfo, SongPathInfo):
	rules: list[ActionRule]=Field(default_factory=list)


class ValidatedSongAboutInfo(SongAboutInfo):

	@field_validator("stations")
	def check_stations_duplicates(cls, v: List[StationInfo]) -> List[StationInfo]:
		if not v:
			return []

		duplicate = next(get_duplicates(t.id for t in v), None)
		if duplicate:
			raise ValueError(
				f"Station with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return v
	
	@model_validator(mode="after") # type: ignore
	def root_validator(self) -> "ValidatedSongAboutInfo":
		artists = self.artists or []
		primaryArtist = self.primaryartist or None

		duplicate = next(get_duplicates(
			a.id for a in chain(artists, (primaryArtist,) if primaryArtist else ())),
			None
		)
		if duplicate:
			raise ValueError(
				f"Artist with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return self