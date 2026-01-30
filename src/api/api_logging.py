from api_dependencies import (
	aggregate_events_logging_service,
	current_user_provider,
	get_from_path_subject_user,
	vistor_tracking_service
)
from fastapi import (
	Depends
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	StationInfo,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	UserActions,
	UserRoleSphere,
)
from musical_chairs_libs.protocols import (
	EventsLogger,
	UserProvider,
	TrackingInfoProvider,
)
from station_validation import get_station

def log_event(sphere: str, action: str):

	def __site_log_event__(eventsLogger: EventsLogger =
		Depends(aggregate_events_logging_service)
	):
		yield
		eventsLogger.add_event(action, sphere)

	def __current_user_log_event__(
		currentUserProvider : UserProvider = Depends(current_user_provider),
		eventsLogger: EventsLogger =
			Depends(aggregate_events_logging_service),
	):
		yield
		currentUserId = currentUserProvider.current_user().id
		eventsLogger.add_event(action, sphere, str(currentUserId))

	def __subject_user_log_event__(
		subjectUser: AccountInfo = Depends(get_from_path_subject_user),
		eventsLogger: EventsLogger =
			Depends(aggregate_events_logging_service),
	):
		yield
		eventsLogger.add_event(action, sphere, str(subjectUser.id))
	
	def __station_log_event__(
		station: StationInfo = Depends(get_station),
		eventsLogger: EventsLogger =
			Depends(aggregate_events_logging_service),
	):
		yield
		eventsLogger.add_event(
			action,
			sphere,
			str(station.id)
		)

	if sphere == UserRoleSphere.Site.value:
		return __site_log_event__
	if sphere == UserRoleSphere.User.value:
		subjectUserActions = {
			UserActions.ADD_SITE_RULE.value,
			UserActions.REMOVE_SITE_RULE.value
		}
		if action in subjectUserActions:
			return __subject_user_log_event__
		
		return __current_user_log_event__
	if sphere == UserRoleSphere.Station.value:
		return __station_log_event__


def log_visit(eventsLogger: EventsLogger =
	Depends(aggregate_events_logging_service),
	vistorTrackingService: TrackingInfoProvider = Depends(vistor_tracking_service)
):
	yield