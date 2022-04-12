import pytest
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection

@pytest.fixture
def db_conn() -> WrappedDbConnection:
	envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
	return conn
