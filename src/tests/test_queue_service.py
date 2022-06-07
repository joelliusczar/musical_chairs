#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
from datetime import datetime, timezone
from .constant_fixtures_for_test import\
	fixture_mock_password as fixture_mock_password,\
	fixture_primary_user as fixture_primary_user,\
	fixture_mock_ordered_date_list as fixture_mock_ordered_date_list
from .common_fixtures import \
	fixture_populated_db_conn_in_mem as fixture_populated_db_conn_in_mem, \
	fixture_queue_service as fixture_queue_service
from musical_chairs_libs.queue_service import QueueService


currentTestDate: datetime = datetime.now(timezone.utc)


def test_adding_song_to_queue(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	queueService.fil_up_queue(1, 50)
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 19 #only 19 songs in test db
	result = queueService._add_song_to_queue(15, 1, 1)
	assert result == 1
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 20




