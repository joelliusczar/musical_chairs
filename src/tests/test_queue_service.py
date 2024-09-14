#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
from .constant_fixtures_for_test import *
from .common_fixtures import fixture_queue_service as fixture_queue_service
from .common_fixtures import *
from musical_chairs_libs.services import QueueService



def test_adding_song_to_queue(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	queueService.fil_up_queue(1, queueService.queue_size)
	queue1, _ = queueService.get_queue_for_station(1)
	assert len(queue1) == 15 #only 19 songs in test db
	result = queueService.__add_song_to_queue__(15, 1, 1)
	assert result == 1
	queue1, _ = queueService.get_queue_for_station(1)
	assert len(queue1) == 16


def test_queue_of_songs_without_artists(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	queueService.fil_up_queue(8, queueService.queue_size)
	queue1, _ = queueService.get_queue_for_station(8)
	assert len(queue1) == 4

# def test_queue_with_skips_and_offsets(fixture_queue_service: QueueService):
# 	queueService = fixture_queue_service
# 	queueService.fil_up_queue(26, queueService.queue_size)
# 	originalQueue = list(queueService.get_queue_for_station(26))

# 	loaded = [queueService.pop_next_queued(26)]
# 	assert loaded[0].id == originalQueue[0].id
# 	loaded.append(queueService.pop_next_queued(26, loaded=set(loaded)))
# 	assert loaded[1].id == originalQueue[1].id
# 	#start playing song 1
# 	nowPlaying = loaded[0]
# 	moved = queueService.move_from_queue_to_history(
# 		26,
# 		nowPlaying.id,
# 		nowPlaying.queuedtimestamp
# 	)
# 	assert moved

# 	assert len(loaded) == 2
# 	assert loaded[0].id == originalQueue[1].id

# 	loaded.append(queueService.pop_next_queued(26, loaded=set(loaded)))
# 	assert len(loaded) == 3
# 	assert loaded[1].id == originalQueue[2].id
# 	loaded.append(queueService.pop_next_queued(26, loaded=set(loaded)))
# 	assert len(loaded) == 4
# 	assert loaded[2].id == originalQueue[3].id
# 	loaded.append(queueService.pop_next_queued(26, loaded=set(loaded)))
# 	assert len(loaded) == 5
# 	assert loaded[3].id == originalQueue[4].id

# 	pass
