import os
import json
from typing import (
	Optional,
	Iterator,
)
from musical_chairs_libs.protocols import EventsQueryer
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	EventRecord,
	get_datetime,
)



class FSEventsQueryService(EventsQueryer):

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


	def get_user_events(
		self,
		userId: int | None,
		fromTimestamp: float,
		actions: set[str] | None = None,
		sphere: str | None = None,
		keypath: str | None = None,
		limit: int | None = None
	) -> Iterator[EventRecord]:
			events = reversed([e for e in self.load_most_recent_logs(24) \
				if (e.userId == str(userId) if userId else True)\
				and (e.action in actions if actions else True)\
				and fromTimestamp <= e.timestamp\
				and (sphere == e.sphere if sphere else True) \
				and (keypath == e.keypath if sphere and keypath else True)
			])

			yield from (e for i, e in enumerate(events)\
				 if (i < limit if limit is not None else True)
			)


	def get_visitor_events(
		self,
		visitorId: int,
		fromTimestamp: float,
		url: Optional[str] = None,
		limit: Optional[int]=None
	)-> Iterator[EventRecord]:
		events = reversed([e for e in self.load_most_recent_logs(24) \
			if e.visitorId == visitorId\
			and fromTimestamp <= e.timestamp\
			and (url == e.url if url else True)
		])

		yield from (e for i, e in enumerate(events)\
				if (i < limit if limit is not None else True)
		)
