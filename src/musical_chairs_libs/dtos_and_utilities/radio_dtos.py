from pydantic import BaseModel, validator
from typing import\
	Optional,\
	Iterable,\
	List
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates

class SongBase(BaseModel):
	id: int
	name: str

class SongItem(SongBase):
	album: Optional[str]
	artist: Optional[str]

class SongItemPlumbing(BaseModel):
	id: int
	path: str
	name: Optional[str]=None
	albumPk: Optional[int]=None
	artistPk: Optional[int]=None
	composerPk: Optional[int]=None
	track: Optional[int]=None
	disc: Optional[int]=None
	genre: Optional[str]=None
	bitrate: Optional[float]=None
	sampleRate: Optional[float]=None
	comment: Optional[str]=None
	duration: Optional[float]=None
	explicit: Optional[bool]=None

class QueueItem(SongItem):
	path: str
	queuedTimestamp: float
	requestedTimestamp: Optional[float]=None

class HistoryItem(SongItem):
	playedTimestamp: float

class CurrentPlayingInfo(BaseModel):
	nowPlaying: Optional[HistoryItem]
	items: Iterable[QueueItem]

class Tag(BaseModel):
	id: int
	name: str

class StationInfo(BaseModel):
	id: int
	name: str
	displayName: str
	tags: Optional[List[Tag]]

class StationCreationInfo(BaseModel):
	name: str
	displayName: Optional[str]
	tags: Optional[List[Tag]]

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


class SongTreeNode(BaseModel):
	path: str
	totalChildCount: int
	id: Optional[int]=None
	name: Optional[str]=None