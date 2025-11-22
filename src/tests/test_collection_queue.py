from .common_fixtures import (
	fixture_queue_service as fixture_queue_service,
	fixture_collection_queue_service as fixture_collection_queue_service
)
from .common_fixtures import *
from musical_chairs_libs.services import QueueService, CollectionQueueService


def test_adding_album_to_queue(
	fixture_queue_service: QueueService,
	fixture_collection_queue_service: CollectionQueueService
):
	queueService = fixture_queue_service
	collectionQueueService = fixture_collection_queue_service
	collectionQueueService.fil_up_queue(26,3)
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
	count = collectionQueueService.queue_count(29)
	assert count
	assert count <= (collectionQueueService.queue_size + 1)


def test_get_catalogue(
	fixture_collection_queue_service: CollectionQueueService
):
	collectionQueueService = fixture_collection_queue_service
	collections, totalRows = collectionQueueService.get_catalogue(
		stationId = 26
	)
	assert {c.id for c in collections} == {7,8,9,10,11}
	assert totalRows == 5