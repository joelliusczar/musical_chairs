from .common_fixtures import (
	fixture_queue_service as fixture_queue_service,
	fixture_album_queue_service as fixture_album_queue_service,
	fixture_collection_queue_service as fixture_collection_queue_service
)
from .common_fixtures import *
from musical_chairs_libs.services import (
	QueueService,
	AlbumQueueService,
	CollectionQueueService,
)


def test_adding_album_to_queue(
	fixture_queue_service: QueueService,
	fixture_album_queue_service: AlbumQueueService
):
	queueService = fixture_queue_service
	albumQueueService = fixture_album_queue_service
	albumQueueService.fil_up_queue(26,3)
	queue1, _ = queueService.get_queue_for_station(26)
	assert queue1

def test_pop_next_on_empty(
	fixture_queue_service: QueueService,
	fixture_album_queue_service: AlbumQueueService
):
	queueService = fixture_queue_service
	albumQueueService = fixture_album_queue_service

	popped = albumQueueService.pop_next_queued(29)
	queue, count = queueService.get_queue_for_station(29)
	assert popped
	assert queue
	assert count

def test_queue_count(
	fixture_album_queue_service: AlbumQueueService
):
	albumQueueService = fixture_album_queue_service

	albumQueueService.pop_next_queued(29)
	count = albumQueueService.queue_count(29)
	assert count
	assert count <= (albumQueueService.queue_size + 1)


def test_get_catalogue(
	fixture_album_queue_service: AlbumQueueService
):
	albumQueueService = fixture_album_queue_service
	collections, totalRows = albumQueueService.get_catalogue(
		stationId = 26
	)
	assert {c.id for c in collections} == {7,8,9,10,11}
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
			queue[0]["songId"],
			queue[0]["queuedTimestamp"],
		)
		idx += 1
		collectionQueueService.pop_next_queued(30)
		return [*collectionQueueService.get_queue_for_station(30)]
	queue = [*collectionQueueService.get_queue_for_station(30)]
	assert not queue
	collectionQueueService.pop_next_queued(30)

	queue = [*collectionQueueService.get_queue_for_station(30)]
	queue = move_next()
	# while True:
	# 	pass

