from pydantic import validator, root_validator
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
from .simple_functions import get_duplicates
from .generic_dtos import IdItem


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
class QueueItem(SongListDisplayItem):
	path: str
	queuedTimestamp: float
	requestedTimestamp: Optional[float]=None

@dataclass()
class HistoryItem(SongListDisplayItem):
	playedTimestamp: float

@dataclass()
class CurrentPlayingInfo:
	nowPlaying: Optional[HistoryItem]
	items: Iterable[QueueItem]

@dataclass(frozen=True)
class Tag:
	id: int
	name: str

@dataclass()
class StationInfo:
	id: int
	name: str
	displayName: str
	tags: Optional[List[Tag]]

@dataclass()
class StationCreationInfo:
	name: str
	displayName: Optional[str]=""
	tags: Optional[List[Tag]]=field(default_factory=list)

@pydanticDataclass
class ValidatedStationCreationInfo(StationCreationInfo):

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
class SongTagTuple:
	songId: int
	tagId: int
	isLinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songId
		yield self.tagId

@dataclass(frozen=True)
class SongArtistTuple:
	songId: int
	artistId: int
	isPrimaryArtist: bool=field(default=False, hash=False, compare=False)
	isLinked: bool=field(default=False, hash=False, compare=False)

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songId
		yield self.artistId


@dataclass()
class SongTagGrouping:
	songId: int
	tags: List[Tag]=field(default_factory=list)

	def __iter__(self) -> Iterator[Tag]:
		return iter(self.tags or [])

@dataclass()
class SongEditInfo:
	id: int
	path: str
	name: Optional[str]=None
	album: Optional[AlbumInfo]=None
	primaryArtist: Optional[ArtistInfo]=None
	artists: Optional[List[ArtistInfo]]=field(default_factory=list)
	covers: Optional[List[int]]=field(default_factory=list)
	track: Optional[int]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	sampleRate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None
	lyrics: Optional[str]=""
	tags: Optional[List[Tag]]=field(default_factory=list)

	@property
	def allArtists(self) -> Iterable[ArtistInfo]:
		if self.primaryArtist:
			yield self.primaryArtist
		yield from (a for a in self.artists or [])


@pydanticDataclass
class ValidatedSongEditInfo(SongEditInfo):

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