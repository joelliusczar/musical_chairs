import json
import logging as builtin_logging
import os
import re
from uuid import UUID
from typing import Any
from pathlib import Path



class ConfigAcessors:

	@classmethod
	def app_root(cls) -> str:
		if ConfigAcessors.__test_flag__():
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
	def db_file(cls) -> str:
		return os.environ["DSF_DB_FILE"]

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
	def __test_flag__(cls) -> bool:
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
	def event_log_dir(cls) -> str:
		return os.environ["DSF_EVENT_LOGS_DIR"]
	

	@classmethod
	def station_queue_files_dir(cls) -> str:
		return os.environ["DSF_QUEUE_FILES_DIR"]
	

	@classmethod
	def station_history_files_dir(cls) -> str:
		return os.environ["DSF_STATION_HISTORY_FILES_DIR"]


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
