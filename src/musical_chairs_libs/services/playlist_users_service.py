
from typing import (
	Iterator,
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	get_playlist_owner_roles,
	PlaylistInfo,
	AccountInfo,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from .domain_user_service import DomainUserService


class PlaylistsUserService:

	def __init__(
		self,
		domainUserService: DomainUserService
	) -> None:
		self.domain_user_service = domainUserService


	def get_playlist_users(
		self,
		playlist: PlaylistInfo,
	) -> Iterator[AccountInfo]:
		return self.domain_user_service.get_domain_users(
			playlist,
			UserRoleSphere.Playlist,
			get_playlist_owner_roles
		)


	def add_user_rule_to_playlist(
		self,
		addedUserId: int,
		playlistId: int,
		rule: ActionRule
	) -> ActionRule:
		return self.domain_user_service.add_domain_rule_to_user(
			addedUserId,
			UserRoleSphere.Playlist.value,
			str(playlistId),
			rule
		)


	def remove_user_rule_from_playlist(
		self,
		subjectUserId: int,
		playlistId: int,
		ruleName: str | None
	):
		self.domain_user_service.remove_domain_rule_from_user(
			subjectUserId,
			UserRoleSphere.Playlist.value,
			str(playlistId),
			ruleName
		)