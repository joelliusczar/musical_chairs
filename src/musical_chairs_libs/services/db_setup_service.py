import hashlib
from typing import Any
from .env_manager import EnvManager
from .template_service import TemplateService
from sqlalchemy import create_engine, NullPool
from sqlalchemy.engine import Connection
from musical_chairs_libs.dtos_and_utilities import (
	is_name_safe
)
from musical_chairs_libs import SqlScripts
from musical_chairs_libs.dtos_and_utilities.constants import DbUsers
from musical_chairs_libs.tables import metadata, get_ddl_scripts
#https://github.com/PyMySQL/PyMySQL/issues/590
from pymysql.constants import CLIENT
from pathlib import Path

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
		dbPass = EnvManager.db_setup_pass()
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
		dbPass = EnvManager.db_pass_api()
		if not dbPass:
			raise RuntimeError("API: The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.API_USER.value,
			"localhost",
			dbPass
		)

		dbPass = EnvManager.db_pass_radio()
		if not dbPass:
			raise RuntimeError("Radio:The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.RADIO_USER.value,
			"localhost",
			dbPass
		)

		dbPass = EnvManager.db_pass_janitor()
		if not dbPass:
			raise RuntimeError("Janitor: The system is not configured correctly for that.")
		self.create_db_user(
			DbUsers.JANITOR_USER.value,
			"localhost",
			dbPass
		)

	def create_owner(self):
		dbPass = EnvManager.db_pass_owner()
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
		# self.revoke_all_roles(dbName, force)
		self.conn.exec_driver_sql(f"DROP DATABASE IF EXISTS {dbName}")

	def revoke_all_roles(self, dbName: str, force: bool=False):
		if not dbName.startswith("test_") and not force:
			raise RuntimeError("only test databases can be removed")
		if not is_db_name_safe(dbName):
			raise RuntimeError("Invalid name was used:")
		self.conn.exec_driver_sql(
			f"REVOKE IF EXISTS ALL PRIVILEGES ON `{dbName}`.* "
			f"FROM {DbUsers.API_USER.format_user()}"
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
		dbPass = EnvManager.db_pass_owner()
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

	def grant_api_roles(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_API)
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<apiUser>", DbUsers.API_USER("localhost"))
		self.conn.exec_driver_sql(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def grant_radio_roles(self):
		template = TemplateService.load_sql_script_content(SqlScripts.GRANT_RADIO)
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<radioUser>", DbUsers.RADIO_USER("localhost"))
		self.conn.exec_driver_sql(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def grant_janitor_roles(self):
		template = TemplateService.load_sql_script_content(
			SqlScripts.GRANT_JANITOR
		)
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)\
			.replace("<janitorUser>", DbUsers.JANITOR_USER("localhost"))
		self.conn.exec_driver_sql(script)
		self.conn.exec_driver_sql("FLUSH PRIVILEGES")

	def create_tables(self):
		metadata.create_all(self.conn.engine)

	def add_path_permission_index(self):
		template = TemplateService.load_sql_script_content(
			SqlScripts.PATH_USER_INDEXES
		)
		if not is_db_name_safe(self.dbName):
			raise RuntimeError("Invalid name was used")
		script = template.replace("<dbName>", self.dbName)
		self.conn.exec_driver_sql(script)

	def add_next_directory_level_func(self):
		script = TemplateService.load_sql_script_content(
			SqlScripts.NEXT_DIRECTORY_LEVEL
		).replace("<apiUser>", DbUsers.API_USER("localhost"))
		self.conn.exec_driver_sql(script)

	def add_normalize_opening_slash(self):
		script = TemplateService.load_sql_script_content(
			SqlScripts.NORMALIZE_OPENING_SLASH
		).replace("<apiUser>", DbUsers.API_USER("localhost"))
		self.conn.exec_driver_sql(script)

	def run_defined_script(self, scriptId: SqlScripts):
		script = TemplateService.load_sql_script_content(
			scriptId
		).replace("<dbName>", self.dbName)\
		.replace("|","")\
		.replace("DELIMITER","")

		self.conn.exec_driver_sql(script)

def setup_database(dbName: str):
	with DbRootConnectionService() as rootConnService:
		rootConnService.create_db(dbName)
		rootConnService.create_owner()
		rootConnService.create_app_users()
		rootConnService.grant_owner_roles(dbName)

	with DbOwnerConnectionService(dbName, echo=False) as ownerConnService:
		ownerConnService.create_tables()
		ownerConnService.add_path_permission_index()
		ownerConnService.grant_api_roles()
		ownerConnService.grant_radio_roles()
		ownerConnService.grant_janitor_roles()
		ownerConnService.add_next_directory_level_func()
		ownerConnService.add_normalize_opening_slash()
		
		ownerConnService.run_defined_script(SqlScripts.DROP_REQUESTED_TIMESTAMP)
		ownerConnService.run_defined_script(SqlScripts.ADD_INTERNAL_PATH)
		ownerConnService.run_defined_script(SqlScripts.DROP_PLACEHOLDERDIR)
		ownerConnService.run_defined_script(SqlScripts.ADD_SONG_FILE_HASH)
		ownerConnService.run_defined_script(SqlScripts.ADD_IP4ADDRESS)
		ownerConnService.run_defined_script(SqlScripts.ADD_IP6ADDRESS)
		ownerConnService.run_defined_script(SqlScripts.ADD_USERAGENT_FK)
		ownerConnService.run_defined_script(SqlScripts.ADD_SONG_DELETEDTIMESTAMP)
		ownerConnService.run_defined_script(SqlScripts.ADD_ALBUM_VERSION)
		ownerConnService.run_defined_script(SqlScripts.ADD_STATION_TYPE)
		ownerConnService.run_defined_script(SqlScripts.ADD_SONG_DELETEDBYUSERID)
		ownerConnService.run_defined_script(SqlScripts.ADD_SONG_TRACKNUM)
		ownerConnService.run_defined_script(SqlScripts.ADD_PLAYLIST_VIEWSECURITY)
		ownerConnService.run_defined_script(SqlScripts.ADD_SONGSPLAYLISTS_ORDER)
		try:
			#there doesn't seem to be a good if table exists, rename
			#syntax, so we're just going to smother the error
			ownerConnService.run_defined_script(SqlScripts.RENAME_PLAYLIST_SONG_TABLE)
		except:
			pass

		Path(f"/tmp/{get_schema_hash()}").touch()