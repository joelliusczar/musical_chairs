import os
from sqlalchemy import create_engine #pyright: ignore [reportUnknownVariableType]
from sqlalchemy.engine import Connection

class EnvManager:

	@property
	def search_base(self) -> str:
		return os.environ["searchBase"]

	def get_configured_db_connection(self,
		echo: bool=False,
		inMemory: bool=False
	) -> Connection:

		dbStr = "sqlite://" if inMemory  else f"sqlite:///{os.environ['dbName']}"

		engine = create_engine(dbStr, echo=echo)
		conn = engine.connect()
		return conn