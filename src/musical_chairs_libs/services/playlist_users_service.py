
from typing import (
	Iterator,
	Optional,
	Union,
	cast,
	Iterable,
	Tuple,
	Collection
)
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	PlaylistInfo,
	AccountInfo,
	OwnerInfo,
	generate_playlist_user_and_rules_from_rows,
	RulePriorityLevel,
	ActionRule,
	PlaylistActionRule,
	UserRoleDomain,
	get_playlist_owner_roles,
	UserRoleDef,
	build_placeholder_select
)
from .path_rule_service import PathRuleService
from sqlalchemy import (
	select,
	Select,
	insert,
	Integer,
	func,
	Float,
	delete,
	literal as dbLiteral,
	String,
	and_,
	or_,
	true,
	false,
	union_all,
)
from sqlalchemy.sql.expression import (
	case,
	CompoundSelect,
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from sqlalchemy.sql.schema import Column
from musical_chairs_libs.tables import (
	playlists as playlists_tbl, pl_description, pl_viewSecurityLevel,
	pl_name, pl_pk, pl_ownerFk, plup_count, plup_span, plup_priority,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, 
	u_dirRoot, u_disabled, ur_userFk, ur_role, ur_count, ur_span, ur_priority,
	playlist_user_permissions, plup_userFk, plup_playlistFk, plup_role
)

__playlist_permissions_query__ = select(
	plup_userFk.label("rule_userfk"),
	plup_role.label("rule_name"),
	plup_count.label("rule_count"),
	plup_span.label("rule_span"),
	coalesce[Integer](
		plup_priority,
		RulePriorityLevel.STATION_PATH.value
	).label("rule_priority"),
	dbLiteral(UserRoleDomain.Playlist.value).label("rule_domain"),
	plup_playlistFk.label("rule_playlistfk")
)

def build_playlist_rules_query(
	userId: Optional[int]=None
) -> CompoundSelect[Tuple[int, str, float, float, int, str]]:
	user_rules_query = select(
		ur_userFk.label("rule_userfk"),
		ur_role.label("rule_name"),
		ur_count.label("rule_count"),
		ur_span.label("rule_span"),
		coalesce[Integer](
			ur_priority,
			case(
				(ur_role == UserRoleDef.ADMIN.value, RulePriorityLevel.SUPER.value),
				else_=RulePriorityLevel.SITE.value
			)
		).label("rule_priority"),
		dbLiteral(UserRoleDomain.Site.value).label("rule_domain"),
		dbLiteral(None).label("rule_playlistfk")
	).where(or_(
			ur_role.like(f"{UserRoleDomain.Playlist.value}:%"),
			ur_role == UserRoleDef.ADMIN.value
		),
	)
	domain_permissions_query = __playlist_permissions_query__
	placeholder_select = build_placeholder_select(
		UserRoleDomain.Playlist
	).add_columns(
		dbLiteral(None).label("rule_playlistfk")
	)

	if userId is not None:
		domain_permissions_query = \
			domain_permissions_query.where(plup_userFk == userId)
		user_rules_query = user_rules_query.where(ur_userFk == userId)
		
	query = union_all(
		placeholder_select,
		domain_permissions_query,
		user_rules_query,
	)
	return query

class PlaylistsUserService:

	def __init__(
		self,
		conn: Connection,
		pathRuleService: Optional[PathRuleService]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		if not pathRuleService:
			pathRuleService = PathRuleService(conn)
		self.conn = conn
		self.get_datetime = get_datetime
		self.path_rule_service = pathRuleService

	def __attach_user_joins__(
		self,
		query: Select[
			Tuple[
				Integer,
				Union[String, None],
				Union[String, None],
				String,
				Integer,
				Union[String, None],
				# Union[String, None],
				Integer
			]
		],
		userId: int,
		scopes: Optional[Collection[str]]=None
	) -> Select[
			Tuple[
				Integer,
				Union[String, None],
				Union[String, None],
				String,
				Integer,
				Union[String, None],
				Integer,
			]
		]:
		rulesQuery = build_playlist_rules_query(userId)
		rulesSubquery = rulesQuery.cte(name="rulesQuery")
		canViewQuery= select(
			rulesSubquery.c.rule_playlistfk, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_priority, #pyright: ignore [reportUnknownMemberType]
			rulesSubquery.c.rule_domain #pyright: ignore [reportUnknownMemberType]
		).where(
			rulesSubquery.c.rule_name.in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
		).cte(name="canviewquery")

		topSiteRule = select(
			coalesce[int](
				func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
				RulePriorityLevel.NONE.value
			).label("max")
		).where(
			canViewQuery.c.rule_domain == UserRoleDomain.Site.value
		).cte("topsiterule")

		ownerScopeSet = set(get_playlist_owner_roles(scopes))

		query = query.join(
			rulesSubquery,
			or_(
				rulesSubquery.c.rule_playlistfk == pl_pk, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_playlistfk == -1, #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
				rulesSubquery.c.rule_playlistfk.is_(None) #pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
			)
		).where(
			or_(
				coalesce(
					pl_viewSecurityLevel,
					RulePriorityLevel.INVITED_USER.value
				) < select(coalesce[int](
							func.max(canViewQuery.c.rule_priority), #pyright: ignore [reportUnknownMemberType]
							RulePriorityLevel.NONE.value
						)).where(pl_pk == canViewQuery.c.rule_playlistfk).scalar_subquery(), #pyright: ignore [reportUnknownMemberType]
				and_(
					dbLiteral(UserRoleDomain.Site.value)
						.in_( #pyright: ignore [reportUnknownMemberType]
							select(canViewQuery.c.rule_domain) #pyright: ignore [reportUnknownMemberType]
						),
					coalesce(
						pl_viewSecurityLevel,
						RulePriorityLevel.RULED_USER.value
					) < select(topSiteRule.c.max).scalar_subquery() #pyright: ignore [reportUnknownMemberType]
				),
				coalesce(
					pl_viewSecurityLevel,
					RulePriorityLevel.ANY_USER.value
				) < RulePriorityLevel.USER.value,
				and_(
					pl_ownerFk == userId,
					coalesce(
						pl_viewSecurityLevel,
						RulePriorityLevel.OWENER_USER.value
					) < RulePriorityLevel.OWNER.value
				)
			),
		).where(
				or_(
					rulesSubquery.c.rule_name.in_(scopes) if scopes else true(), #pyright: ignore [reportUnknownMemberType]
					(pl_ownerFk == userId) if scopes and ownerScopeSet else false()
				)
			)

		query = query.add_columns(
			cast(Column[String], rulesSubquery.c.rule_name),
			cast(Column[Float[float]], rulesSubquery.c.rule_count),
			cast(Column[Float[float]], rulesSubquery.c.rule_span),
			cast(Column[Integer], rulesSubquery.c.rule_priority),
			cast(Column[String], rulesSubquery.c.rule_domain)
		)
		return query


	def get_playlists(
		self,
		playlistKeys: Union[int, str, Iterable[int], None]=None,
		ownerId: Union[int, None]=None,
		user: Optional[AccountInfo]=None,
		scopes: Optional[Collection[str]]=None,
		page: int = 0,
		pageSize: Optional[int]=None,
	) -> Iterator[PlaylistInfo]:
		query = select(
			pl_pk,
			pl_name,
			pl_description,
			u_username,
			pl_ownerFk,
			u_displayName,
			pl_viewSecurityLevel
		).select_from(playlists_tbl)\
		.join(user_tbl, pl_ownerFk == u_pk, isouter=True)

		if user:
			query = self.__attach_user_joins__(query, user.id, scopes)
		else:
			if scopes:
				return
			query = query.where(
				coalesce(pl_viewSecurityLevel, 0) == 0
			)
		if type(ownerId) is int:
			query = query.where(pl_ownerFk == ownerId)
		if type(playlistKeys) == int:
			query = query.where(pl_pk == playlistKeys)
		elif isinstance(playlistKeys, Iterable) and not isinstance(playlistKeys, str):
			query = query.where(pl_pk.in_(playlistKeys))
		elif type(playlistKeys) is str and not ownerId:
			raise ValueError("user must be provided when using playlist name")
		elif type(playlistKeys) is str:
			lPlaylistKey = playlistKeys.replace("_","\\_").replace("%","\\%")
			query = query\
				.where(pl_name.like(f"%{lPlaylistKey}%"))
		query = query.order_by(pl_pk)
		offset = page * pageSize if pageSize else 0
		query = query.offset(offset).limit(pageSize)
		records = self.conn.execute(query).mappings()

		if user:
			yield from PlaylistInfo.generate_playlist_and_rules_from_rows(
				records,
				user.id,
				scopes
			)
		else:
			for row in records:
				yield PlaylistInfo.row_to_playlist(row)


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
		userId: Optional[int]=None
	) -> Iterator[AccountInfo]:
		rulesQuery = build_playlist_rules_query().cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			u_dirRoot,
			rulesQuery.c.rule_userfk,
			rulesQuery.c.rule_name,
			rulesQuery.c.rule_count,
			rulesQuery.c.rule_span,
			rulesQuery.c.rule_priority,
			rulesQuery.c.rule_domain
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
		if userId is not None:
			query = query.where(u_pk == userId)
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
	) -> PlaylistActionRule:
		stmt = insert(playlist_user_permissions).values(
			userfk = addedUserId,
			playlistfk = playlistId,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return PlaylistActionRule(
			name=rule.name,
			span=rule.span,
			count=rule.count,
			priority=RulePriorityLevel.STATION_PATH.value
		)


	def remove_user_rule_from_playlist(
		self,
		userId: int,
		playlistId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(playlist_user_permissions)\
			.where(plup_userFk == userId)\
			.where(plup_playlistFk == playlistId)
		if ruleName:
			delStmt = delStmt.where(plup_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]