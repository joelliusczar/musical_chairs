import musical_chairs_libs.dtos_and_utilities as dtos
import musical_chairs_libs.tables as tbl
from typing import Iterable, Iterator, cast, Optional, Union
from sqlalchemy import (
	select,
	delete,
	insert,
	func,
	or_,
	and_
)
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.engine import Connection
from musical_chairs_libs.protocols import FileService, UserProvider
from musical_chairs_libs.dtos_and_utilities import (
	build_base_rules_query,
	RulePriorityLevel,
	normalize_opening_slash,
	RoledUser,
	ChainedAbsorbentTrie,
	ActionRule,
	get_path_owner_roles,
	UserRoleSphere,
	UserRoleDef,
	get_datetime,
	generate_path_user_and_rules_from_rows
)
from musical_chairs_libs.tables import (
	userRoles as user_roles_tbl,
	ur_userFk, ur_keypath, ur_role, ur_priority, ur_span, ur_quota,
	users as user_tbl, u_pk, u_username, u_displayName, u_email,
	u_disabled,
	sg_pk, sg_path, sg_deletedTimstamp,
)

class PathRuleService:

	def __init__(
		self,
		conn: Connection,
		fileService: FileService,
		userProvider: UserProvider
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.file_service = fileService
		self.user_provider = userProvider


	def get_paths_user_can_see(self, userId: int) -> Iterator[ActionRule]:
		query = select(ur_keypath, ur_role, ur_priority, ur_span, ur_quota)\
			.where(ur_userFk == userId)\
			.order_by(ur_keypath)
		records = self.conn.execute(query).mappings()
		for r in records:
			yield ActionRule(
				name=cast(str,r[ur_role]),
				priority=cast(int,r[ur_priority]) \
					or RulePriorityLevel.INVITED_USER.value,
				span=cast(int,r[ur_span]) or 0,
				quota=cast(int,r[ur_quota]) or 0,
				keypath=normalize_opening_slash(cast(str,r[ur_keypath])),
				sphere=UserRoleSphere.Path.value
			)


	def get_rule_path_tree(
		self
	) -> ChainedAbsorbentTrie[ActionRule]:
		user = self.user_provider.current_user()
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
		)

		pathRuleTree = ChainedAbsorbentTrie[ActionRule](
			(normalize_opening_slash(p.keypath), p) for p in
				rules if p.sphere == UserRoleSphere.Path.value and p.keypath
		)
		pathRuleTree.add("/", (r for r in user.roles \
			if type(r) == ActionRule \
				and (UserRoleSphere.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
		return pathRuleTree


	def remove_user_rule_from_path(
		self,
		subjectUserId: int,
		prefix: str,
		ruleName: Optional[str]
	):
		delStmt = delete(user_roles_tbl)\
			.where(ur_userFk == subjectUserId)\
			.where(ur_keypath == prefix)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt)

	def add_user_rule_to_path(
		self,
		addedUserId: int,
		prefix: str,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(user_roles_tbl).values(
			userfk = addedUserId,
			keypath = prefix,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp(),
			sphere = UserRoleSphere.Path.value
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.INVITED_USER.value,
			keypath=prefix,
			sphere=UserRoleSphere.Path.value
		)


	def get_users_of_path(
		self,
		prefix: str,
		owner: dtos.User | None=None
	) -> Iterator[dtos.RoledUser]:
		addSlash = True
		normalizedPrefix = normalize_opening_slash(prefix)
		rulesQuery = build_base_rules_query(UserRoleSphere.Path).cte()
		query = select(
			u_pk,
			u_username,
			u_displayName,
			u_email,
			tbl.u_dirRoot,
			tbl.u_publictoken,
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
					func.substring(
						normalizedPrefix,
						1,
						func.length(
							func.normalize_opening_slash(tbl.u_dirRoot, addSlash)
						)
					) == func.normalize_opening_slash(tbl.u_dirRoot, addSlash),
					rulesQuery.c["rule>userfk"] == 0
				),
				and_(
					rulesQuery.c["rule>userfk"] == u_pk,
						func.substring(
							normalizedPrefix,
							1,
							func.length(
								func.normalize_opening_slash(
									rulesQuery.c["rule>keypath"],
									addSlash
								)
							)
						) == func.normalize_opening_slash(
							rulesQuery.c["rule>keypath"],
							addSlash
						)
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == 0))\
		.where(
			or_(
				coalesce(
					rulesQuery.c["rule>priority"],
					RulePriorityLevel.SITE.value
				) > RulePriorityLevel.REQUIRES_INVITE.value,
					func.substring(
						prefix,
						1,
						func.length(
							func.normalize_opening_slash(tbl.u_dirRoot, addSlash)
						)
					) == func.normalize_opening_slash(tbl.u_dirRoot, addSlash)
			)
		)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_path_user_and_rules_from_rows(
			records,
			prefix
		)


	def get_song_path(
		self,
		itemIds: Union[Iterable[int], int]
	) -> Iterator[str]:
		query = select(sg_path).where(sg_deletedTimstamp.is_(None))
		if isinstance(itemIds, Iterable):
			query = query.where(sg_pk.in_(itemIds))
		else:
			query = query.where(sg_pk == itemIds)
		results = self.conn.execute(query)
		yield from (self.file_service.song_absolute_path(cast(str,row[0])) \
			for row in results
		)


	def get_permitted_paths_tree(
		self,
		user: RoledUser,
	) -> ChainedAbsorbentTrie[ActionRule]:
		pathTree = ChainedAbsorbentTrie[ActionRule](
			(normalize_opening_slash(r.keypath), r) for r in
			user.roles if r.sphere == UserRoleSphere.Path.value \
				and r.keypath is not None
		)
		pathTree.add("/", (
			ActionRule(**r.model_dump(exclude={"keypath"}), keypath = "/") 
			for r in user.roles \
			if r.keypath is None and (UserRoleSphere.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
		return pathTree


	def get_permitted_paths(
		self,
		user: RoledUser,
	) -> Iterator[str]:
		pathTree = self.get_permitted_paths_tree(user)
		yield from (p for p in pathTree.shortest_paths())