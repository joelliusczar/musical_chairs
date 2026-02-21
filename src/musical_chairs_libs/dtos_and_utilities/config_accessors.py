import json
import logging as builtin_logging
import os
import re
from contextlib import contextmanager
from uuid import UUID
from typing import Any
from pathlib import Path



class ConfigAcessors:

	config_overrides: dict[str, Any] = {}

	@classmethod
	def get_value(cls, envKey: str, overrideKey: str | None = None) -> Any:
		if overrideKey is not None and overrideKey in cls.config_overrides:
			return cls.config_overrides[overrideKey]
		return os.environ[envKey]


	@classmethod
	def app_root(cls) -> str:
		if ConfigAcessors.__test_flag__():
			return os.environ["DSF_TEST_ROOT"]
		return os.environ["DSF_APP_ROOT"]


	@classmethod
	def absolute_content_home(cls) -> str:
		return cls.get_value("DSF_CONTENT_DIR", "absolute_content_home")


	@classmethod
	def db_setup_pass(cls) -> str:
		return cls.get_value("DSF_DB_PASS_SETUP","db_setup_pass")


	@classmethod
	def db_pass_api(cls) -> str:
		return cls.get_value("DSF_DB_PASS_API","db_pass_api")


	@classmethod
	def db_pass_radio(cls) -> str:
		return cls.get_value("DSF_DB_PASS_RADIO","db_pass_radio")


	@classmethod
	def db_pass_janitor(cls) -> str:
		return cls.get_value("DSF_DB_PASS_JANITOR","db_pass_janitor")


	@classmethod
	def db_pass_owner(cls) -> str:
		return cls.get_value("DSF_DB_PASS_OWNER","db_pass_owner")


	@classmethod
	def namespace_uuid(cls) -> UUID:
		return UUID(cls.get_value("DSF_NAMESPACE_UUID", "namespace_uuid"))


	@classmethod
	def templates_dir(cls) -> str:
		return cls.get_value("DSF_TEMPLATES_DEST", "templates_dir")


	@classmethod
	def station_config_dir(cls) -> str:
		return cls.get_value("DSF_ICES_CONFIGS_DIR", "station_config_dir")


	@classmethod
	def station_module_dir(cls) -> str:
		return cls.get_value("DSF_PY_MODULE_DIR", "station_module_dir")


	@classmethod
	def db_name(cls) -> str:
		return cls.get_value("DSF_DATABASE_NAME", "db_name")

	@classmethod
	def s3_bucket_name(cls) -> str:
		return cls.get_value("S3_BUCKET_NAME", "s3_bucket_name")

	@classmethod
	def s3_region_name(cls) -> str:
		return cls.get_value("S3_REGION_NAME", "s3_region_name")

	@classmethod
	def s3_endpoint(cls) -> str:
		return cls.get_value("AWS_ENDPOINT_URL", "s3_endpoint")

	@classmethod
	def __test_flag__(cls) -> bool:
		return os.environ.get("__TEST_FLAG__","false") == "true"

	@classmethod
	def auth_key(cls) -> str:
		return cls.get_value("DSF_AUTH_SECRET_KEY", "auth_key")
	
	@classmethod
	def back_key(cls) -> str:
		return cls.get_value("DSF_BACK_KEY", "back_key")
	
	@classmethod
	def dev_app_user_name(cls) -> str:
		return cls.get_value("DSF_DEV_APP_USER_NAME", "dev_app_user_name")

	@classmethod
	def dev_app_user_pw(cls) -> str:
		return cls.get_value("DSF_DEV_APP_USER_PW", "dev_app_user_pw")


	@classmethod
	def event_log_dir(cls) -> str:
		return cls.get_value("DSF_EVENT_LOGS_DIR", "event_log_dir")


	@classmethod
	def visit_log_dir(cls) -> str:
		return cls.get_value("DSF_VISIT_LOGS_DIR", "visit_log_dir")
	

	@classmethod
	def station_queue_files_dir(cls) -> str:
		return cls.get_value("DSF_QUEUE_FILES_DIR", "station_queue_files_dir")
	
	@classmethod
	def shuffled_alphabet(cls) -> str:
		return cls.get_value("DSF_SHUFFLED_ALPHABET", "shuffled_alphabet")
	

	@classmethod
	def station_history_files_dir(cls) -> str:
		return cls.get_value(
			"DSF_STATION_HISTORY_FILES_DIR",
			"station_history_files_dir")
	

	@classmethod
	def alembic_ini(cls) -> str:
		return cls.get_value("DSF_ALEMBIC_INI", "alembic_ini")


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
	def api_log_handler(cls) -> str:
		try:
			return cls.live_config()["logHandlers"]["api"] or \
				"json"
		except:
			return "json"


	@classmethod
	def radio_log_handler(cls) -> str:
		try:
			return cls.live_config()["logHandlers"]["radio"] or \
				"json"
		except:
			return "json"


	@classmethod
	def python_executable(cls) -> str:
		return os.environ["DSF_PYTHON_EXECUTABLE"]


	@classmethod
	def ices_executable(cls) -> str:
		return str(Path(os.environ["DSF_ICES_EXECUTABLE"]).expanduser())


	@classmethod
	def live_config(cls) -> dict[str, Any]:
		try:
			config_path = os.environ["DSF_LIVE_CONFIG_PATH"]
			contents = Path(config_path).read_text()
			return json.loads(contents)
		except:
			return {}


	@classmethod
	@contextmanager
	def override_configs(cls, overrides: dict[str, Any]):
		if overrides:
			cls.config_overrides = overrides
		yield
		cls.config_overrides = {}


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