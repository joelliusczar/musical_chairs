from typing import Any
from .env_manager import EnvManager
from .template_service import TemplateService
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	is_name_safe,
	DbUsers,
	SqlScripts
)

"""
This class will mostly exist for the sake of unit tests
"""
class DbRootConnectionService:

	def __init__(self) -> None:
		self.conn = self.conn = self.get_root_connection()

	def get_root_connection(self) -> Connection:
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		engineAsRoot = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		return engineAsRoot.connect()

	def __enter__(self) -> "DbRootConnectionService":
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		if self.conn:
			self.conn.close()

	def create_db(self, dbName: str):
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		self.conn.exec_driver_sql(f"CREATE DATABASE {dbName}")

	def create_db_user(self, username: str, userPass: str):

		if not is_name_safe(username):
			raise RuntimeError("Invalid username was used")
		self.conn.exec_driver_sql(
			f"CREATE USER IF NOT EXISTS {username} "
			f"IDENTIFIED BY %(userPass)s",
			{ "userPass": userPass}
		)

	def create_app_users(self):
		dbPass = EnvManager.db_pass_api
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(DbUsers.API_USER.value, dbPass)

		dbPass = EnvManager.db_pass_radio
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(DbUsers.RADIO_USER.value, dbPass)

	def create_owner(self, dbName: str):
		dbPass = EnvManager.db_pass_owner
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(DbUsers.OWNER_USER.value, dbPass)
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		self.conn.exec_driver_sql(
			f"GRANT ALL PRIVILEGES ON {dbName}.* to "
			f"'{DbUsers.OWNER_USER.value}'@'localhost' WITH GRANT OPTION"
		)

class DbOwnerConnectionService:

	def __init__(self, dbName: str) -> None:
		self.dbName = dbName
		self.conn = self.conn = self.get_root_connection()

	def get_root_connection(self) -> Connection:
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		owner = DbUsers.OWNER_USER.value
		engine = create_engine(f"mysql+pymysql://{owner}:{dbPass}@localhost")
		return engine.connect()

	def __enter__(self) -> "DbOwnerConnectionService":
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.conn.close()

	def grant_api_roles(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_API)
		if not is_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<apiUser>", DbUsers.API_USER.value)
		self.conn.exec_driver_sql(script)

	def grant_radio_roles(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_RADIO)
		if not is_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<apiUser>", DbUsers.RADIO_USER.value)
		self.conn.exec_driver_sql(script)

	def revoke_all_roles(self):
		self.conn.exec_driver_sql(
			f"REVOKE ALL PRIVILEGES, GRANT OPTION "
			f"FROM {DbUsers.API_USER.value}, {DbUsers.RADIO_USER.value}"
		)
