from .common_fixtures import *
from sqlalchemy.engine import Connection
from musical_chairs_libs.queue_service import QueueService

def test_get_now_playing_and_queue(db_conn: Connection):
	print(db_conn)
	#queueSevice = QueueService(db_conn)