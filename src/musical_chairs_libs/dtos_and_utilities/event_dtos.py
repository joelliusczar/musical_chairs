from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Iterator
from .account_dtos import UserRoleDomain

@dataclass
class EventRecord:
	id: str
	userId: str
	action: str
	visitorId: int
	timestamp: float
	path: str | None
	domain: str = UserRoleDomain.Site.value
	url: str = ""
	extraInfo: str=""

type EventActionDict = defaultdict[str, deque[EventRecord]]

type EventPathDict = defaultdict[str | None, EventActionDict]

type EventDomainDict = defaultdict[str, EventPathDict]

type EventUserIdDict = defaultdict[
	str, #userId
	EventDomainDict
]

type EventUrlDict = EventActionDict

type EventVisitorIdDict = defaultdict[int, EventUrlDict]

def __deque_factory__() -> deque[EventRecord]:
	return deque(maxlen=1000)

def __action_dict_factory__() -> EventActionDict:
	return defaultdict(__deque_factory__)

def __path_dict_factory__() -> EventPathDict:
	return defaultdict(__action_dict_factory__)

def __domain_dict_factory__() -> EventDomainDict:
	return defaultdict(__path_dict_factory__)

def user_events_dict_factory() -> EventUserIdDict:
	return defaultdict(__domain_dict_factory__)

def visitorId_dict_factory() -> EventVisitorIdDict:
	return defaultdict(__action_dict_factory__)

class InMemEventRecordMap:

	def __init__(self) -> None:
		self.userEvents = user_events_dict_factory()
		self.vistorEvents = visitorId_dict_factory()


	def __len__(self) -> int:
		return len(self.userEvents) or len(self.vistorEvents)


	@staticmethod
	def events_for_actions(
		eventsParentMap: EventActionDict, 
		actions: set[str] | None,
	) -> Iterator[EventRecord]:
		if actions:
			for action in actions:
				events = eventsParentMap[action]
				yield from (e for e in reversed(events))
		else:
			for events in eventsParentMap.values():
				yield from (e for e in reversed(events))


	@staticmethod
	def events_for_paths(
		eventsParentMap: EventPathDict,
		actions: set[str] | None,
		path: str | None
	) -> Iterator[EventRecord]:
		if path:
			pathEvents = eventsParentMap[path]
			yield from InMemEventRecordMap.events_for_actions(pathEvents, actions)
		else:
			for pathEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_actions(pathEvents, actions)


	@staticmethod
	def events_for_domain(
		eventsParentMap: EventDomainDict,
		actions: set[str] | None,
		path: str | None,
		domain: str | None,
	) -> Iterator[EventRecord]:
		if domain:
			domainEvents = eventsParentMap[domain]
			yield from InMemEventRecordMap.events_for_paths(
				domainEvents,
				actions,
				path
			)
		else:
			for domainEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_paths(
					domainEvents,
					actions,
					path
				)


	@staticmethod
	def events_for_userId(
		eventsParentMap: EventUserIdDict,
		actions: set[str] | None,
		path: str | None,
		domain: str | None,
		userId: str | None
	) -> Iterator[EventRecord]:
		if userId:
			userIdEvents = eventsParentMap[userId]
			yield from InMemEventRecordMap.events_for_domain(
				userIdEvents,
				actions,
				path,
				domain
			)
		else:
			for userIdEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_domain(
					userIdEvents,
					actions,
					path,
					domain
				)