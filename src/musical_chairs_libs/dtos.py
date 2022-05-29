from dataclasses import dataclass, field
from typing import List, Optional, Iterable


@dataclass
class AccountInfo:
	id: int
	userName: str
	hash: Optional[bytes]
	email: Optional[str]
	isAuthenticated: bool = False
	roles: List[str] = field(default_factory=list)

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
	requestedTimestamp: Optional[float] = None

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