#pyright: reportMissingTypeStubs=false
from .common_fixtures import db_conn as db_conn
from musical_chairs_libs.queue_service import QueueService
from sqlalchemy.engine import Connection

def test_get_now_playing_and_queue(db_conn: Connection):
	print(db_conn)
	queueSevice = QueueService(db_conn)
	res = queueSevice.get_now_playing_and_queue(stationName="vg")
	print(res)