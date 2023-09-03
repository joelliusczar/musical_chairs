from typing import (
	Optional,
	Iterator,
	cast,
	Iterable,
	Union,
	overload,
	Collection
)
from .env_manager import EnvManager
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	UserHistoryActionItem,
	StationHistoryActionItem,
	ActionRule,
	StationInfo
)
from sqlalchemy import (
	select,
	insert,
	func
)
from musical_chairs_libs.tables import (
	user_action_history, uah_userFk, uah_action, uah_pk,
	uah_requestedTimestamp,
	station_queue, q_stationFk, q_userActionHistoryFk
)
from itertools import groupby

def __when_next_can_do__(
	rule: ActionRule,
	timestamps: list[float],
	currentTimestamp: float
) -> Optional[float]:
	if rule.noLimit:
		return 0
	if rule.blocked:
		return None
	fromTimestamp = currentTimestamp - rule.span
	#the main query can be overly permissive if
	#there is a mismatch of strictness
	timestamps = [t for t in timestamps if t >= fromTimestamp]
	if not timestamps:
		return 0

	if len(timestamps) == rule.count:
		return timestamps[0] + rule.span
	return 0


class UserActionsHistoryService:

	def __init__(self,
		conn: Optional[Connection]=None,
		envManager: Optional[EnvManager]=None
	) -> None:
		if not conn:
			if not envManager:
				envManager = EnvManager()
			conn = envManager.get_configured_db_connection()
		self.conn = conn
		self.get_datetime = get_datetime

	@overload
	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		actions: Iterable[str]=[],
		limit: Optional[int]=None,
		stationIds: None=None
	) -> Iterator[UserHistoryActionItem]:
		...

	@overload
	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		actions: Iterable[str]=[],
		limit: Optional[int]=None,
		stationIds: Iterable[int]=[]
	) -> Iterator[StationHistoryActionItem]:
		...

	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		actions: Iterable[str]=[],
		limit: Optional[int]=None,
		stationIds: Optional[Iterable[int]]=None
	) -> Union[
				Iterator[UserHistoryActionItem],
				Iterator[StationHistoryActionItem]
			]:
		query = select(
			uah_action,
			uah_requestedTimestamp,
			func.row_number().over(
				partition_by=[q_stationFk, uah_action] if stationIds else uah_action,
				order_by=uah_requestedTimestamp
			).label("rowNum")
		)\
		.select_from(user_action_history)\
		.where(uah_requestedTimestamp >= fromTimestamp)\
		.where(uah_userFk == userId)
		if stationIds:
			query = query.add_columns(q_stationFk)\
				.join(station_queue, q_userActionHistoryFk == uah_pk)\
				.where(q_stationFk.in_(stationIds))
		if stationIds:
			query = query.order_by(q_stationFk)
		if actions:
			query = query.where(uah_action.in_(actions))
		query = query.order_by(uah_action, uah_requestedTimestamp)
		subquery = query.subquery()
		query = select(*subquery.c)
		if limit is not None:
			query = query.where(subquery.c.rowNum < limit)

		records = self.conn.execute(query).fetchall() #pyright: ignore reportUnknownMemberType
		if stationIds:
			yield from (
				StationHistoryActionItem(
					userId,
					cast(str,row[uah_action]),
					cast(float,row[uah_requestedTimestamp]),
					cast(int, row[q_stationFk])
				)
				for row in records
			)

		else:
			yield from (
				UserHistoryActionItem(
					userId,
					cast(str,row[uah_action]),
					cast(float,row[uah_requestedTimestamp])
				)
				for row in records
			)

	def add_user_action_history_item(self, userId: int, action: str):
		stmt = insert(user_action_history).values(
			userFk = userId,
			action = action,
			timestamp = self.get_datetime().timestamp(),
		)
		res = self.conn.execute(stmt) #pyright: ignore reportUnknownMemberType

	def calc_lookup_for_when_user_can_next_do_action(
		self,
		userId: int,
		rules: Collection[ActionRule],
	) -> dict[str, Optional[float]]:
		if not rules:
			return {}
		maxLimit = max(r.count for r in rules)
		maxSpan = max(r.span for r in rules)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - maxSpan
		actionGen = self.get_user_action_history(
			userId,
			fromTimestamp,
			(r.name for r in rules),
			maxLimit
		)
		presorted = {g[0]:[i.timestamp for i in g[1]] for g in groupby(
			actionGen,
			key=lambda k: k.action
		)}
		result = {
			r.name:__when_next_can_do__(
				r,
				presorted.get(r.name,[]),
				currentTimestamp
			) for r in ActionRule.filter_out_repeat_roles(rules)
		}
		return result

	def calc_lookup_for_when_user_can_next_do_station_action(
		self,
		userId: int,
		stations: Collection[StationInfo],
	) -> dict[int, dict[str, Optional[float]]]:
		if not stations:
			return {}
		if not any(r for s in stations for r in s.rules):
			return {}
		maxLimit = max(r.count for s in stations for r in s.rules)
		maxSpan = max(r.span for s in stations for r in s.rules)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - maxSpan
		actionGen = self.get_user_action_history(
			userId,
			fromTimestamp,
			{r.name for s in stations for r in s.rules},
			maxLimit,
			(s.id for s in stations)
		)
		presorted = {s[0]:{
				a[0]:[i.timestamp for i in a[1]] for a in
					groupby(
						s[1],
						lambda k: k.action
					)
			} for s in groupby(
			actionGen,
			key=lambda k: k.stationId
		)}
		result = {s.id: {
				r.name:__when_next_can_do__(
					r,
					presorted.get(s.id,{}).get(r.name,[]),
					currentTimestamp
				)
				for r in ActionRule.filter_out_repeat_roles(s.rules)
			}
			for s in stations
		}
		return result