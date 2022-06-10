import os
from sqlalchemy import create_engine #pyright: ignore [reportUnknownVariableType]
from sqlalchemy.engine import Connection
from musical_chairs_libs.tables import metadata
from musical_chairs_libs.dtos import SearchNameString, SavedNameString

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
	def get_configured_db_connection(cls,
		echo: bool=False,
		inMemory: bool=False,
		check_same_thread: bool=True
	) -> Connection:

		dbStr = "sqlite://" if inMemory  else f"sqlite:///{cls.db_name}"

		engine = create_engine(
			dbStr,
			echo=echo,
			connect_args={ "check_same_thread": check_same_thread } #fastapi docs said this was okay
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
		return conn

	@classmethod
	def setup_db_if_missing(cls, replace: bool=False, echo: bool = False):
		if replace:
			os.remove(cls.db_name)
		if not os.path.exists(cls.db_name):
			conn = cls.get_configured_db_connection(echo=echo)
			metadata.create_all(conn.engine)
			conn.close()
