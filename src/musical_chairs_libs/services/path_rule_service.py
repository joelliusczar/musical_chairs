from typing import Iterator, cast, Optional
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
from musical_chairs_libs.dtos_and_utilities import (
	PathsActionRule,
	RulePriorityLevel,
	normalize_opening_slash,
	AccountInfo,
	ChainedAbsorbentTrie,
	ActionRule,
	get_path_owner_roles,
	UserRoleDomain,
	UserRoleDef,
	build_rules_query,
	get_datetime,
	MinItemSecurityLevel,
	generate_user_and_rules_from_rows
)
from musical_chairs_libs.tables import (
	path_user_permissions as path_user_permissions_tbl,
	pup_userFk, pup_path, pup_role, pup_priority, pup_span, pup_count,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, u_dirRoot,
	u_disabled
)

class PathRuleService:

	def __init__(
		self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime


	def get_paths_user_can_see(self, userId: int) -> Iterator[PathsActionRule]:
		query = select(pup_path, pup_role, pup_priority, pup_span, pup_count)\
			.where(pup_userFk == userId)\
			.order_by(pup_path)
		records = self.conn.execute(query).mappings()
		for r in records:
			yield PathsActionRule(
				name=cast(str,r[pup_role]),
				priority=cast(int,r[pup_priority]) \
					or RulePriorityLevel.STATION_PATH.value,
				span=cast(int,r[pup_span]) or 0,
				count=cast(int,r[pup_count]) or 0,
				path=normalize_opening_slash(cast(str,r[pup_path]))
			)

	def get_rule_path_tree(
		self,
		user: AccountInfo
	) -> ChainedAbsorbentTrie[ActionRule]:
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
		)

		pathRuleTree = ChainedAbsorbentTrie[ActionRule](
			(normalize_opening_slash(p.path), p) for p in
				rules if isinstance(p, PathsActionRule) and p.path
		)
		pathRuleTree.add("", (r for r in user.roles \
			if type(r) == ActionRule \
				and (UserRoleDomain.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
		return pathRuleTree

	def remove_user_rule_from_path(
		self,
		userId: int,
		prefix: str,
		ruleName: Optional[str]
	):
		delStmt = delete(path_user_permissions_tbl)\
			.where(pup_userFk == userId)\
			.where(pup_path == prefix)
		if ruleName:
			delStmt = delStmt.where(pup_role == ruleName)
		self.conn.execute(delStmt)

	def add_user_rule_to_path(
		self,
		addedUserId: int,
		prefix: str,
		rule: ActionRule
	) -> PathsActionRule:
		stmt = insert(path_user_permissions_tbl).values(
			userFk = addedUserId,
			path = prefix,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationTimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return PathsActionRule(
			name=rule.name,
			span=rule.span,
			count=rule.count,
			priority=RulePriorityLevel.STATION_PATH.value,
			path=prefix
		)

	def get_users_of_path(
		self,
		prefix: str,
		userId: Optional[int]=None,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		addSlash = True
		normalizedPrefix = normalize_opening_slash(prefix)
		rulesQuery = build_rules_query(UserRoleDomain.Path).cte()
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
					func.substring(
						normalizedPrefix,
						1,
						func.length(
							func.normalize_opening_slash(u_dirRoot, addSlash)
						)
					) == func.normalize_opening_slash(u_dirRoot, addSlash),
					rulesQuery.c.rule_userfk == 0
				),
				and_(
					rulesQuery.c.rule_userfk == u_pk,
						func.substring(
							normalizedPrefix,
							1,
							func.length(
								func.normalize_opening_slash(rulesQuery.c.rule_path, addSlash)
							)
						) == func.normalize_opening_slash(rulesQuery.c.rule_path, addSlash)
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == 0))\
		.where(
			or_(
				coalesce(
					rulesQuery.c.rule_priority,
					RulePriorityLevel.SITE.value
				) > MinItemSecurityLevel.INVITED_USER.value,
					func.substring(
						prefix,
						1,
						func.length(
							func.normalize_opening_slash(u_dirRoot, addSlash)
						)
					) == func.normalize_opening_slash(u_dirRoot, addSlash)
			)
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_user_and_rules_from_rows(
			records,
			UserRoleDomain.Path,
			owner.id if owner else None,
			prefix
		)