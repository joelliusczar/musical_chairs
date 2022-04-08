from dataclasses import dataclass
from collections.abc import Iterable
from pydantic import BaseModel

class AccountInfo(BaseModel):
	username: str
	password: bytearray
	email: str

@dataclass
class SongItem:
	id: int
	title: str
	album: str
	artist: str

@dataclass
class QueueItem(SongItem): 
	path: str
	queuedTimestamp: float
	requestedTimestamp: float = None

@dataclass
class HistoryItem(SongItem):
	playedTimestamp: float

@dataclass
class CurrentPlayingInfo:
	nowPlaying: HistoryItem
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