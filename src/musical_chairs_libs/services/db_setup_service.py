from .env_manager import EnvManager
from sqlalchemy import create_engine
from musical_chairs_libs.dtos_and_utilities import (
	is_name_safe
)

class DbSetupService:

	@staticmethod
	def create_db(dbName: str):
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		engineAsRoot = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		with engineAsRoot.connect() as conn:
			conn.exec_driver_sql(f"CREATE DATABASE {dbName}")

	@staticmethod
	def create_db_user(dbName: str, username: str, userPass: str):
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		if not is_name_safe(dbName):
			raise RuntimeError("Invalid name was used")
		if not is_name_safe(username):
			raise RuntimeError("Invalid username was used")
		engineAsRoot = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		with engineAsRoot.connect() as conn:
			conn.exec_driver_sql(f"use {dbName}")
			conn.exec_driver_sql(
				f"CREATE USER {username} IF NOT EXISTS "
				"IDENTIFIED BY PASSWORD(%(userPass)s)",
				{ "userPass": userPass}
			)