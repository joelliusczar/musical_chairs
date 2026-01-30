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
	RulePriorityLevel,
	normalize_opening_slash,
	AccountInfo,
	ChainedAbsorbentTrie,
	ActionRule,
	get_path_owner_roles,
	UserRoleSphere,
	UserRoleDef,
	build_path_rules_query,
	get_datetime,
	generate_path_user_and_rules_from_rows
)
from musical_chairs_libs.tables import (
	path_user_permissions as path_user_permissions_tbl,
	pup_userFk, pup_path, pup_role, pup_priority, pup_span, pup_count,
	users as user_tbl, u_pk, u_username, u_displayName, u_email, u_dirRoot,
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


	def get_paths_user_can_see(self) -> Iterator[ActionRule]:
		userId = self.user_provider.current_user().id
		query = select(pup_path, pup_role, pup_priority, pup_span, pup_count)\
			.where(pup_userFk == userId)\
			.order_by(pup_path)
		records = self.conn.execute(query).mappings()
		for r in records:
			yield ActionRule(
				name=cast(str,r[pup_role]),
				priority=cast(int,r[pup_priority]) \
					or RulePriorityLevel.STATION_PATH.value,
				span=cast(int,r[pup_span]) or 0,
				quota=cast(int,r[pup_count]) or 0,
				keypath=normalize_opening_slash(cast(str,r[pup_path])),
				sphere=UserRoleSphere.Path.value
			)


	def get_rule_path_tree(
		self
	) -> ChainedAbsorbentTrie[ActionRule]:
		user = self.user_provider.current_user()
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.get_paths_user_can_see()),
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
		delStmt = delete(path_user_permissions_tbl)\
			.where(pup_userFk == subjectUserId)\
			.where(pup_path == prefix)
		if ruleName:
			delStmt = delStmt.where(pup_role == ruleName)
		self.conn.execute(delStmt)

	def add_user_rule_to_path(
		self,
		addedUserId: int,
		prefix: str,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(path_user_permissions_tbl).values(
			userfk = addedUserId,
			keypath = prefix,
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
			keypath=prefix,
			sphere=UserRoleSphere.Path.value
		)


	def get_users_of_path(
		self,
		prefix: str,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		addSlash = True
		normalizedPrefix = normalize_opening_slash(prefix)
		rulesQuery = build_path_rules_query().cte()
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
								func.normalize_opening_slash(
									rulesQuery.c.rule_keypath,
									addSlash
								)
							)
						) == func.normalize_opening_slash(
							rulesQuery.c.rule_keypath,
							addSlash
						)
				),
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == 0))\
		.where(
			or_(
				coalesce(
					rulesQuery.c.rule_priority,
					RulePriorityLevel.SITE.value
				) > RulePriorityLevel.INVITED_USER.value,
					func.substring(
						prefix,
						1,
						func.length(
							func.normalize_opening_slash(u_dirRoot, addSlash)
						)
					) == func.normalize_opening_slash(u_dirRoot, addSlash)
			)
		)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_path_user_and_rules_from_rows(
			records,
			owner.id if owner else None,
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