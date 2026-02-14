from sqlalchemy.engine.row import RowMapping
from pydantic import (
	Field,
	field_validator,
)
from typing import (
	Any,
	cast,
	Iterator,
	Optional,
	Tuple
)
from .generic_dtos import (
	Named,
	NamedTokenItem,
)
from .account_dtos import User, RuledOwnedTokenEntity
from .user_role_def import RulePriorityLevel
from .queued_item import SongListDisplayItem
from .validation_functions import min_length_validator_factory
from .simple_functions import get_non_simple_chars
from .station_dtos import StationInfo

class PlaylistCreationInfo(Named):
	displayname: Optional[str]=""
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)

class PlaylistUnowned(NamedTokenItem):
	displayname: str | None=""

class PlaylistInfo(PlaylistUnowned, RuledOwnedTokenEntity):


	@classmethod
	def row_to_playlist(cls, row: RowMapping) -> "PlaylistInfo":
		return PlaylistInfo(
			id=row["id"],
			name=row["name"],
			displayname=row["displayname"],
			owner=User(
				id=row["owner>id"],
				username=row["owner>username"],
				displayname=row["owner>displayname"],
				publictoken=row["owner>publictoken"]
			),
			viewsecuritylevel=row["viewsecuritylevel"] \
				or RulePriorityLevel.PUBLIC.value,
		)	


class SongsPlaylistInfo(PlaylistInfo):
	songs: list[SongListDisplayItem]=cast(
		list[SongListDisplayItem], Field(default_factory=list, frozen=False)
	)
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)


class ValidatedPlaylistCreationInfo(PlaylistCreationInfo):

	_name_len = field_validator(
		"name"
	)(min_length_validator_factory(2, "Playlist name"))

	@field_validator("name")
	@classmethod
	def check_name_for_illegal_chars(cls, v: str) -> str:
		if not v:
			return ""

		m = get_non_simple_chars(v)
		if m:
			raise ValueError(f"Illegal character used in playlist name: {m}")
		return v


class SongPlaylistTuple:

	def __init__(
		self,
		songid: int,
		playlistid: Optional[int]=None,
		rank: str=""
	) -> None:
		self.songid = songid
		self.playlistid = playlistid
		self.lexorder = rank

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songid
		yield self.playlistid

	def __hash__(self) -> int:
		return hash((self.songid, self.playlistid, self.lexorder))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.songid == other.songid \
			and self.playlistid == other.playlistid \
			and self.lexorder == other.lexorder
	
	def __as_tuple__(self) -> Tuple[int, str, int]:
		return (self.playlistid or 0, self.lexorder, self.songid)
	
	def __lt__(self, other: "SongPlaylistTuple") -> bool:
		return self.__as_tuple__() < other.__as_tuple__()
	
	def __str__(self) -> str:
		return f"(playlistid={self.playlistid}, songid={self.songid},"\
			f" rank={self.lexorder})"
	
	def __repr__(self) -> str:
		return str(self)