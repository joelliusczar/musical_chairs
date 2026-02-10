from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Iterator
from .constants import UserRoleSphere

@dataclass
class EventRecord:
	id: str
	userId: str
	action: str
	visitorId: int
	timestamp: float
	keypath: str | None
	sphere: str = UserRoleSphere.Site.value
	url: str = ""
	method: str = ""
	extraInfo: str=""

@dataclass
class VisitRecord:
	id: str
	visitorId: int
	timestamp: float
	url: str = ""
	method: str = ""
	extraInfo: str=""

type VisitsMethodDict =  defaultdict[str, deque[VisitRecord]]

type EventActionDict = defaultdict[str, deque[EventRecord]]

type EventPathDict = defaultdict[str | None, EventActionDict]

type EventDomainDict = defaultdict[str, EventPathDict]

type EventUserIdDict = defaultdict[
	str, #userId
	EventDomainDict
]

type VisitUrlDict = defaultdict[str, VisitsMethodDict]

type VisitVisitorIdDict = defaultdict[int, VisitUrlDict]

def __deque_factory__() -> deque[EventRecord]:
	return deque(maxlen=5_000)

def __vist_deque_factory__() -> deque[VisitRecord]:
	return deque(maxlen=5_000)

def __action_dict_factory__() -> EventActionDict:
	return defaultdict(__deque_factory__)

def __method_dict_factory__() -> VisitsMethodDict:
	return defaultdict(__vist_deque_factory__)

def __keypath_dict_factory__() -> EventPathDict:
	return defaultdict(__action_dict_factory__)

def __url_dict_factory__() -> VisitUrlDict:
	return defaultdict(__method_dict_factory__)

def __sphere_dict_factory__() -> EventDomainDict:
	return defaultdict(__keypath_dict_factory__)

def user_events_dict_factory() -> EventUserIdDict:
	return defaultdict(__sphere_dict_factory__)

def visitorId_dict_factory() -> VisitVisitorIdDict:
	return defaultdict(__url_dict_factory__)

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
	def events_for_keypaths(
		eventsParentMap: EventPathDict,
		actions: set[str] | None,
		keypath: str | None
	) -> Iterator[EventRecord]:
		if keypath:
			keypathEvents = eventsParentMap[keypath]
			yield from InMemEventRecordMap.events_for_actions(keypathEvents, actions)
		else:
			for keypathEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_actions(
					keypathEvents,
					actions
				)

	@staticmethod
	def visits_for_url(
		urlParentMap: VisitsMethodDict,
	)-> Iterator[VisitRecord]:
		for methodVists in urlParentMap.values():
			yield from (e for e in reversed(methodVists))


	@staticmethod
	def visits_for_visitor(
		visitsParentMap: VisitUrlDict,
		url: str | None = None
	) -> Iterator[VisitRecord]:
		if url:
			urlEvents = visitsParentMap[url]
			yield from InMemEventRecordMap.visits_for_url(urlEvents)
		else:
			for urlEvents in visitsParentMap.values():
				yield from InMemEventRecordMap.visits_for_url(
					urlEvents,
				)


	@staticmethod
	def events_for_sphere(
		eventsParentMap: EventDomainDict,
		actions: set[str] | None,
		keypath: str | None,
		sphere: str | None,
	) -> Iterator[EventRecord]:
		if sphere:
			sphereEvents = eventsParentMap[sphere]
			yield from InMemEventRecordMap.events_for_keypaths(
				sphereEvents,
				actions,
				keypath
			)
		else:
			for sphereEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_keypaths(
					sphereEvents,
					actions,
					keypath
				)


	@staticmethod
	def events_for_userId(
		eventsParentMap: EventUserIdDict,
		actions: set[str] | None,
		keypath: str | None,
		sphere: str | None,
		userId: str | None
	) -> Iterator[EventRecord]:
		if userId:
			userIdEvents = eventsParentMap[userId]
			yield from InMemEventRecordMap.events_for_sphere(
				userIdEvents,
				actions,
				keypath,
				sphere
			)
		else:
			for userIdEvents in eventsParentMap.values():
				yield from InMemEventRecordMap.events_for_sphere(
					userIdEvents,
					actions,
					keypath,
					sphere
				)

	@staticmethod
	def get_visits(
		visitsParentMap: VisitVisitorIdDict,
		visitorId: int | None = None,
		url: str | None = None
	) -> Iterator[VisitRecord]:
		if visitorId:
			visitorIdEvents = visitsParentMap[visitorId]
			yield from InMemEventRecordMap.visits_for_visitor(visitorIdEvents, url)
		else:
			for visitorIdEvents in visitsParentMap.values():
				yield from InMemEventRecordMap.visits_for_visitor(visitorIdEvents, url)

type TimeoutBucket = defaultdict[int, defaultdict[str, float]]

def timeout_factory():
	return defaultdict[str, float](lambda : 0)