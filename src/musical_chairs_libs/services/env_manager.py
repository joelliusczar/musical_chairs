import os
from typing import Iterable, cast
from sqlalchemy import create_engine #pyright: ignore [reportUnknownVariableType]
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row
from musical_chairs_libs.tables import metadata
from musical_chairs_libs.dtos_and_utilities import (
	SearchNameString,
	SavedNameString,
	next_directory_level,
	normalize_opening_slash
)


class EnvManager:

	@classmethod
	@property
	def search_base(cls) -> str:
		return os.environ["searchBase"]

	@classmethod
	@property
	def db_name(cls) -> str:
		return os.environ["dbName"]

	@classmethod
	@property
	def templates_dir(cls) -> str:
		return os.environ["templateDir"]

	@classmethod
	@property
	def icecast_conf_location(cls) -> str:
		return os.environ["icecastConfLocation"]

	@classmethod
	@property
	def station_config_dir(cls) -> str:
		return os.environ["stationConfigDir"]

	@classmethod
	@property
	def station_module_dir(cls) -> str:
		return os.environ["stationModuleDir"]

	@classmethod
	def get_configured_db_connection(
		cls,
		echo: bool=False,
		inMemory: bool=False,
		checkSameThread: bool=True
	) -> Connection:

		dbStr = f"sqlite:///file::memory:?cache=shared&uri=true" \
			if inMemory else f"sqlite:///{cls.db_name}"

		engine = create_engine(
			dbStr,
			echo=echo,
			connect_args={ "check_same_thread": checkSameThread } #fastapi docs said this was okay
		)
		conn = engine.connect()
		conn.connection.connection.create_function( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
			"format_name_for_search",
			1,
			SearchNameString.format_name_for_search,
			deterministic=True
		)
		conn.connection.connection.create_function( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
			"format_name_for_save",
			1,
			SavedNameString.format_name_for_save,
			deterministic=True
		)
		conn.connection.connection.create_function( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
			"next_directory_level",
			2,
			next_directory_level,
			deterministic=True
		)
		conn.connection.connection.create_function( #pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
			"normalize_opening_slash",
			2,
			normalize_opening_slash,
			deterministic=True
		)
		return conn

	@classmethod
	def setup_db_if_missing(cls, echo: bool = False):
		if not os.path.exists(cls.db_name):
			conn = cls.get_configured_db_connection(echo=echo)

			metadata.create_all(conn.engine)
			conn.close()

	@classmethod
	def print_expected_schema(cls):
		conn = cls.get_configured_db_connection(inMemory=True)
		metadata.create_all(conn.engine)
		result = conn.execute("SELECT sql FROM sqlite_master WHERE type='table';") #pyright: ignore [reportUnknownMemberType]
		result = (cast(str,r[0]) for r in cast(Iterable[Row],result.fetchall()))
		print("\n".join(result))
		result = conn.execute("SELECT sql FROM sqlite_master WHERE type='index';") #pyright: ignore [reportUnknownMemberType]
		result = (cast(str,r[0]) for r in cast(Iterable[Row],result.fetchall()))
		print("\n".join(result))
		conn.close()
