from typing import Iterator, cast
from sqlalchemy import (
	select,
)
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
	UserRoleDef
)
from musical_chairs_libs.tables import (
	pup_userFk, pup_path, pup_role, pup_priority, pup_span, pup_count,
)

class PathRuleService:

	def __init__(
		self,
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn


	def get_paths_user_can_see(self, userId: int) -> Iterator[PathsActionRule]:
		query = select(pup_path, pup_role, pup_priority, pup_span, pup_count)\
			.where(pup_userFk == userId)\
			.order_by(pup_path)
		records = self.conn.execute(query).mappings()
		for r in records:
			yield PathsActionRule(
				cast(str,r[pup_role]),
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
			(p for p in get_path_owner_roles(user.dirroot))
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