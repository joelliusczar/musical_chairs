from typing import Iterator
import pytest
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection
from musical_chairs_libs.tables import metadata, \
	artists, \
	albums, \
	songs, \
	song_artist
		
from sqlalchemy import insert

@pytest.fixture
def db_conn() -> WrappedDbConnection:
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
	return conn

@pytest.fixture
def db_conn_in_mem() -> Iterator[WrappedDbConnection]:
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection(inMemory=True)
	try:
		yield conn
	finally:
		conn.close()

@pytest.fixture
def setup_in_mem_tbls(db_conn_in_mem: WrappedDbConnection) -> None:
	metadata.create_all(db_conn_in_mem.engine)
	artistParams = [
		{ "name": "alpha_artist"},
		{ "name": "bravo_artist"},
		{ "name": "charlie_artist"},
		{ "name": "delta_artist"},
		{ "name": "echo_artist"},
		{ "name": "foxtrot_artist"},
		{ "name": "golf_artist"}
	]
	stmt = insert(artists)
	db_conn_in_mem.execute(stmt, artistParams)

@pytest.fixture
def setup_in_mem_tbls_full(db_conn_in_mem: WrappedDbConnection) -> None:
	setup_in_mem_tbls(db_conn_in_mem)
	albumParams = [
		{ "name": "hotel_album", "albumArtistFk": 7, "year": 2001 },
		{ "name": "india_album", "albumArtistFk": 7, "year": 2003 },
		{ "name": "juliet_album", "albumArtistFk": 7 },
		{ "name": "kilo_album", "year": 2004 },
		{ "name": "lima_album" },
		{ "name": "roo_album" },
		{ "name": "koo_album", "year": 2010 },
		{ "name": "shoo_album", "albumArtistFk": 6, "year": 2003 },
		{ "name": "who_2_album", "albumArtistFk": 6, "year": 2001 },
		{ "name": "who_1_album", "albumArtistFk": 5, "year": 2001 },
		{ "name": "boo_album", "albumArtistFk": 4, "year": 2001 },
	]
	stmt = insert(albums)
	db_conn_in_mem.execute(stmt, albumParams)
	songParams = [
		{ "path": "/foo/goo/boo/sierra", 
			"name": "sierra_song",
			"albumFk": 11,
			"track": 1,
			"disc": 1,
			"genre": "pop",
			"explicit": 0,
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/boo/tango", 
			"name": "tango_song",
			"albumFk": 11,
			"track": 2,
			"disc": 1,
			"genre": "pop",
			"explicit": 0,
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/boo/uniform", 
			"name": "uniform_song",
			"albumFk": 11,
			"track": 3,
			"disc": 1,
			"genre": "pop",
			"explicit": 1,
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/boo/victor", 
			"name": "victor_song",
			"albumFk": 11,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/boo/victor", 
			"name": "victor_song",
			"albumFk": 11,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"bitrate": 144,
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_1/whiskey", 
			"name": "whiskey_song",
			"albumFk": 10,
			"track": 1,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_1/xray", 
			"name": "xray_song",
			"albumFk": 10,
			"track": 2,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_1/yankee", 
			"name": "yankee_song",
			"albumFk": 10,
			"track": 3,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_1/zulu", 
			"name": "zulu_song",
			"albumFk": 10,
			"track": 4,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_1/alpha", 
			"name": "alpha_song",
			"albumFk": 10,
			"track": 5,
			"disc": 1,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_2/bravo", 
			"name": "bravo_song",
			"albumFk": 9,
			"track": 1,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_2/charlie", 
			"name": "charlie_song",
			"albumFk": 9,
			"track": 2,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_2/delta", 
			"name": "delta_song",
			"albumFk": 9,
			"track": 3,
			"disc": 2,
			"genre": "pop",
			"comment": "Kazoos make good swimmers"
		},
		{ "path": "/foo/goo/who_2/foxtrot", 
			"name": "foxtrot_song",
			"albumFk": 9,
			"track": 4,
			"disc": 2,
			"genre": "pop",
		},
		{ "path": "/foo/goo/who_2/golf", 
			"name": "golf_song",
			"albumFk": 9,
			"track": 5,
			"disc": 2,
			"genre": "pop",
		},
		{ "path": "/foo/goo/shoo/hotel", 
			"name": "hotel_song",
			"albumFk": 8,
			"track": 1,
			"disc": 1,
		},
		{ "path": "/foo/goo/shoo/india", 
			"name": "india_song",
			"albumFk": 8,
			"track": 2,
			"disc": 1,
		},
		{ "path": "/foo/goo/shoo/juliet", 
			"name": "juliet_song",
			"albumFk": 8,
			"track": 3,
			"disc": 1,
		},
		{ "path": "/foo/goo/shoo/kilo", 
			"name": "kilo_song",
			"albumFk": 8,
			"track": 4,
			"disc": 1,
		},
		{ "path": "/foo/goo/koo/lima", 
			"name": "lima_song",
			"albumFk": 7,
			"track": 1,
		},
		{ "path": "/foo/goo/koo/mike", 
			"name": "mike_song",
			"albumFk": 7,
			"track": 2,
		},
		{ "path": "/foo/goo/koo/november", 
			"name": "november_song",
			"albumFk": 7,
			"track": 3,
		},
		{ "path": "/foo/goo/roo/oscar", 
			"name": "oscar_song",
			"albumFk": 6,
		},
		{ "path": "/foo/goo/roo/papa", 
			"name": "papa_song",
			"albumFk": 6,
		},
		{ "path": "/foo/goo/roo/romeo", 
			"name": "romeo_song",
			"albumFk": 6,
		},
		{ "path": "/foo/goo/roo/sierra2", 
			"name": "sierra2_song",
			"albumFk": 6,
		},
		{ "path": "/foo/goo/roo/tango2", 
			"name": "tango2_song",
		},
		{ "path": "/foo/goo/roo/uniform2", 
			"name": "uniform2_song",
		},
		{ "path": "/foo/goo/roo/victor2", 
			"name": "victor2_song",
		},
		{ "path": "/foo/goo/roo/whiskey2", 
			"name": "whiskey2_song",
		},
		{ "path": "/foo/goo/roo/xray2", 
			"name": "xray2_song",
		}
	]
	stmt = insert(songs)
	db_conn_in_mem.execute(stmt, songParams)
	songArtistParams = [
		{ "songFk": 31, "artistFk": 1}
	]
	stmt = insert(song_artist)
	db_conn_in_mem.execute(stmt, songArtistParams)