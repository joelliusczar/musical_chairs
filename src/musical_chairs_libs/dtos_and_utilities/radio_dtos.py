from pydantic import validator, root_validator #pyright: ignore [reportUnknownVariableType]
from pydantic.dataclasses import dataclass as pydanticDataclass
from dataclasses import dataclass, field
from typing import\
	Iterator,\
	Optional,\
	Iterable,\
	List,\
	Any
from itertools import chain
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates, check_name_safety
from .generic_dtos import IdItem, TableData, T
from .account_dtos import ActionRule


@dataclass(frozen=True)
class ArtistInfo:
	id: int
	name: str

@dataclass(frozen=True)
class AlbumCreationInfo:
	name: str
	year: Optional[int]=None
	albumArtist: Optional[ArtistInfo]=None

@dataclass(frozen=True)
class AlbumInfo(AlbumCreationInfo, IdItem):
	...

@dataclass()
class SongBase:
	id: int
	name: str

@dataclass()
class SongListDisplayItem(SongBase):
	album: Optional[str]
	artist: Optional[str]
	path: str
	queuedTimestamp: float
	requestedTimestamp: Optional[float]=None
	playedTimestamp: Optional[float]=None
	rules: list[ActionRule]=field(default_factory=list)


@dataclass(frozen=True)
class ScanningSongItem:
	id: int
	path: str
	name: Optional[str]=None
	albumId: Optional[int]=None
	artistId: Optional[int]=None
	composerId: Optional[int]=None
	track: Optional[int]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	sampleRate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None


@dataclass()
class StationData(TableData[T]):
	requestRule: ActionRule

@dataclass()
class CurrentPlayingInfo(StationData[SongListDisplayItem]):
	nowPlaying: Optional[SongListDisplayItem]

@dataclass(frozen=True)
class Tag:
	id: int
	name: str

@dataclass(frozen=True)
class StationInfo:
	id: int
	name: str
	displayName: str=field(default="", hash=False, compare=False)
	isRunning: bool=field(default=False, hash=False, compare=False)
	ownerId: Optional[int]=field(default=None, hash=False, compare=False)
	requestSecurityLevel: int=field(default=0, hash=False, compare=False)

@dataclass()
class StationCreationInfo:
	name: str
	displayName: Optional[str]=""

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

		m = check_name_safety(v)
		if m:
			raise ValueError(f"Illegal character used in station name: {m}")
		return v


@dataclass(frozen=True)
class SongTreeNode:
	path: str
	totalChildCount: int
	id: Optional[int]=None
	name: Optional[str]=None

@dataclass()
class SongArtistGrouping:
	songId: int
	artists: List[ArtistInfo]=field(default_factory=list)

	def __iter__(self) -> Iterator[ArtistInfo]:
		return iter(self.artists or [])

@dataclass(frozen=True)
class StationSongTuple:
	songId: int
	stationId: int
	isLinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songId
		yield self.stationId

@dataclass(frozen=True)
class SongArtistTuple:
	songId: int
	artistId: int
	isPrimaryArtist: bool=False
	isLinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[int]:
		yield self.songId
		yield self.artistId

@dataclass()
class SongTagGrouping:
	songId: int
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
	primaryArtist: Optional[ArtistInfo]=None
	artists: Optional[list[ArtistInfo]]=field(default_factory=list)
	covers: Optional[list[int]]=field(default_factory=list)
	track: Optional[int]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	sampleRate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None
	lyrics: Optional[str]=""
	stations: Optional[list[StationInfo]]=field(default_factory=list)
	touched: Optional[set[str]]=None

	@property
	def allArtists(self) -> Iterable[ArtistInfo]:
		if self.primaryArtist:
			yield self.primaryArtist
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
		primaryArtist = values.get("primaryArtist", None)

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
