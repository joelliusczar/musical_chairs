from .common_fixtures import db_conn
from sqlalchemy.engine import Connection
from typing import Callable
from musical_chairs_libs.queue_service import QueueService

def test_get_now_playing_and_queue(db_conn: Callable[[], Connection]):
	queueSevice = QueueService(db_conn)