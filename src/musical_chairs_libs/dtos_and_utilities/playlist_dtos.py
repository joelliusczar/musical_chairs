from sqlalchemy.engine.row import RowMapping
from pydantic import (
	Field,
	field_validator,
)
from typing import (
	Any,
	Iterator,
	Iterable,
	Optional,
	cast,
	Collection,
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

class PlaylistCreationInfo(Named):
	description: Optional[str]=""

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
		islinked: bool=False
	) -> None:
		self.songid = songid
		self.playlistid = playlistid
		self.islinked = islinked

	def __len__(self) -> int:
		return 2

	def __iter__(self) -> Iterator[Any]:
		yield self.songid
		yield self.playlistid

	def __hash__(self) -> int:
		return hash((self.songid, self.playlistid))

	def __eq__(self, other: Any) -> bool:
		if not other:
			return False
		return self.songid == other.songid \
			and self.playlistid == other.playlistid