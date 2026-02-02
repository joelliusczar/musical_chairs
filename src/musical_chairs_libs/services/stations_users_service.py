from .current_user_provider import CurrentUserProvider
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime
)
from sqlalchemy.engine import Connection
from sqlalchemy import (
	select,
	insert,
	or_,
	and_,
	delete,
)
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import coalesce
from musical_chairs_libs.dtos_and_utilities import (
	build_base_rules_query,
	generate_domain_user_and_rules_from_rows,
	get_station_owner_rules,
	StationInfo,
	get_datetime,
	AccountInfo,
	ActionRule,
	RulePriorityLevel,
	UserRoleSphere,
)
from musical_chairs_libs.tables import (

	userRoles as user_roles_tbl, ur_userFk, ur_keypath, ur_role,
	users as user_tbl, u_username, u_pk, u_displayName, u_email, u_dirRoot,
	u_disabled,
)
from typing import (
	Iterator,
	Optional,
)


class StationsUsersService:

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


	def add_user_rule_to_station(
		self,
		addedUserId: int,
		stationId: int,
		rule: ActionRule
	) -> ActionRule:
		stmt = insert(user_roles_tbl).values(
			userfk = addedUserId,
			keypath = stationId,
			role = rule.name,
			span = rule.span,
			quota = rule.quota,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp(),
			sphere = UserRoleSphere.Station.value
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return ActionRule(
			name=rule.name,
			span=rule.span,
			quota=rule.quota,
			priority=RulePriorityLevel.INVITED_USER.value,
			sphere=UserRoleSphere.Station.value
		)
	
	def get_station_users(
		self,
		station: StationInfo,
	) -> Iterator[AccountInfo]:
		rulesQuery = build_base_rules_query(UserRoleSphere.Station).cte()
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
					(u_pk == station.owner.id) if station.owner else false(),
					rulesQuery.c["rule>userfk"] == 0
				),
				and_(
					rulesQuery.c["rule>userfk"] == u_pk,
					rulesQuery.c["rule>keypath"] == str(station.id),
					rulesQuery.c["rule>sphere"] == UserRoleSphere.Station.value
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
				(u_pk == station.owner.id) if station.owner else false()
			)
		)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()

		yield from generate_domain_user_and_rules_from_rows(
			records,
			get_station_owner_rules,
			station.owner.id if station.owner else None
		)

	def remove_user_rule_from_station(
		self,
		userId: int,
		stationId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(user_roles_tbl)\
			.where(ur_userFk == userId)\
			.where(ur_keypath == stationId)
		if ruleName:
			delStmt = delStmt.where(ur_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]