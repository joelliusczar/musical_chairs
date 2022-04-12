from .common_fixtures import db_conn as db_conn
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection
from musical_chairs_libs.queue_service import QueueService

def test_get_now_playing_and_queue(db_conn: WrappedDbConnection):
	print(db_conn)
	queueSevice = QueueService(db_conn)
	res = queueSevice.get_now_playing_and_queue(stationName="VG")
	print(res)