import os
import json
from typing import (
	Optional,
	Iterator,
	Iterable,
	Collection
)
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	EventRecord,
	get_datetime,
	ActionRule,
	UserRoleDomain,
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


class EventsQueryService:

#must not add userProvider as dependency here
	def __init__(self):
		self.get_datetime = get_datetime

	def load_most_recent_logs(self, hoursAgo: int) -> Iterator[EventRecord]:
		daysLogs = sorted(os.listdir(ConfigAcessors.event_log_dir()))[:hoursAgo]
		for log in daysLogs:
			fullPath = os.path.join(ConfigAcessors.event_log_dir(), log)
			with open(fullPath, "r", 1) as f:
				while line := f.readline():
					yield EventRecord(**json.loads(line))


	def get_user_action_history(
		self,
		userId: int,
		fromTimestamp: float,
		actions: Iterable[str]=[],
		domain: Optional[str] = None,
		path: Optional[str] = None,
		limit: Optional[int]=None
	) -> Iterator[EventRecord]:
			actions = {*actions}
			events = reversed([e for e in self.load_most_recent_logs(24) \
				if e.userId == str(userId)\
				and (e.action in actions if actions else True)\
				and fromTimestamp <= e.timestamp\
				and (domain == e.domain if domain else True) \
				and (path == e.path if domain and path else True)
			])

			yield from (e for i, e in enumerate(events)\
				 if (i < limit if limit is not None else True)
			)


	def calc_lookup_for_when_user_can_next_do_action(
		self,
		userid: int,
		rules: Collection[ActionRule],
		domain: str = UserRoleDomain.Site.value,
		path: Optional[str]=None,
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
			domain=domain,
			path=path,
			limit=maxLimit
		)
		presorted = {g[0]:[i.timestamp for i in g[1]] for g in groupby(
			actionGen,
			key=lambda k: k.action
		)}
		result = {
			r.name:__when_next_can_do__(
				r,
				presorted.get(r.name, []),
				currentTimestamp
			) for r in ActionRule.filter_out_repeat_roles(rules)
		}
		return result
