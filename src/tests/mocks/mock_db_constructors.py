import pytest
from typing import (Protocol, Optional)
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import AccountInfo
from .mock_datetime_provider import MockDatetimeProvider
from .db_population import (
	populate_artists,
	populate_albums,
	populate_songs,
	populate_songs_artists,
	populate_stations_songs,
	populate_station_albums,
	populate_stations,
	populate_station_queue,
	populate_playlists,
	populate_playlists_songs,
	populate_station_playlists
)
from .db_data import (
	populate_path_permissions,
	populate_playlist_permissions,
	populate_station_permissions,
	populate_users,
	populate_user_roles,
)

class ConnectionConstructor(Protocol):
	def __call__(
		self,
		echo: bool=False,
		inMemory: bool=False
	) -> Connection:
			...

class MockDbPopulateClosure(Protocol):
	def __call__(
		self,
		conn: Connection,
		request: Optional[pytest.FixtureRequest]=None
	) -> None:
		...


def setup_in_mem_tbls(
	conn: Connection,
	request: Optional[pytest.FixtureRequest],
	datetimeProvider: MockDatetimeProvider,
	primaryUser: AccountInfo,
	testPassword: bytes,
) -> None:
	populate_users(conn, datetimeProvider, primaryUser, testPassword)
	populate_artists(conn)
	populate_albums(conn)
	populate_songs(conn)
	populate_songs_artists(conn)
	populate_stations(conn)
	populate_stations_songs(conn)
	populate_station_albums(conn)
	populate_user_roles(conn, datetimeProvider, primaryUser)
	populate_station_permissions(conn, datetimeProvider)
	populate_path_permissions(conn, datetimeProvider)
	populate_station_queue(conn)
	populate_playlists(conn)
	populate_station_playlists(conn)
	populate_playlists_songs(conn)
	populate_playlist_permissions(conn, datetimeProvider)
	conn.commit()
