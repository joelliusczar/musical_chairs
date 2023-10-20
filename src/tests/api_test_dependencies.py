import json
import pytest
from typing import Any
from fastapi.testclient import TestClient
from .mocks.constant_values_defs import (
	primary_user,
	clear_mock_password
)
from sqlalchemy.engine import Connection
from fastapi.testclient import TestClient
from .common_fixtures import (
	fixture_db_conn_in_mem as fixture_db_conn_in_mem
)
from .common_fixtures import *
from index import app
from api_dependencies import (
	get_configured_db_connection,
	file_service
)
from .mocks.mock_file_service import MockFileService


def mock_depend_primary_user():
	return primary_user()


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
	fixture_db_conn_in_mem: Connection,
	request: pytest.FixtureRequest
) -> TestClient:

	app.dependency_overrides[get_configured_db_connection] =\
		lambda: fixture_db_conn_in_mem
	app.dependency_overrides[file_service] = lambda: MockFileService()

	client = TestClient(app, raise_server_exceptions=False)
	return client