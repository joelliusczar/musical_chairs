from musical_chairs_libs.services import (
	UserActionsHistoryService
)
from .constant_fixtures_for_test import *
from .common_fixtures import *
from .mocks.db_data import juliet_user_id
from .constant_fixtures_for_test import (
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
)

def test_get_user_action_history(
	fixture_user_actions_history_service: UserActionsHistoryService,
	fixture_mock_ordered_date_list: List[datetime],
):
	dates = fixture_mock_ordered_date_list
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
		stationIds=[2, 5, 6]
	))
	assert res