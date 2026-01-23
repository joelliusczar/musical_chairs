from musical_chairs_libs.services import (
	EventsLoggingService
)
from .constant_fixtures_for_test import *
from .common_fixtures import *
from .mocks.db_data import juliet_user_id
from .mocks.mock_datetime_provider import MockDatetimeProvider
from .common_fixtures import (
	fixture_datetime_iterator as fixture_datetime_iterator
)

def test_get_user_action_history(
	fixture_user_actions_history_service: EventsLoggingService,
	fixture_datetime_iterator: MockDatetimeProvider,
):
	dates = fixture_datetime_iterator
	historyService = fixture_user_actions_history_service
	res = list(historyService.get_user_action_history(
		juliet_user_id,
		dates[0].timestamp() - 1000,
		limit=3
	))
	assert res
	res = list(historyService.get_user_action_history(
		juliet_user_id,
		dates[0].timestamp() - 1000,
		limit=3,
		# stationIds=[2, 5, 6]
	))
	assert res