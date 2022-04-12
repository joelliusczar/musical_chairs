import pytest
from musical_chairs_libs.config_loader import ConfigLoader
from musical_chairs_libs.wrapped_db_connection import WrappedDbConnection

@pytest.fixture
def db_conn() -> WrappedDbConnection:
	configLoader = ConfigLoader()
	conn = configLoader.get_configured_db_connection()
	return conn
