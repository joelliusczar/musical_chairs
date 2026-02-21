from .common_fixtures import (
	fixture_queue_service as fixture_queue_service,
	fixture_collection_queue_service as fixture_collection_queue_service
)
from .common_fixtures import *
from musical_chairs_libs.dtos_and_utilities import (
	QueueMetrics,
	SimpleQueryParameters
)
from musical_chairs_libs.services import (
	QueueService,
	CollectionQueueService,
)


def test_adding_album_to_queue(
	fixture_queue_service: QueueService,
	fixture_collection_queue_service: CollectionQueueService
):
	queueService = fixture_queue_service
	collectionQueueService = fixture_collection_queue_service
	station = collectionQueueService.queue_service.__get_station__(26)
	collectionQueueService.fil_up_queue_in_trx(station, QueueMetrics(maxSize=3))
	queue1, _ = queueService.get_queue_for_station(26)
	assert queue1

def test_pop_next_on_empty(
	fixture_queue_service: QueueService,
	fixture_collection_queue_service: CollectionQueueService
):
	queueService = fixture_queue_service
	collectionQueueService = fixture_collection_queue_service

	popped = collectionQueueService.pop_next_queued(29)
	queue, count = queueService.get_queue_for_station(29)
	assert popped
	assert queue
	assert count


def test_queue_count(
	fixture_collection_queue_service: CollectionQueueService
):
	collectionQueueService = fixture_collection_queue_service

	collectionQueueService.pop_next_queued(29)
	station = collectionQueueService.queue_service.__get_station__(29)
	alreadyQueued = [*collectionQueueService.load_current_queue(station)]
	count = collectionQueueService.queue_count(alreadyQueued)
	assert count
	assert count <= (collectionQueueService.queue_size + 1)


def test_get_catalogue(
	fixture_collection_queue_service: CollectionQueueService
):
	collectionQueueService = fixture_collection_queue_service
	collections, totalRows = collectionQueueService.get_catalogue(
		stationId = 26,
		queryParams=SimpleQueryParameters()
	)
	assert {c.decoded_id() for c in collections} == {7,8,9,10,11}
	assert totalRows == 5


def test_collection_pop_next(
	fixture_collection_queue_service: CollectionQueueService
):
	collectionQueueService = fixture_collection_queue_service
	idx = 0
	def move_next():
		nonlocal idx
		collectionQueueService.move_from_queue_to_history(
			30,
			queue[0].id,
			queue[0].queuedtimestamp,
		)
		idx += 1
		collectionQueueService.pop_next_queued(30)
		return collectionQueueService.get_queue_for_station(30)[0]
	queue, _ = collectionQueueService.get_queue_for_station(30)
	collectionQueueService.pop_next_queued(30)

	queue, _ = collectionQueueService.get_queue_for_station(30)
	for _ in range(0, 100):
		queue = move_next()
		assert queue
		# while True:
	# 	pass


def test_collection_queue_with_loaded(
	fixture_collection_queue_service: CollectionQueueService
):
	collectionQueueService = fixture_collection_queue_service
	loaded: set[Any] = set()
	popped = collectionQueueService.pop_next_queued(30)
	loaded.add(popped)

	loaded.add(collectionQueueService.pop_next_queued(30, loaded))