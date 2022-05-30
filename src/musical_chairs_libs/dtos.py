from dataclasses import dataclass, field
from typing import List, Optional, Iterable, TypeVar, Generic

T = TypeVar("T")

@dataclass
class TableData(Generic[T]):
	totalRows: int
	items: List[T]

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