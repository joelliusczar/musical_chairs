#pyright: reportMissingTypeStubs=false, reportPrivateUsage=false
import pytest
from datetime import datetime, timezone
from .constant_fixtures_for_test import test_password as test_password,\
	primary_user as primary_user,\
	test_date_ordered_list as test_date_ordered_list
from .common_fixtures import \
	db_conn as db_conn, \
	db_conn_in_mem_full as db_conn_in_mem_full, \
	queue_service_in_mem as queue_service_in_mem
from musical_chairs_libs.queue_service import QueueService
from sqlalchemy import insert
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import stations_history, station_queue
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.accounts_service import UserRoleDef


currentTestDate: datetime = datetime.now(timezone.utc)

def test_get_now_playing_and_queue(db_conn: Connection):
	print(db_conn)
	queueSevice = QueueService(db_conn)
	queueSevice.get_now_playing_and_queue(stationName="vg")

def _insert_row_into_history(conn: Connection, userPk: int):
	queuedTimestamp = \
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=10,
			tzinfo=timezone.utc
		).timestamp()
	historyParams = [{
			"stationFk": 1,
			"songFk": 15,
			"playedTimestamp": datetime(
				year=2022,
				month=5,
				day=27,
				hour=19,
				minute=20,
				tzinfo=timezone.utc
			).timestamp(),
			"queuedTimestamp": queuedTimestamp,
			"requestedTimestamp": queuedTimestamp,
			"requestedByUserFk": userPk
		}
	]
	stmt = insert(stations_history)
	conn.execute(stmt, historyParams) #pyright: ignore [reportUnknownMemberType]

@pytest.fixture
def queue_service_mock_current_time(queue_service_in_mem: QueueService):
	def _get_test_datetime() -> datetime:
		return currentTestDate
	queue_service_in_mem.get_datetime = _get_test_datetime
	return queue_service_in_mem

def test_when_can_make_request_with_history(
	queue_service_mock_current_time: QueueService,
	primary_user: AccountInfo
):
	queueService = queue_service_mock_current_time
	_insert_row_into_history(queueService.conn, 1)

	primary_user.roles = [f"{UserRoleDef.SONG_REQUEST.value}60"]
	global currentTestDate
	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=25,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 2700

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 0

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			second=1,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 0

def _insert_row_into_queue(conn: Connection, userPk: int):
	queuedTimestamp = \
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=10,
			tzinfo=timezone.utc
		).timestamp()
	queueParams = [{
			"stationFk": 1,
			"songFk": 15,
			"queuedTimestamp": queuedTimestamp,
			"requestedTimestamp": queuedTimestamp,
			"requestedByUserFk": userPk
		}
	]
	stmt = insert(station_queue)
	conn.execute(stmt, queueParams) #pyright: ignore [reportUnknownMemberType]

def test_when_can_make_request_with_queue(
	queue_service_mock_current_time: QueueService,
	primary_user: AccountInfo
):
	queueService = queue_service_mock_current_time
	_insert_row_into_queue(queueService.conn, 1)

	primary_user.roles = [f"{UserRoleDef.SONG_REQUEST.value}60"]
	global currentTestDate
	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=25,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 2700

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 0

	currentTestDate =\
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=20,
			minute=10,
			second=1,
			tzinfo=timezone.utc
		)
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 0

def test_when_song_can_be_added_without_role(
	queue_service_mock_current_time: QueueService,
	primary_user: AccountInfo
):
	queueService = queue_service_mock_current_time
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == -1

def test_when_song_can_be_added_with_admin(
	queue_service_mock_current_time: QueueService,
	primary_user: AccountInfo
):
	queueService = queue_service_mock_current_time
	primary_user.roles = [UserRoleDef.ADMIN.value]
	result = queueService.time_til_user_can_make_request(primary_user)
	assert result == 0

def test_adding_song_to_queue(queue_service_in_mem: QueueService):
	queueService = queue_service_in_mem
	queueService.fil_up_queue(1, 50)
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 19 #only 19 songs in test db
	result = queueService._add_song_to_queue(15, 1, 1)
	assert result == 1
	queue1 = list(queueService.get_queue_for_station(1))
	assert len(queue1) == 20

@pytest.mark.echo(True)
def test_if_song_can_be_added_to_station(queue_service_in_mem: QueueService):
	queueService = queue_service_in_mem
	result = queueService.can_song_be_queued_to_station(15, 1)
	assert result == True
	result = queueService.can_song_be_queued_to_station(15, 2)
	assert result == False
	result = queueService.can_song_be_queued_to_station(36, 1)
	assert result == False


