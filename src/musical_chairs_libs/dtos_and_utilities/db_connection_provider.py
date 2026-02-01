import re
from sqlalchemy import create_engine, NullPool
from sqlalchemy.engine import Connection
from sqlalchemy.event import listens_for
from musical_chairs_libs.dtos_and_utilities.constants import DbUsers
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT
from typing import Any
from .config_accessors import ConfigAcessors
from .name_strings import (
	SearchNameString,
	SavedNameString
)
from .simple_functions import (
	next_directory_level,
	normalize_opening_slash
)


collation_connection = "utf8mb4_uca1400_ai_ci"

def __on_connect__(**kw: dict[str, Any]): 
	dbapi_connection = kw["dbapi_connection"]
	#somewhere between mariahdb 11.8.3 and 10.6.22, the default collation_connection
	#became utf8mb4_uca1400_ai_ci which causes problems with next_directory_level.
	#Supposedly, you should be able to add connect_args={'init_command': "SET @@collation_connection='utf8mb4_unicode_ci'"}
	#to the engine constructor, but apparently there is another bug described here
	#https://github.com/sqlalchemy/sqlalchemy/discussions/7858 
	#that seems to indicate that collation_connection is being overwritten
	dbapi_connection.query(f"SET @@collation_connection='{collation_connection}'") #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue]

class DbConnectionProvider:


	@classmethod
	def sqlite_connection(cls,
		echo: bool=False,
		inMemory: bool=False,
		check_same_thread: bool=True
	) -> Connection:

		if inMemory:
			engine = create_engine(
				"sqlite://",
				echo=echo,
				connect_args={ "check_same_thread": check_same_thread }, #fastapi docs said this was okay
				# poolclass=NullPool
			)
		else:
			engine = create_engine(
				f"sqlite:///{ConfigAcessors.db_file()}",
				echo=echo,
				connect_args={ "check_same_thread": check_same_thread }, #fastapi docs said this was okay
				poolclass=NullPool
			)

		conn = engine.connect()
		conn.connection.connection.create_function( 
			"format_name_for_search",
			1,
			SearchNameString.format_name_for_like,
			deterministic=True
		)
		conn.connection.connection.create_function(
			"format_name_for_save",
			1,
			SavedNameString.format_name_for_save,
			deterministic=True
		)
		conn.connection.connection.create_function(
			"next_directory_level",
			2,
			next_directory_level,
			deterministic=True
		)
		conn.connection.connection.create_function(
			"normalize_opening_slash",
			2,
			normalize_opening_slash,
			deterministic=True
		)

		def regexp_replace(input: Any, pattern: str, replacement: str):
			return re.sub(pattern, replacement, input)

		conn.connection.connection.create_function(
			"regexp_replace",
			3,
			regexp_replace,
			deterministic=True
		)

		return conn


	@classmethod
	def get_configured_api_connection(
		cls,
		dbName: str,
		echo: bool=False
	) -> Connection:
		dbPass = ConfigAcessors.db_pass_api()
		if not dbPass:
			raise RuntimeError("API: The system is not configured correctly for that.")
		engine = create_engine(
			f"mysql+pymysql://{DbUsers.API_USER()}:{dbPass}@localhost/{dbName}",
			echo=echo,
		)
		
		listens_for(engine, "connect", named=True)(__on_connect__)


		conn = engine.connect()
		return conn


	@classmethod
	def get_configured_janitor_connection(
		cls,
		dbName: str,
		echo: bool=False
	) -> Connection:
		dbPass = ConfigAcessors.db_pass_janitor()
		if not dbPass:
			raise RuntimeError("Janitor: The system is not configured correctly for that.")
		engine = create_engine(
			f"mysql+pymysql://{DbUsers.JANITOR_USER()}:{dbPass}@localhost/{dbName}",
			echo=echo,
			connect_args={
				"client_flag": CLIENT.MULTI_STATEMENTS | CLIENT.MULTI_RESULTS
			},
		)

		listens_for(engine, "connect", named=True)(__on_connect__)
		conn = engine.connect()
		return conn


	@classmethod
	def get_configured_radio_connection(
		cls,
		dbName: str,
		echo: bool=False,
		isolationLevel: str="REPEATABLE READ"
	) -> Connection:
		dbPass = ConfigAcessors.db_pass_radio()
		if not dbPass:
			raise RuntimeError("Radio: The system is not configured correctly for that.")
		engine = create_engine(
			f"mysql+pymysql://{DbUsers.RADIO_USER()}:{dbPass}@localhost/{dbName}",
			echo=echo,
			execution_options={
        "isolation_level": isolationLevel
    	}
		)
		listens_for(engine, "connect", named=True)(__on_connect__)
		return engine.connect()