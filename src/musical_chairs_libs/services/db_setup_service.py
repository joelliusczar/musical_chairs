from .env_manager import EnvManager
from sqlalchemy import create_engine

class DbSetupService:

	@staticmethod
	def create_db(dbName: str):
		dbPass = EnvManager.db_setup_pass
		if not dbPass:
			raise RuntimeError("The system is not configured correctly for that.")
		engine = create_engine(f"mysql+pymysql://root:{dbPass}@localhost")
		with engine.connect() as conn:
			conn.exec_driver_sql("CREATE DATABASE @dbName",{ "dbName": dbName })

