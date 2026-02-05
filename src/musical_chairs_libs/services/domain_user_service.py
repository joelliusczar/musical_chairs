from .current_user_provider import CurrentUserProvider
from musical_chairs_libs.dtos_and_utilities import (
	build_base_rules_query,
	generate_domain_user_and_rules_from_rows,
	get_datetime,
	AccountInfo,
	ActionRule,
	RulePriorityLevel,
	UserRoleSphere,
	RuledOwnedEntity,
)

from musical_chairs_libs.tables import (

	userRoles as user_roles_tbl, ur_userFk, ur_keypath, ur_role, ur_sphere,
	users as user_tbl, u_username, u_pk, u_displayName, u_email, u_dirRoot,
	u_disabled,
)
from sqlalchemy import (
	select,
	insert,
	or_,
	and_,
	delete,
)
from sqlalchemy.engine import Connection
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import coalesce
from typing import (
	Callable,
	Iterator,
)



class DomainUserService:

	def __init__(
		self,
		conn: Connection,
		currentUserProvider: CurrentUserProvider,
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime
		self.current_user_provider = currentUserProvider


	def add_domain_rule_to_user(
		self,
		addedUserId: int,
		domain: str,
		keypath: str | None,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(user_roles_tbl).values(
			userfk = addedUserId,
			keypath = keypath,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp(),
			sphere = domain
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.INVITED_USER.value,
			keypath=keypath,
			sphere=domain
		)


	def get_domain_users(
		self,
		entity: RuledOwnedEntity,
		sphere: UserRoleSphere,
		ownerRuleProvider: Callable[[], Iterator[ActionRule]],
	) -> Iterator[AccountInfo]:
		rulesQuery = build_base_rules_query(sphere).cte()
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
					(u_pk == entity.owner.id) if entity.owner else false(),
					rulesQuery.c["rule>userfk"] == 0
				),
				and_(
					rulesQuery.c["rule>userfk"] == u_pk,
					rulesQuery.c["rule>keypath"] == str(entity.id),
					rulesQuery.c["rule>sphere"] == sphere.value
				)
			),
			isouter=True
		).where(or_(u_disabled.is_(None), u_disabled == False))\
		.where(
			or_(
				coalesce(
					rulesQuery.c["rule>priority"],
					RulePriorityLevel.SITE.value
				) > RulePriorityLevel.REQUIRES_INVITE.value,
				(u_pk == entity.owner.id) if entity.owner else false()
			)
		)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()

		yield from generate_domain_user_and_rules_from_rows(
			records,
			ownerRuleProvider,
			entity.owner.id if entity.owner else None
		)


	def remove_domain_rule_from_user(
		self,
		userId: int,
		sphere: str,
		keypath: str | None,
		ruleName: str | None
	):
		delStmt = delete(user_roles_tbl)\
			.where(ur_sphere == sphere)\
			.where(ur_userFk == userId)\
			.where(ur_keypath == keypath)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]