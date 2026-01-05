from pydantic import (
	field_validator,
	model_validator,
	Field,
)
from typing import (
	Iterator,
	Optional,
	Iterable,
	List,
	Any,
	cast
)
from itertools import chain
from .simple_functions import get_duplicates
from .generic_dtos import (
	FrozenIdItem,
	FrozenBaseClass,
	MCBaseClass,
	IdItem,
)
from .action_rule_dtos import ActionRule, PathsActionRule
from .station_dtos import StationInfo
from pathlib import Path
from .album_dtos import AlbumInfo
from .artist_dtos import ArtistInfo
from .playlist_dtos import PlaylistInfo




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


class SongTreeNode(FrozenBaseClass):
	path: str
	totalChildCount: int
	id: Optional[int]=None
	name: Optional[str]=None
	trackNum: float=0
	directChildren: list["SongTreeNode"]=cast(list["SongTreeNode"], Field(default_factory=list))
	rules: list[PathsActionRule]=cast(list[PathsActionRule], Field(default_factory=list, frozen=True))

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


class SongArtistTuple:

	def __init__(
		self,
		songid: int,
		artistid: Optional[int],
		isprimaryartist: bool=False,
		islinked: bool=False
	) -> None:
		self.songid = songid
		self.artistid = artistid
		self.isprimaryartist = isprimaryartist
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Optional[int]]:
		yield self.songid
		yield self.artistid

	def __hash__(self) -> int:
		return hash((self.songid, self.artistid))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.songid == other.songid \
			and self.artistid == other.artistid
	
	def __str__(self) -> str:
		return f"(songid={self.songid}, artistid={self.artistid})"
	
	def __repr__(self) -> str:
		return str(self)


class SongPathInfo(IdItem):
	path: str
	internalpath: str

class TrackListing(MCBaseClass):
	name: str
	tracknum: float=0
	track: Optional[str]=None

class SongAboutInfo(MCBaseClass):
	name: str
	album: Optional[AlbumInfo]=None
	primaryartist: Optional[ArtistInfo]=None
	artists: Optional[list[ArtistInfo]]=cast(list[ArtistInfo], Field(default_factory=list))
	covers: Optional[list[int]]=cast(list[int], Field(default_factory=list))
	track: Optional[str]=None
	tracknum: float=0
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	samplerate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None
	lyrics: Optional[str]=""
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)
	playlists: list[PlaylistInfo]=cast(
		list[PlaylistInfo], Field(default_factory=list)
	)


	@property
	def allArtists(self) -> Iterable[ArtistInfo]:
		if self.primaryartist:
			yield self.primaryartist
		yield from self.artists or []

class SongFullQueryInfo(SongAboutInfo, SongPathInfo):
	pass

class ChangeTrackedSongInfo(SongAboutInfo):
	touched: Optional[set[str]]=None
	trackinfo: dict[int, TrackListing]={}

class SongEditInfo(ChangeTrackedSongInfo, SongPathInfo):
	rules: list[ActionRule]=cast(list[ActionRule], Field(default_factory=list))

#The path info is left out because I don't want to deal with the 
#validation errors. I suppose they could be added a optional properties though.
class ValidatedSongAboutInfo(ChangeTrackedSongInfo):

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

		duplicate = next(
			get_duplicates(
				a.id for a in chain(artists, (primaryArtist,) if primaryArtist else ())
			),
			None,
		)
		if duplicate:
			raise ValueError(
				f"Artist with id {duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		return self


class DirectoryTransfer(MCBaseClass):
	path: str
	newprefix: str

class LastPlayedItem(MCBaseClass):
	songid: int
	timestamp: float
	historyid: int
	itemtype: str=Field(default="song") #for display?
	parentkey: Optional[int]=None
