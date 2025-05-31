import hashlib
from typing import (
	Optional,
	Iterator,
	cast,
	Iterable,
	Union,
	overload,
	Collection
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	get_datetime,
	UserHistoryActionItem,
	StationHistoryActionItem,
	ActionRule,
	StationInfo,
	TrackingInfo
)
from sqlalchemy import (
	select,
	insert,
	func
)
from musical_chairs_libs.tables import (
	user_action_history, uah_userFk, uah_action, uah_pk,
	uah_queuedTimestamp,
	station_queue, q_stationFk, q_userActionHistoryFk,
	user_agents, uag_pk, uag_content, uag_hash, uag_length
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
		conn: Optional[Connection]=None
	) -> None:
		if not conn:
			raise RuntimeError("No connection provided")
		self.conn = conn
		self.get_datetime = get_datetime

	@overload
	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		stationIds: None=None,
		actions: Iterable[str]=[],
		limit: Optional[int]=None,
	) -> Iterator[UserHistoryActionItem]:
		...

	@overload
	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		stationIds: Iterable[int],
		actions: Iterable[str]=[],
		limit: Optional[int]=None,
	) -> Iterator[StationHistoryActionItem]:
		...

	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		stationIds: Optional[Iterable[int]]=None,
		actions: Iterable[str]=[],
		limit: Optional[int]=None
	) -> Union[
				Iterator[UserHistoryActionItem],
				Iterator[StationHistoryActionItem]
			]:
		query = select(
			uah_action,
			uah_queuedTimestamp,
			func.row_number().over( #pyright: ignore [reportUnknownMemberType]
				partition_by=[q_stationFk, uah_action] if stationIds else uah_action,
				order_by=uah_queuedTimestamp
			).label("rownum")
		)\
		.select_from(user_action_history)\
		.where(uah_queuedTimestamp >= fromTimestamp)\
		.where(uah_userFk == userId)
		if stationIds:
			query = query.add_columns(q_stationFk)\
				.join(station_queue, q_userActionHistoryFk == uah_pk)\
				.where(q_stationFk.in_(stationIds))
		if stationIds:
			query = query.order_by(q_stationFk)
		if actions:
			query = query.where(uah_action.in_(actions))
		query = query.order_by(uah_action, uah_queuedTimestamp)
		subquery = query.subquery()
		query = select(*subquery.c)
		if limit is not None:
			query = query.where(subquery.c.rownum < limit)

		records = self.conn.execute(query).mappings().fetchall()
		if stationIds:
			#apparently these do need to be the strings and not the 
			#column objects
			yield from (
				StationHistoryActionItem(
					userid=userId,
					action=cast(str,row["action"]), 
					timestamp=cast(float,row["queuedtimestamp"]),
					stationid=cast(int, row["stationfk"])
				)
				for row in records
			)

		else:
			yield from (
				UserHistoryActionItem(
					userid=userId,
					action=cast(str,row["action"]),
					timestamp=cast(float,row["queuedtimestamp"])
				)
				for row in records
			)

	def add_user_agent(self, userAgent: str) -> Optional[int]:
		userAgentHash = hashlib.md5(userAgent.encode()).digest()
		userAgentLen = len(userAgent)
		query = select(uag_pk, uag_content)\
			.where(uag_hash == userAgentHash)\
			.where(uag_length == userAgentLen)
		results = self.conn.execute(query).mappings()
		for row in results:
			if userAgent == row[uag_content]:
				return row[uag_pk]
		stmt = insert(user_agents).values(
			content = userAgent,
			hash = userAgentHash,
			length = userAgentLen
		)
		insertedIdRow = self.conn.execute(stmt).inserted_primary_key
		if insertedIdRow:
			return insertedIdRow[0]


	def add_user_action_history_item(
			self,
			userId: int,
			action: str,
			trackingInfo: TrackingInfo
		) -> Optional[int]:
		userAgentId = self.add_user_agent(trackingInfo.userAgent)
		timestamp = self.get_datetime().timestamp()
		stmt = insert(user_action_history).values(
			userfk = userId,
			action = action,
			queuedtimestamp = timestamp,
			ipv4address = trackingInfo.ipv4Address,
			ipv6address = trackingInfo.ipv6Address,
			useragentsfk = userAgentId
		)
		insertedIdRow = self.conn.execute(stmt).inserted_primary_key
		if insertedIdRow:
			return insertedIdRow[0]



	def calc_lookup_for_when_user_can_next_do_action(
		self,
		userid: int,
		rules: Collection[ActionRule],
	) -> dict[str, Optional[float]]:
		if not rules:
			return {}
		maxLimit = max(int(r.count) for r in rules)
		maxSpan = max(r.span for r in rules)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - maxSpan
		actionGen = self.get_user_action_history(
			userid,
			fromTimestamp,
			actions=(r.name for r in rules),
			limit=maxLimit
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
		maxLimit = max(int(r.count) for s in stations for r in s.rules)
		maxSpan = max(r.span for s in stations for r in s.rules)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - maxSpan
		actionGen = self.get_user_action_history(
			userId,
			fromTimestamp,
			(s.id for s in stations),
			{r.name for s in stations for r in s.rules},
			maxLimit,
		)
		presorted = {s[0]:{
				a[0]:[i.timestamp for i in a[1]] for a in
					groupby(
						s[1],
						lambda k: k.action
					)
			} for s in groupby(
			actionGen,
			key=lambda k: k.stationid
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