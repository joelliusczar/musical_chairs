import yaml
import os
from typing import Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

class ConfigLoader:

	def __init__(self) -> None:
			self._config: Optional(dict[str, Any]) = None

	@property
	def config(self) -> dict[str, Any]:  
		if self._config:
			return self._config
		config_path = os.environ["config_file"]

		self._config = None

		with open(config_path,"r") as stream:
			self._config =  yaml.safe_load(stream)
		return self._config

	def get_http_config(self) -> dict[str, Any]:
		config_path = os.environ["http_config"]

		with open(config_path,"r") as stream:
			config =  yaml.safe_load(stream)
		return config

	def get_configured_db_connection(self, echo = False) -> Connection:
		config = self.config
		engine = create_engine(f"sqlite+pysqlite:///{config['dbName']}", echo=echo)
		return engine.connect()