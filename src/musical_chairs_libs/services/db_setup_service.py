from .env_manager import EnvManager
from sqlalchemy import create_engine
from musical_chairs_libs.dtos_and_utilities import (
	check_name_safety
)

class DbSetupService:

	@staticmethod
	def create_db(dbName: str):
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		m = check_name_safety(dbName)
		if m:
			raise RuntimeError("Invalid name was used")
		engineAsRoot = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		with engineAsRoot.connect() as conn:
			conn.exec_driver_sql(f"CREATE DATABASE {dbName}")

	@staticmethod
	def create_api_user(userPass: str):
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		engineAsRoot = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		with engineAsRoot.connect() as conn:
			conn.exec_driver_sql("")