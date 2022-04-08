import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

class ConfigLoader:

	def get_configured_db_connection(self, echo: bool = False) -> Connection:

		engine = create_engine(\
			f"sqlite+pysqlite:///{os.environ['dbName']}", \
			echo=echo)
		return engine.connect()