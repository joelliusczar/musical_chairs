from dataclasses import dataclass
from collections.abc import Iterable
from typing import Optional
from pydantic import BaseModel


class AccountInfo(BaseModel):
	username: str
	password: bytes
	email: str

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