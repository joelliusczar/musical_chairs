
from typing import (
	Iterator,
	Optional,
	Tuple,
)
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	PlaylistInfo,
	AccountInfo,
	OwnerInfo,
	generate_playlist_user_and_rules_from_rows,
	RulePriorityLevel,
	ActionRule,
	UserRoleDef,
	build_placeholder_select
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserRoleSphere
)
from .current_user_provider import CurrentUserProvider
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	insert,
	Integer,
	delete,
	literal as dbLiteral,
	and_,
	or_,
	union_all,
)
from sqlalchemy.sql.expression import (
	case,
	CompoundSelect,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import (
	playlists as playlists_tbl,
	pl_pk, pl_ownerFk, plup_count, plup_span, plup_priority,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, 
	u_dirRoot, u_disabled, ur_userFk, ur_role, ur_quota, ur_span, ur_priority,
	playlist_user_permissions, plup_userFk, plup_playlistFk, plup_role
)

__playlist_permissions_query__ = select(
	plup_userFk.label("rule_userfk"),
	plup_role.label("rule_name"),
	plup_count.label("rule_quota"),
	plup_span.label("rule_span"),
	coalesce[Integer](
		plup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleSphere.Playlist.value).label("rule_sphere"),
	plup_playlistFk.label("rule_playlistfk")
)

def build_playlist_rules_query(
	userId: Optional[int]=None
) -> CompoundSelect[Tuple[int, str, float, float, int, str]]:
	user_rules_query = select(
		ur_userFk.label("rule_userfk"),
		ur_role.label("rule_name"),
		ur_quota.label("rule_quota"),
		ur_span.label("rule_span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule_priority"),
		dbLiteral(UserRoleSphere.Site.value).label("rule_sphere"),
		dbLiteral(None).label("rule_playlistfk")
	).where(or_(
			ur_role.like(f"{UserRoleSphere.Playlist.value}:%"),
			ur_role == UserRoleDef.ADMIN.value
		),
	)
	sphere_permissions_query = __playlist_permissions_query__
	placeholder_select = build_placeholder_select(
		UserRoleDef.PLAYLIST_VIEW.value
	).add_columns(
		dbLiteral(None).label("rule_playlistfk")
	)

	if userId is not None:
		sphere_permissions_query = \
			sphere_permissions_query.where(plup_userFk == userId)
		user_rules_query = user_rules_query.where(ur_userFk == userId)
		
	query = union_all(
		placeholder_select,
		sphere_permissions_query,
		user_rules_query,
	)
	return query

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
		rulesQuery = build_playlist_rules_query().cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userfk.label("rule.userfk"),
			rulesQuery.c.rule_name.label("rule.name"),
			rulesQuery.c.rule_quota.label("rule.quota"),
			rulesQuery.c.rule_span.label("rule.span"),
			rulesQuery.c.rule_priority.label("rule.priority"),
			rulesQuery.c.rule_sphere.label("rule.sphere")
		).select_from(user_tbl).join(
			rulesQuery,
			or_(
				and_(
					u_pk == playlist.owner.id,
					rulesQuery.c.rule_userfk == 0
				),
				and_(
					rulesQuery.c.rule_userfk == u_pk,
					rulesQuery.c.rule_playlistfk == playlist.id
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			or_(
				coalesce(
					rulesQuery.c.rule_priority,
					RulePriorityLevel.SITE.value
				) > RulePriorityLevel.INVITED_USER.value,
				u_pk == playlist.owner.id
			)
		)

		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_playlist_user_and_rules_from_rows(
			records,
			playlist.owner.id if playlist.owner else None
		)


	def add_user_rule_to_playlist(
		self,
		addedUserId: int,
		playlistId: int,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(playlist_user_permissions).values(
			userfk = addedUserId,
			playlistfk = playlistId,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.STATION_PATH.value,
			sphere=UserRoleSphere.Playlist.value
		)


	def remove_user_rule_from_playlist(
		self,
		subjectUserId: int,
		playlistId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(playlist_user_permissions)\
			.where(plup_userFk == subjectUserId)\
			.where(plup_playlistFk == playlistId)
		if ruleName:
			delStmt = delStmt.where(plup_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]