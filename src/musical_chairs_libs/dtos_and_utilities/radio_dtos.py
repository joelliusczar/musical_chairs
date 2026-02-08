from pydantic import (
	field_validator,
	model_validator,
	Field,
)
from typing import (
	Iterator,
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
from .action_rule_dtos import ActionRule
from .station_dtos import StationInfo, StationUnowned
from pathlib import Path
from .album_dtos import AlbumInfo, AlbumUnowned
from .artist_dtos import ArtistInfo, ArtistUnowned
from .playlist_dtos import PlaylistInfo, PlaylistUnowned




class ScanningSongItem(FrozenIdItem):
	treepath: str
	name: str | None=None
	albumId: int | None=None
	artistId: int | None=None
	composerId: int | None=None
	track: str | None=None
	discnum: int | None=None
	genre: str | None=None
	bitrate: float | None=None
	samplerate: float | None=None
	notes: str | None=None
	duration: float | None=None
	explicit: bool | None=None


class SongTreeNode(FrozenBaseClass):
	treepath: str
	totalChildCount: int
	id: int | None=None
	name: str | None=None
	trackNum: float=0
	directChildren: list["SongTreeNode"]=cast(
		list["SongTreeNode"], Field(default_factory=list)
	)
	rules: list[ActionRule]=cast(
		list[ActionRule], Field(default_factory=list, frozen=True)
	)

	def __hash__(self) -> int:
		return hash(self.treepath)

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.treepath == other.treepath

	@staticmethod
	def same_level_sort_key(node: "SongTreeNode") -> str:
		if node.name:
			return node.name
		return Path(node.treepath).stem


class SongArtistTuple:

	def __init__(
		self,
		songid: int,
		artistid: int | None,
		isprimaryartist: bool=False,
		islinked: bool=False
	) -> None:
		self.songid = songid
		self.artistid = artistid
		self.isprimaryartist = isprimaryartist
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[int | None]:
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
	treepath: str
	internalpath: str


class TrackListing(MCBaseClass):
	name: str
	tracknum: float=0
	track: str | None=None


class SongAboutInfo(MCBaseClass):
	name: str
	album: AlbumInfo | AlbumUnowned | None=None
	primaryartist: ArtistInfo | ArtistUnowned | None=None
	artists: list[ArtistInfo | ArtistUnowned] | None=cast(
		list[ArtistInfo | ArtistUnowned], Field(default_factory=list)
	)
	covers: list[int] | None=cast(list[int], Field(default_factory=list))
	track: str | None=None
	tracknum: float=0
	discnum: int | None=None
	genre: str | None=None
	bitrate: float | None=None
	samplerate: float | None=None
	notes: str | None=None
	duration: float | None=None
	explicit: bool | None=None
	lyrics: str | None=""
	stations: list[StationInfo | StationUnowned]=cast(
		list[StationInfo | StationUnowned], Field(default_factory=list)
	)
	playlists: list[PlaylistInfo | PlaylistUnowned]=cast(
		list[PlaylistInfo | PlaylistUnowned], Field(default_factory=list)
	)


	@property
	def allArtists(self) -> Iterable[ArtistInfo | ArtistUnowned]:
		if self.primaryartist:
			yield self.primaryartist
		yield from self.artists or []

class SongFullQueryInfo(SongAboutInfo, SongPathInfo):
	pass

class ChangeTrackedSongInfo(SongAboutInfo):
	touched: set[str] | None=None
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
	treepath: str
	newprefix: str

class LastPlayedItem(MCBaseClass):
	songid: int
	timestamp: float
	historyid: int
	itemtype: str=Field(default="song") #for display?
	parentkey: int | None=None