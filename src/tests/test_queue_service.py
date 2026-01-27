#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
from .common_fixtures import (
	fixture_queue_service as fixture_queue_service,
	fixture_clean_queue_files as fixture_clean_queue_files
)
from .common_fixtures import *
from musical_chairs_libs.dtos_and_utilities import QueueMetrics
from musical_chairs_libs.services import QueueService

@pytest.mark.usefixtures("fixture_clean_queue_files")
@pytest.mark.current_username("testUser_alpha")
def test_adding_song_to_queue(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	m = QueueMetrics(maxSize=queueService.queue_size)
	station = queueService.__get_station__(1)
	queueService.fil_up_queue(station, m, [])
	queue1, _ = queueService.get_queue_for_station(1)
	assert len(queue1) == 15 #only 19 songs in test db
	queueService.add_to_queue(15, station)
	queue1, _ = queueService.get_queue_for_station(1)
	assert len(queue1) == 16


@pytest.mark.usefixtures("fixture_clean_queue_files")
def test_queue_of_songs_without_artists(fixture_queue_service: QueueService):
	queueService = fixture_queue_service
	m = QueueMetrics(maxSize=queueService.queue_size)
	station = queueService.__get_station__(8)
	queueService.fil_up_queue(station, m, [])
	queue1, _ = queueService.get_queue_for_station(8)
	assert len(queue1) == 4


@pytest.mark.usefixtures("fixture_clean_queue_files")
def test_if_song_can_be_added_to_station(
	fixture_queue_service: QueueService
):
	queueService = fixture_queue_service
	result = queueService.can_song_be_queued_to_station(15, 1)
	assert result == True
	result = queueService.can_song_be_queued_to_station(15, 2)
	assert result == False
	result = queueService.can_song_be_queued_to_station(36, 1)
	assert result == False


@pytest.mark.usefixtures("fixture_clean_queue_files")
def test_if_not_crashing_one_song_station(
	fixture_queue_service: QueueService
):
	queueService = fixture_queue_service
	stationId = 21
	# queueService.fil_up_queue(stationId, queueService.queue_size)
	# queueService.conn.commit()
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)


@pytest.mark.usefixtures("fixture_clean_queue_files")
def test_if_not_crashing_3_song_station(
	fixture_queue_service: QueueService
):
	queueService = fixture_queue_service
	stationId = 6
	# queueService.fil_up_queue(stationId, queueService.queue_size)
	# queueService.conn.commit()
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	


@pytest.mark.usefixtures("fixture_clean_queue_files")
def test_queue(
	fixture_queue_service: QueueService
):
	queueService = fixture_queue_service
	stationId = 1
	# queueService.fil_up_queue(stationId, queueService.queue_size)
	# queueService.conn.commit()
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)
	queueService.__move_next__(stationId)


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
