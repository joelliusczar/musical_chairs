import hashlib
import re
from typing import Any
from .template_service import TemplateService
from sqlalchemy import create_engine, NullPool, text
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	DbConnectionProvider,
	is_name_safe
)
from musical_chairs_libs import SqlScripts
from musical_chairs_libs.dtos_and_utilities.constants import DbUsers
from musical_chairs_libs.tables import metadata, get_ddl_scripts
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT
from pathlib import Path
from contextlib import redirect_stderr

def is_db_name_safe(dbName: str) -> bool:
	return is_name_safe(dbName, maxLen=100)

def get_schema_hash() -> str:
	with DbRootConnectionService() as rootConnService:
		content = get_ddl_scripts(rootConnService.conn)
		for scriptEnum in sorted(SqlScripts, key=lambda e: e.value[0]):
			content += (scriptEnum.value[1] + "\n")

		hashStr = hashlib.sha256(content.encode("utf-8")).hexdigest()
		return hashStr

"""
This class will mostly exist for the sake of unit tests
"""
class DbRootConnectionService:

	def __init__(self) -> None:
		self.conn = self.conn = self.get_root_connection()

	def get_root_connection(self) -> Connection:
		return DbConnectionProvider.sqlite_connection(inMemory=True)

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
			"COLLATE = utf8mb4_general_ci" 
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

	def grant_radio_rolesx(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_RADIO)
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<radioUser>", DbUsers.RADIO_USER("localhost"))
		self.conn.exec_driver_sql(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def flush_privileges(self):
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def create_tables(self):
		metadata.create_all(self.conn.engine)

	def load_script_contents(self, scriptId: SqlScripts) -> str:
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		templateNoComments = re.sub(
			r"^[ \t]*--.*\n",
			"",
			TemplateService.load_sql_script_content(
				scriptId
			),
			flags=re.MULTILINE
		)
		return templateNoComments.replace("<dbName>", self.dbName)


def setup_database(dbName: str):

		if not dbName.startswith("test_"):
			Path(f"/tmp/{get_schema_hash()}").touch()


class SqliteDDLProcessor:

	def __init__(self, dbName: str, echo: bool=False) -> None:
		self.dbName = dbName
		self.echo = echo
		self.conn = DbConnectionProvider.sqlite_connection(echo=echo)


	def __enter__(self) -> "SqliteDDLProcessor":
		return self


	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.conn.close()

	def rename_column(self, tableName: str, oldColName: str, newColName: str):
		try:
			#there doesn't seem to be a good if table exists, rename
			#syntax, so we're just going to smother the error
			with redirect_stderr(None):
				self.conn.execute(text(
					f"ALTER {tableName} RENAME {oldColName} TO {newColName};"
				))
		except:
			pass

		

	def setup_database(self):

			Path(f"/tmp/{get_schema_hash()}").touch()