#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
from .constant_fixtures_for_test import *
from .common_fixtures import fixture_queue_service as fixture_queue_service
from .common_fixtures import *
from musical_chairs_libs.services import QueueService



def test_adding_song_to_queue(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	queueService.fil_up_queue(1, 50)
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 19 #only 19 songs in test db
	result = queueService._add_song_to_queue(15, 1, 1)
	assert result == 1
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 20




