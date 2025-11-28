import os
from .action_rule_dtos import ActionRule
from .artist_dtos import ArtistInfo
from .generic_dtos import (
	TableData,
	T,
	NamedIdItem,
)
from pydantic import (
	Field,
)
from typing import (
	Optional,
	Any,
	cast
)

class QueuedItem(NamedIdItem):
	queuedtimestamp: float=Field(frozen=True)

	def __hash__(self) -> int:
		return hash((self.id, self.name, self.queuedtimestamp))

	def __eq__(self, value: Any) -> bool:
		if not value:
			return False
		return self.id == value.id \
			and self.name == value.name \
			and self.queuedtimestamp == value.queuedtimestamp
	
class CollectionQueuedItem(QueuedItem):
	creator: str
	itemtype: str
	itemtypeid: int
	year: Optional[int]=None
	rules: list[ActionRule]=cast(
		list[ActionRule],
		Field(default_factory=list, frozen=False)
	)


class SongListDisplayItem(QueuedItem):
	album: Optional[str]
	artist: Optional[str]
	path: str
	internalpath: str
	track: Optional[float]=None
	playedtimestamp: Optional[float]=None
	rules: list[ActionRule]=cast(
		list[ActionRule],
		Field(default_factory=list, frozen=False)
	)
	historyid: Optional[int]=None
	disc: Optional[int]=None


	def display(self) -> str:
		if self.name:
				display = f"{self.name} - {self.album} - {self.artist}"
		else:
			display = os.path.splitext(os.path.split(self.path)[1])[0]
		return display.replace("\n", "")


class StationTableData(TableData[T]):
	stationrules: list[ActionRule]


class CurrentPlayingInfo(StationTableData[SongListDisplayItem]):
	nowplaying: Optional[SongListDisplayItem]


class SongsArtistInfo(ArtistInfo):
	songs: list[SongListDisplayItem]=cast(
		list[SongListDisplayItem], Field(default_factory=list, frozen=False)
	)
