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
from musical_chairs_libs.tables import metadata
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT

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
		self.conn.exec_driver_sql(f"CREATE DATABASE IF NOT EXISTS {dbName}")

	def create_db_user(self, username: str, host: str, userPass: str):
		if not is_name_safe(username):
			raise RuntimeError("Invalid username was used")
		if not is_name_safe(host):
			raise RuntimeError("Invalid host was used")
		self.conn.exec_driver_sql(
			f"CREATE USER IF NOT EXISTS '{username}'@'{host}' "
			f"IDENTIFIED BY %(userPass)s",
			{ "userPass": userPass}
		)

	def create_app_users(self):
		dbPass = EnvManager.db_pass_api
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.API_USER.value,
			"localhost",
			dbPass
		)

		dbPass = EnvManager.db_pass_radio
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.RADIO_USER.value,
			"localhost",
			dbPass
		)

	def create_owner(self):
		dbPass = EnvManager.db_pass_owner
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.OWNER_USER.value,
			"localhost",
			dbPass
		)

	def grant_owner_roles(self, dbName: str):
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		user = DbUsers.OWNER_USER(host="localhost")
		self.conn.exec_driver_sql(
			f"GRANT ALL PRIVILEGES ON {dbName}.* to "
			f"{user} WITH GRANT OPTION"
		)
		self.conn.exec_driver_sql(
			f"GRANT RELOAD ON *.* to "
			f"{user}"
		)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	#this method can only be used on test databases
	def drop_database(self, dbName: str):
		if not dbName.startswith("test_"):
			raise RuntimeError("only test databases can be removed")
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		self.conn.exec_driver_sql(f"DROP DATABASE IF EXISTS {dbName}")

	def revoke_all_roles(self):
		self.conn.exec_driver_sql(
			f"REVOKE ALL PRIVILEGES, GRANT OPTION "
			f"FROM {DbUsers.API_USER.format_user()}, "
			f"{DbUsers.RADIO_USER.format_user()}, "
			f"{DbUsers.OWNER_USER.format_user()}"
		)

	def drop_user(self, user: DbUsers):
		self.conn.exec_driver_sql(f"DROP USER IF EXISTS {user.format_user()}")

	def drop_all_users(self):
		for user in DbUsers:
			self.drop_user(user)

class DbOwnerConnectionService:

	def __init__(self, dbName: str, echo: bool=False) -> None:
		self.dbName = dbName
		self.echo = echo
		self.conn = self.get_owner_connection()

	def get_owner_connection(self) -> Connection:
		dbPass = EnvManager.db_pass_owner
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		if not is_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		owner = DbUsers.OWNER_USER.value
		engine = create_engine(
			f"mysql+pymysql://{owner}:{dbPass}@localhost/{self.dbName}",
			echo=self.echo,
			connect_args={
				"client_flag": CLIENT.MULTI_STATEMENTS
			}
		)
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
			.replace("<apiUser>", DbUsers.API_USER("localhost"))
		self.conn.exec_driver_sql(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def grant_radio_roles(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_RADIO)
		if not is_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<radioUser>", DbUsers.RADIO_USER("localhost"))
		cursor = self.conn.engine.raw_connection().cursor()
		cursor.execute(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def create_tables(self):
		metadata.create_all(self.conn.engine)

	def add_path_permission_index(self):
		template = TemplateService.load_sql_script_content(
			SqlScripts.PATH_USER_INDEXES
		)
		if not is_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)
		cursor = self.conn.engine.raw_connection().cursor()
		cursor.execute(script)