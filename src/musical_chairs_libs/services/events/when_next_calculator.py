from itertools import groupby
from musical_chairs_libs.protocols import (
	EventsQueryer,
	UserProvider
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	UserRoleSphere,
	get_datetime,
	TooManyRequestsError,
	WrongPermissionsError,
)
from typing import (
	Collection,
	Optional
)


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

	if len(timestamps) == rule.quota:
		return timestamps[0] + rule.span
	return 0


class WhenNextCalculator:

	def __init__(
		self,
		eventQueryer: EventsQueryer,
		userProvider: UserProvider
	):
		self.event_queryer = eventQueryer
		self.user_provider = userProvider
		self.get_datetime = get_datetime

	
	def calc_lookup_for_when_user_can_next_do_action(
		self,
		userid: int,
		rules: Collection[ActionRule],
		sphere: str = UserRoleSphere.Site.value,
		path: Optional[str]=None,
	) -> dict[str, Optional[float]]:
		if not rules:
			return {}
		maxLimit = max(int(r.quota) for r in rules)
		maxSpan = max(r.span for r in rules)
		currentTimestamp = self.get_datetime().timestamp()
		fromTimestamp = currentTimestamp - maxSpan
		actionGen = self.event_queryer.get_user_events(
			userid,
			fromTimestamp,
			actions={r.name for r in rules},
			sphere=sphere,
			keypath=path,
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
	

	def check_if_user_can_perform_rate_limited_action(
		self,
		conformingScope: set[str],
		rules: list[ActionRule],
		sphere: str
	):
		if not rules and conformingScope:
			raise WrongPermissionsError()
		user = self.user_provider.current_user()
		timeoutLookup = \
			self.calc_lookup_for_when_user_can_next_do_action(
				user.id,
				rules,
				sphere
			)
		for scope in conformingScope:
			if scope in timeoutLookup:
				whenNext = timeoutLookup[scope]
				if whenNext is None:
					raise WrongPermissionsError()
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise TooManyRequestsError(int(timeleft))