#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
from datetime import datetime, timezone
from .constant_fixtures_for_test import test_password as test_password,\
	primary_user as primary_user,\
	test_date_ordered_list as test_date_ordered_list
from .common_fixtures import \
	db_conn as db_conn, \
	db_conn_in_mem_full as db_conn_in_mem_full, \
	queue_service_in_mem as queue_service_in_mem
from musical_chairs_libs.queue_service import QueueService
from sqlalchemy.engine import Connection


currentTestDate: datetime = datetime.now(timezone.utc)

def test_get_now_playing_and_queue(db_conn: Connection):
	print(db_conn)
	queueSevice = QueueService(db_conn)
	queueSevice.get_now_playing_and_queue(stationName="vg")

def test_adding_song_to_queue(queue_service_in_mem: QueueService):
	queueService = queue_service_in_mem
	queueService.fil_up_queue(1, 50)
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 19 #only 19 songs in test db
	result = queueService._add_song_to_queue(15, 1, 1)
	assert result == 1
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 20




