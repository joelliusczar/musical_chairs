import pytest
from musical_chairs_libs.config_loader import ConfigLoader
from sqlalchemy.engine import Connection

@pytest.fixture
def db_conn() -> Connection:
	configLoader = ConfigLoader()
	conn = configLoader.get_configured_db_connection()
	return conn
