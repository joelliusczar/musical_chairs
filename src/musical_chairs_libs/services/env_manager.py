import os
import re
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	DbUsers
)


class EnvManager:

	@classmethod
	@property
	def app_root(cls) -> str:
		if EnvManager.test_flag:
			return os.environ["MC_TEST_ROOT"]
		return os.environ["MC_APP_ROOT"]

	@classmethod
	@property
	def search_base(cls) -> str:
		contentHome = os.environ["MC_CONTENT_HOME"]
		return f"{EnvManager.app_root}/{contentHome}"

	@classmethod
	@property
	def db_setup_pass(cls) -> str:
		return os.environ.get("__DB_SETUP_PASS__", "")

	@classmethod
	@property
	def db_pass_api(cls) -> str:
		return os.environ.get("MC_DB_PASS_API", "")

	@classmethod
	@property
	def db_pass_radio(cls) -> str:
		return os.environ.get("MC_DB_PASS_RADIO", "")

	@classmethod
	@property
	def db_pass_owner(cls) -> str:
		return os.environ.get("MC_DB_PASS_OWNER", "")

	@classmethod
	@property
	def templates_dir(cls) -> str:
		templateDir = os.environ["MC_TEMPLATES_DIR_CL"]
		return f"{EnvManager.app_root}/{templateDir}"

	@classmethod
	@property
	def station_config_dir(cls) -> str:
		configDir = os.environ["MC_ICES_CONFIGS_DIR"]
		return f"{EnvManager.app_root}/{configDir}"

	@classmethod
	@property
	def station_module_dir(cls) -> str:
		moduleDir = os.environ["MC_PY_MODULE_DIR"]
		return f"{EnvManager.app_root}/{moduleDir}"

	@classmethod
	@property
	def sql_script_dir(cls) -> str:
		moduleDir = os.environ["MC_SQL_SCRIPTS_DIR_CL"]
		return f"{EnvManager.app_root}/{moduleDir}"

	@classmethod
	@property
	def db_name(cls) -> str:
		return os.environ["MC_DATABASE_NAME"]

	@classmethod
	@property
	def test_flag(cls) -> bool:
		return os.environ.get("__TEST_FLAG__","false") == "true"

	@classmethod
	@property
	def secret_key(cls) -> str:
		return os.environ["MC_AUTH_SECRET_KEY"]

	@classmethod
	def get_configured_api_connection(
		cls,
		dbName: str,
		echo: bool=False
	) -> Connection:
		dbPass = EnvManager.db_pass_api
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		engine = create_engine(
			f"mysql+pymysql://{DbUsers.API_USER()}:{dbPass}@localhost/{dbName}",
			echo=echo,
		)
		conn = engine.connect()
		return conn

	@classmethod
	def get_configured_radio_connection(
		cls,
		dbName: str,
		echo: bool=False
	) -> Connection:
		dbPass = EnvManager.db_pass_radio
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		engine = create_engine(
			f"mysql+pymysql://{DbUsers.RADIO_USER()}:{dbPass}@localhost/{dbName}",
			echo=echo,
		)
		return engine.connect()


	@staticmethod
	def read_config_value(confLocation: str, key: str) -> str:
		passLines: list[str] = []
		with open(confLocation, "r") as configFile:
			for line in configFile:
				if f"<{key}>" in line or passLines:
					passLines.append(line)
				if f"</{key}>" in line:
					break
		segment = "".join(passLines)
		match = re.search(rf"<{key}>([^<]+)</{key}>", segment)
		if match:
			g = match.groups()
			return g[0]
		return ""