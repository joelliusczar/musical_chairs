from musical_chairs_libs.dtos_and_utilities.event_dtos import VisitRecord
from musical_chairs_libs.protocols import (
	EventsLogger,
)
from musical_chairs_libs.dtos_and_utilities import (
	EventRecord,
)



class AggregateEventsLoggingService(EventsLogger):

	def __init__(self, *eventsLoggers: EventsLogger) -> None:
		self.events_loggers = eventsLoggers


	def add_event(
		self,
		action: str,
		sphere: str,
		keypath: str | None = None,
		extraInfo: str = ""
	) -> EventRecord:
		if not any(self.events_loggers):
			raise RuntimeError("No events loggers were provided")
		loggerIter = iter(self.events_loggers)
		logger1 = next(loggerIter)
		record = logger1.add_event(action, sphere, keypath, extraInfo)
		while loggerN := next(loggerIter, None):
			loggerN.add_event_record(record)
		return record



	def add_event_record(self, record: EventRecord):
		for logger in self.events_loggers:
			logger.add_event_record(record)

	
	def add_visit_record(self, record: VisitRecord):
		for logger in self.events_loggers:
			logger.add_visit_record(record)


	def add_visit(self, extraInfo: str = "") -> VisitRecord:
		if not any(self.events_loggers):
			raise RuntimeError("No events loggers were provided")
		loggerIter = iter(self.events_loggers)
		logger1 = next(loggerIter)
		record = logger1.add_visit(extraInfo)
		while loggerN := next(loggerIter, None):
			loggerN.add_visit_record(record)
		return record