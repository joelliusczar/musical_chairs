from alembic import command
from alembic.config import Config

from typing import Any
from sqlalchemy import create_engine, NullPool
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	is_name_safe
)
from musical_chairs_libs.dtos_and_utilities.constants import DbUsers
from musical_chairs_libs.tables import metadata
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT


def is_db_name_safe(dbName: str) -> bool:
	return is_name_safe(dbName, maxLen=100)


"""
This class will mostly exist for the sake of unit tests
"""
class DbRootConnectionService:

	def __init__(self) -> None:
		self.conn = self.conn = self.get_root_connection()

	def get_root_connection(self) -> Connection:
		dbPass = ConfigAcessors.db_setup_pass()
		if not dbPass:
			raise RuntimeError("Root: The system is not configured correctly for that.")
		engineAsRoot = create_engine(
			f"mysql+pymysql://root:{dbPass}@localhost",
			#not fully sure why this was needed, but mariadb/sqlalchemy/somebody
			#was holding onto connections and this was fucking up unit tests
			poolclass=NullPool
		)
		return engineAsRoot.connect()

	def __enter__(self) -> "DbRootConnectionService":
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.conn.close()

	def create_db(self, dbName: str):
		if not is_db_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		#once the server is using a new db version, 
		#we will want to update the COLLATE value
		self.conn.exec_driver_sql(
			f"CREATE DATABASE IF NOT EXISTS {dbName} "\
			"COLLATE = utf8mb4_uca1400_ai_ci" 
		)

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
		dbPass = ConfigAcessors.db_pass_api()
		if not dbPass:
			raise RuntimeError("API: The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.API_USER.value,
			"localhost",
			dbPass
		)

		dbPass = ConfigAcessors.db_pass_radio()
		if not dbPass:
			raise RuntimeError("Radio:The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.RADIO_USER.value,
			"localhost",
			dbPass
		)

		dbPass = ConfigAcessors.db_pass_janitor()
		if not dbPass:
			raise RuntimeError("Janitor: The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.JANITOR_USER.value,
			"localhost",
			dbPass
		)

	def create_owner(self):
		dbPass = ConfigAcessors.db_pass_owner()
		if not dbPass:
			raise RuntimeError("OWNER: The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.OWNER_USER.value,
			"localhost",
			dbPass
		)

	def grant_owner_roles(self, dbName: str):
		if not is_db_name_safe(dbName):
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
	def drop_database(self, dbName: str, force: bool=False):
		if not dbName.startswith("test_") and not force:
			raise RuntimeError("only test databases can be removed")
		if not is_db_name_safe(dbName):
			raise RuntimeError("Invalid name was used:")
		self.conn.exec_driver_sql(f"DROP DATABASE IF EXISTS {dbName}")


class DbOwnerConnectionService:

	def __init__(self, dbName: str, echo: bool=False) -> None:
		self.dbName = dbName
		self.echo = echo
		self.conn = self.get_owner_connection()

	def get_owner_connection(self) -> Connection:
		dbPass = ConfigAcessors.db_pass_owner()
		if not dbPass:
			raise RuntimeError("Owner: The system is not configured correctly for that.")
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		owner = DbUsers.OWNER_USER.value
		engine = create_engine(
			f"mysql+pymysql://{owner}:{dbPass}@localhost/{self.dbName}",
			echo=self.echo,
			connect_args={
				"client_flag": CLIENT.MULTI_STATEMENTS | CLIENT.MULTI_RESULTS
			},
			poolclass=NullPool
		)
		return engine.connect()

	def __enter__(self) -> "DbOwnerConnectionService":
		return self

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.conn.close()


	def flush_privileges(self):
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def create_tables(self):
		metadata.create_all(self.conn.engine)

def setup_database(dbName: str):
	with DbRootConnectionService() as rootConnService:
		rootConnService.create_db(dbName)
		rootConnService.create_owner()
		rootConnService.create_app_users()
		rootConnService.grant_owner_roles(dbName)

	with DbOwnerConnectionService(dbName, echo=False) as ownerConnService:
		
		ownerConnService.create_tables()

		config = Config(ConfigAcessors.alembic_ini())
		config.set_main_option("script_location", "../../alembic")
		config.attributes["connection"] = ownerConnService
		config.attributes["target_metadata"] = metadata
		# context.configure(
		# 	connection=ownerConnService.get_owner_connection(),
		# 	target_metadata=metadata
		# )


			# with context.begin_transaction():
		command.upgrade(config, "b7d204ce6e41", tag="test")
		# ownerConnService.flush_privileges()
