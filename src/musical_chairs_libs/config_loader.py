import os
from sqlalchemy import create_engine
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection

class ConfigLoader:

	@property
	def search_base(self) -> str:
		return os.environ["searchBase"]

	def get_configured_db_connection(self, 
		echo: bool = False
	) -> WrappedDbConnection:

		engine = create_engine(\
			f"sqlite+pysqlite:///{os.environ['dbName']}", \
			echo=echo)
		conn = engine.connect()
		return WrappedDbConnection(conn)