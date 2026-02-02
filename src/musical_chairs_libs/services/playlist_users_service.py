
from typing import (
	Iterator,
	Optional,
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	build_base_rules_query,
	get_datetime,
	get_playlist_owner_roles,
	PlaylistInfo,
	AccountInfo,
	OwnerInfo,
	generate_domain_user_and_rules_from_rows,
	RulePriorityLevel,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from .current_user_provider import CurrentUserProvider
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	delete,
	and_,
	or_,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import (
	playlists as playlists_tbl,
	pl_pk, pl_ownerFk,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, 
	u_dirRoot, u_disabled, ur_userFk, ur_role,
	userRoles as user_roles_tbl, ur_keypath
)

class PlaylistsUserService:

	def __init__(
		self,
		conn: Connection,
		pathRuleService: PathRuleService,
		currentUserProvider: CurrentUserProvider,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService
		self.current_user_provider = currentUserProvider


	def get_playlist_owner(self, playlistId: int) -> OwnerInfo:
		query = select(pl_ownerFk, u_username, u_displayName)\
			.select_from(playlists_tbl)\
			.join(user_tbl, u_pk == pl_ownerFk)\
			.where(pl_pk == playlistId)
		data = self.conn.execute(query).mappings().fetchone()
		if not data:
			return OwnerInfo(id=0,username="", displayname="")
		return OwnerInfo(
			id=data[pl_ownerFk],
			username=data[u_username],
			displayname=data[u_displayName]
		)


	def get_playlist_users(
		self,
		playlist: PlaylistInfo,
	) -> Iterator[AccountInfo]:
		rulesQuery = build_base_rules_query(UserRoleSphere.Playlist).cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c["rule>userfk"].label("rule>userfk"),
			rulesQuery.c["rule>name"].label("rule>name"),
			rulesQuery.c["rule>quota"].label("rule>quota"),
			rulesQuery.c["rule>span"].label("rule>span"),
			rulesQuery.c["rule>priority"].label("rule>priority"),
			rulesQuery.c["rule>sphere"].label("rule>sphere")
		).select_from(user_tbl).join(
			rulesQuery,
			or_(
				and_(
					u_pk == playlist.owner.id,
					rulesQuery.c["rule>userfk"] == 0
				),
				and_(
					rulesQuery.c["rule>userfk"] == u_pk,
					rulesQuery.c["rule>keypath"] == str(playlist.id),
					rulesQuery.c["rule>sphere"] == UserRoleSphere.Playlist.value
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			or_(
				coalesce(
					rulesQuery.c["rule>priority"],
					RulePriorityLevel.SITE.value
				) > RulePriorityLevel.REQUIRES_INVITE.value,
				u_pk == playlist.owner.id
			)
		)

		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_domain_user_and_rules_from_rows(
			records,
			get_playlist_owner_roles,
			playlist.owner.id if playlist.owner else None
		)


	def add_user_rule_to_playlist(
		self,
		addedUserId: int,
		playlistId: int,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(user_roles_tbl).values(
			userfk = addedUserId,
			keypath = playlistId,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp(),
			sphere = UserRoleSphere.Playlist.value
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.INVITED_USER.value,
			sphere=UserRoleSphere.Playlist.value
		)


	def remove_user_rule_from_playlist(
		self,
		subjectUserId: int,
		playlistId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(user_roles_tbl)\
			.where(ur_userFk == subjectUserId)\
			.where(ur_keypath == playlistId)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]