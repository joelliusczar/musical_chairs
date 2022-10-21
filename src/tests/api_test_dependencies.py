import json
import pytest
from typing import Any, Callable
from fastapi.testclient import TestClient
from .constant_fixtures_for_test import\
	primary_user,\
	clear_mock_password
from musical_chairs_libs.services import EnvManager
from .mocks.mock_db_constructors import\
	MockDbPopulator,\
	db_populator_noop,\
	construct_mock_connection_constructor
from sqlalchemy.engine import Connection
from fastapi.testclient import TestClient
from .common_fixtures import\
	fixture_db_populate_factory as fixture_db_populate_factory,\
	fixture_db_conn_in_mem as fixture_db_conn_in_mem
from .common_fixtures import *
from index import app


def mock_depend_primary_user():
	return primary_user()

def mock_depend_env_manager_factory(
	request: pytest.FixtureRequest
) -> Callable[[], EnvManager]:

	def mock_depend_env_manager() -> EnvManager:
		envMgr = EnvManager()
		envMgr.get_configured_db_connection = \
			construct_mock_connection_constructor(db_populator_noop)
		return envMgr
	return mock_depend_env_manager

def login_test_user(username: str, client: TestClient) -> dict[str, Any]:
	formData = {
		"username": username,
		"password": clear_mock_password()
	}
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	accessToken = data["access_token"]
	headers = {
		"Authorization": f"Bearer {accessToken}"
	}
	return headers

@pytest.fixture
def fixture_api_test_client(
	fixture_db_populate_factory: MockDbPopulator,
	fixture_db_conn_in_mem: Connection,
	request: pytest.FixtureRequest
) -> TestClient:
	# we need some sort of parent reference to the in mem db
	# so that the db does not get removed at the end of a request
	fixture_db_populate_factory(fixture_db_conn_in_mem, request)
	mock_depend_env_manager = mock_depend_env_manager_factory(request)
	app.dependency_overrides[EnvManager] = mock_depend_env_manager

	client = TestClient(app, raise_server_exceptions=False)
	return client