from typing import Protocol, Callable
from datetime import datetime
from sqlalchemy.engine import Connection
from musical_chairs_libs.services import EnvManager
from musical_chairs_libs.dtos_and_utilities import AccountInfo
from musical_chairs_libs.tables import metadata
from .db_population import populate_artists,\
	populate_albums,\
	populate_songs,\
	populate_songs_artists,\
	populate_tags,\
	populate_songs_tags,\
	populate_stations,\
	populate_station_tags,\
	populate_users,\
	populate_user_roles

class ConnectionConstructor(Protocol):
	def __call__(
		self,
		echo: bool=False,
		inMemory: bool=False,
		checkSameThread: bool=True
	) -> Connection:
			...

def setup_in_mem_tbls(
	conn: Connection,
	orderedTestDates: list[datetime],
	primaryUser: AccountInfo,
	testPassword: bytes
) -> None:
	metadata.create_all(conn.engine)
	populate_artists(conn)
	populate_albums(conn)
	populate_songs(conn)
	populate_songs_artists(conn)
	populate_tags(conn)
	populate_songs_tags(conn)
	populate_stations(conn)
	populate_station_tags(conn)
	populate_users(conn, orderedTestDates, primaryUser, testPassword)
	populate_user_roles(conn, orderedTestDates, primaryUser)

def construct_mock_connection_constructor(
	dbPopulate: Callable[[Connection], None]
) -> ConnectionConstructor:

	def get_mock_db_connection_constructor(
		echo: bool=False,
		inMemory: bool=False,
		checkSameThread: bool=True
	) -> Connection:
		envMgr = EnvManager()
		conn = envMgr.get_configured_db_connection(
			echo=echo,
			inMemory=True,
			checkSameThread=checkSameThread
		)
		dbPopulate(conn)
		return conn
	return get_mock_db_connection_constructor