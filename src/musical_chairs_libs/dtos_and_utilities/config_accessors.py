import json
import logging as builtin_logging
import os
import re
from uuid import UUID
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.event import listens_for
from musical_chairs_libs.dtos_and_utilities.constants import DbUsers
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT
from pathlib import Path

collation_connection = "utf8mb4_general_ci"

def __on_connect__(**kw: dict[str, Any]): 
	dbapi_connection = kw["dbapi_connection"]
	#somewhere between mariahdb 11.8.3 and 10.6.22, the default collation_connection
	#became utf8mb4_uca1400_ai_ci which causes problems with next_directory_level.
	#Supposedly, you should be able to add connect_args={'init_command': "SET @@collation_connection='utf8mb4_unicode_ci'"}
	#to the engine constructor, but apparently there is another bug described here
	#https://github.com/sqlalchemy/sqlalchemy/discussions/7858 
	#that seems to indicate that collation_connection is being overwritten
	dbapi_connection.query(f"SET @@collation_connection='{collation_connection}'") #pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue]

class ConfigAcessors:

	@classmethod
	def app_root(cls) -> str:
		if ConfigAcessors.test_flag():
			return os.environ["DSF_TEST_ROOT"]
		return os.environ["DSF_APP_ROOT"]

	@classmethod
	def absolute_content_home(cls) -> str:
		contentHome = os.environ["DSF_CONTENT_DIR"]
		return contentHome

	@classmethod
	def db_setup_pass(cls) -> str:
		return os.environ.get("DSF_DB_PASS_SETUP", "")

	@classmethod
	def db_pass_api(cls) -> str:
		return os.environ.get("DSF_DB_PASS_API", "")

	@classmethod
	def db_pass_radio(cls) -> str:
		return os.environ.get("DSF_DB_PASS_RADIO", "")

	@classmethod
	def db_pass_janitor(cls) -> str:
		return os.environ.get("DSF_DB_PASS_JANITOR", "")

	@classmethod
	def db_pass_owner(cls) -> str:
		return os.environ.get("DSF_DB_PASS_OWNER", "")

	@classmethod
	def namespace_uuid(cls) -> UUID:
		return UUID(os.environ.get("DSF_NAMESPACE_UUID", ""))

	@classmethod
	def templates_dir(cls) -> str:
		templateDir = os.environ["DSF_TEMPLATES_DEST"]
		return templateDir

	@classmethod
	def station_config_dir(cls) -> str:
		configDir = os.environ["DSF_ICES_CONFIGS_DIR"]
		return configDir

	@classmethod
	def station_module_dir(cls) -> str:
		moduleDir = os.environ["DSF_PY_MODULE_DIR"]
		return moduleDir

	@classmethod
	def sql_script_dir(cls) -> str:
		moduleDir = os.environ["DSF_SQL_SCRIPTS_DEST"]
		return moduleDir

	@classmethod
	def db_name(cls) -> str:
		return os.environ["DSF_DATABASE_NAME"]

	@classmethod
	def s3_bucket_name(cls) -> str:
		return os.environ["S3_BUCKET_NAME"]

	@classmethod
	def s3_region_name(cls) -> str:
		return os.environ["S3_REGION_NAME"]

	@classmethod
	def s3_endpoint(cls) -> str:
		return os.environ["AWS_ENDPOINT_URL"]

	@classmethod
	def test_flag(cls) -> bool:
		return os.environ.get("__TEST_FLAG__","false") == "true"

	@classmethod
	def auth_key(cls) -> str:
		return os.environ["DSF_AUTH_SECRET_KEY"]
	
	@classmethod
	def back_key(cls) -> str:
		return os.environ["DSF_BACK_KEY"]
	
	@classmethod
	def dev_app_user_name(cls) -> str:
		return os.environ["DSF_DEV_APP_USER_NAME"]

	@classmethod
	def dev_app_user_pw(cls) -> str:
		return os.environ["DSF_DEV_APP_USER_PW"]

	@classmethod
	def api_log_level(cls) -> str:
		try:
			return cls.live_config()["logLevels"]["api"] or \
				builtin_logging.getLevelName(builtin_logging.WARNING)
		except:
			return builtin_logging.getLevelName(builtin_logging.WARNING)

	@classmethod
	def radio_log_level(cls) -> str:
		try:
			return cls.live_config()["logLevels"]["radio"] or \
				builtin_logging.getLevelName(builtin_logging.WARNING)
		except:
			return builtin_logging.getLevelName(builtin_logging.WARNING)
	
	@classmethod
	def python_executable(cls) -> str:
		return os.environ["DSF_PYTHON_EXECUTABLE"]
	
	@classmethod
	def live_config(cls) -> dict[str, Any]:
		try:
			config_path = os.environ["DSF_LIVE_CONFIG_PATH"]
			contents = Path(config_path).read_text()
			return json.loads(contents)
		except:
			return {}


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
