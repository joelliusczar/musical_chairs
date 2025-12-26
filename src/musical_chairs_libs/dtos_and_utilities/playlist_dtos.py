from sqlalchemy.engine.row import RowMapping
from pydantic import (
	Field,
	field_validator,
)
from typing import (
	Any,
	cast,
	Collection,
	Iterable,
	Iterator,
	Optional,
	Tuple
)
from .generic_dtos import (
	RuledEntity,
	Named,
	NamedIdItem
)
from musical_chairs_libs.tables import (
	pl_description, pl_viewSecurityLevel,
	pl_name, pl_pk, pl_ownerFk,
	u_username, u_displayName
)
from .account_dtos import OwnerType, OwnerInfo, get_playlist_owner_roles
from .user_role_def import RulePriorityLevel
from .queued_item import SongListDisplayItem
from .action_rule_dtos import ActionRule
from .validation_functions import min_length_validator_factory
from .simple_functions import get_non_simple_chars
from .station_dtos import StationInfo

class PlaylistCreationInfo(Named):
	description: Optional[str]=""
	stations: list[StationInfo]=cast(
		list[StationInfo], Field(default_factory=list)
	)

class PlaylistInfo(NamedIdItem, RuledEntity):
	owner: OwnerType
	description: Optional[str]=""

	@classmethod
	def row_to_playlist(cls, row: RowMapping) -> "PlaylistInfo":
		return PlaylistInfo(
			id=row[pl_pk],
			name=row[pl_name],
			description=row[pl_description],
			owner=OwnerInfo(
				id=row[pl_ownerFk],
				username=row[u_username],
				displayname=row[u_displayName]
			),
			viewsecuritylevel=row[pl_viewSecurityLevel] \
				or RulePriorityLevel.PUBLIC.value,
		)
	
	@classmethod
	def generate_playlist_and_rules_from_rows(
		cls,
		rows: Iterable[RowMapping],
		userId: Optional[int],
		scopes: Optional[Collection[str]]=None
	) -> Iterator["PlaylistInfo"]:
		currentPlaylist = None
		for row in rows:
			if not currentPlaylist or currentPlaylist.id != cast(int,row[pl_pk]):
				if currentPlaylist:
					playlistOwner = currentPlaylist.owner
					if playlistOwner and playlistOwner.id == userId:
						currentPlaylist.rules.extend(get_playlist_owner_roles(scopes))
					currentPlaylist.rules = ActionRule.sorted(currentPlaylist.rules)
					yield currentPlaylist
				currentPlaylist = cls.row_to_playlist(row)
				if cast(str,row["rule_domain"]) != "shim":
					currentPlaylist.rules.append(ActionRule.row_to_action_rule(row))
			elif cast(str,row["rule_domain"]) != "shim":
				currentPlaylist.rules.append(ActionRule.row_to_action_rule(row))
		if currentPlaylist:
			playlistOwner = currentPlaylist.owner
			if playlistOwner and playlistOwner.id == userId:
				currentPlaylist.rules.extend(get_playlist_owner_roles(scopes))
			currentPlaylist.rules = ActionRule.sorted(currentPlaylist.rules)
			yield currentPlaylist
	

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