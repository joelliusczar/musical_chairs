import os
from .account_dtos import User
from .action_rule_dtos import ActionRule
from .artist_dtos import ArtistInfo
from .constants import StationRequestTypes
from .generic_dtos import (
	TableData,
	T,
	NamedIdItem,
	IdItem,
)
from pydantic import (
	BaseModel as MCBaseClass,
	Field,
)
from typing import (
	Optional,
	Any,
	cast
)

class QueuedItem(NamedIdItem):
	queuedtimestamp: float = Field(frozen=True)
	itemtype: str = Field(default=StationRequestTypes.SONG.lower()) #for display?
	parentkey: int | None = None

	def __hash__(self) -> int:
		return hash((self.id, self.name, self.queuedtimestamp))

	def __eq__(self, value: Any) -> bool:
		if not value:
			return False
		return self.id == value.id \
			and self.name == value.name \
			and self.queuedtimestamp == value.queuedtimestamp


class SongListBasicItem(QueuedItem):
	album: str | None
	artist: str | None
	internalpath: str
	treepath: str


	def __hash__(self) -> int:
		return super().__hash__()


	def display(self) -> str:
		if self.name:
				display = f"{self.name} - {self.album} - {self.artist}"
		else:
			display = os.path.splitext(os.path.split(self.treepath)[1])[0]
		return display.replace("\n", "")


class StreamQueuedItem(SongListBasicItem):
	userId: int | None = None
	action: str | None = None

	def __hash__(self) -> int:
		return super().__hash__()


class CatalogueItem(QueuedItem):
	creator: str
	parentname: str
	requesttypeid: int #so that the front end knows what to equest
	year: Optional[int]=None
	rules: list[ActionRule]=cast(
		list[ActionRule],
		Field(default_factory=list, frozen=False)
	)
	owner: User
	playedcount: int=0


class SongListDisplayItem(SongListBasicItem):
	track: float | None = None
	discnum: int | None = None
	rules: list[ActionRule]=cast(
		list[ActionRule],
		Field(default_factory=list, frozen=False)
	)


class HistoryItem(SongListDisplayItem):
	playedtimestamp: Optional[float]=None
	historyid: int


class StationTableData(TableData[T]):
	stationrules: list[ActionRule]


class CurrentPlayingInfo(StationTableData[SongListDisplayItem]):
	nowplaying: Optional[SongListDisplayItem]


class SongsArtistInfo(ArtistInfo):
	songs: list[SongListDisplayItem]=cast(
		list[SongListDisplayItem], Field(default_factory=list, frozen=False)
	)

class QueueRequest(IdItem):
	itemtype: str
	parentKey: Optional[int]


class QueuePossibility(MCBaseClass):
	itemId: int
	lastplayednum: int
	playnum: int
	itemtype: str = StationRequestTypes.SONG.lower()


class QueueMetrics(MCBaseClass):
	maxSize: int
	loaded: int = 0
	queued: int = 0