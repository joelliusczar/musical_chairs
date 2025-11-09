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
	StationInfo,
	get_datetime,
	AccountInfo,
	ActionRule,
	StationActionRule,
	RulePriorityLevel,
	build_station_rules_query,
	generate_station_user_and_rules_from_rows,
)
from musical_chairs_libs.tables import (

	station_user_permissions as station_user_permissions_tbl, stup_userFk,
	stup_stationFk, stup_role,
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
		conn: Connection
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime

	def add_user_rule_to_station(
		self,
		addedUserId: int,
		stationId: int,
		rule: ActionRule
	) -> StationActionRule:
		stmt = insert(station_user_permissions_tbl).values(
			userfk = addedUserId,
			stationfk = stationId,
			role = rule.name,
			span = rule.span,
			count = rule.count,
			priority = None,
			creationtimestamp = self.get_datetime().timestamp()
		)
		self.conn.execute(stmt)
		self.conn.commit()
		return StationActionRule(
			name=rule.name,
			span=rule.span,
			count=rule.count,
			priority=RulePriorityLevel.STATION_PATH.value
		)
	
	def get_station_users(
		self,
		station: StationInfo,
		userId: Optional[int]=None
	) -> Iterator[AccountInfo]:
		rulesQuery = build_station_rules_query().cte()
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
					(u_pk == station.owner.id) if station.owner else false(),
					rulesQuery.c.rule_userfk == 0
				),
				and_(
					rulesQuery.c.rule_userfk == u_pk,
					rulesQuery.c.rule_stationfk == station.id
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
				(u_pk == station.owner.id) if station.owner else false()
			)
		)
		if userId is not None:
			query = query.where(u_pk == userId)
		query = query.order_by(u_username)
		records = self.conn.execute(query).mappings()
		yield from generate_station_user_and_rules_from_rows(
			records,
			station.owner.id if station.owner else None
		)

	def remove_user_rule_from_station(
		self,
		userId: int,
		stationId: int,
		ruleName: Optional[str]
	):
		delStmt = delete(station_user_permissions_tbl)\
			.where(stup_userFk == userId)\
			.where(stup_stationFk == stationId)
		if ruleName:
			delStmt = delStmt.where(stup_role == ruleName)
		self.conn.execute(delStmt) #pyright: ignore [reportUnknownMemberType]