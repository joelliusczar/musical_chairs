import json
import pytest
from datetime import datetime
from typing import Any, List
from fastapi import Depends
from fastapi.testclient import TestClient
from .constant_fixtures_for_test import\
	mock_ordered_date_list,\
	mock_password,\
	primary_user,\
	clear_mock_password
from musical_chairs_libs.dtos_and_utilities import AccountInfo
from musical_chairs_libs.env_manager import EnvManager
from .mocks.mock_db_constructors import construct_mock_connection_constructor
from sqlalchemy.engine import Connection
from fastapi.testclient import TestClient
from .common_fixtures import\
	fixture_db_populate_factory as fixture_db_populate_factory,\
	fixture_db_conn_in_mem as fixture_db_conn_in_mem
from .common_fixtures import *
from index import app


def mock_depend_primary_user():
	return primary_user()

def mock_depend_db_populate_factory(
	orderedDateList: List[datetime] = Depends(mock_ordered_date_list),
	primaryUser: AccountInfo = Depends(mock_depend_primary_user),
	mockPassword: bytes = Depends(mock_password)
) -> Callable[[Connection], None]:
	def _setup_tables(conn: Connection):
		setup_in_mem_tbls(
			conn,
			orderedDateList,
			primaryUser,
			mockPassword
		)
	return _setup_tables

def mock_depend_env_manager() -> EnvManager:
	envMgr = EnvManager()
	envMgr.get_configured_db_connection = \
		construct_mock_connection_constructor(lambda c: None)
	return envMgr

class ParentDbConnectionRef():

	def __init__(self, conn: Connection):
		self._conn = conn

	def __call__(
		self,
		envManager: EnvManager = Depends(mock_depend_env_manager)
	) -> Iterator[Connection]:
		if not envManager:
				envManager = EnvManager()
		conn = envManager.get_configured_db_connection(checkSameThread=False)
		try:
			yield conn
		finally:
			conn.close()

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
	fixture_db_populate_factory: Callable[[Connection], None],
	fixture_db_conn_in_mem: Connection
) -> TestClient:
	# we need some sort of parent reference to the in mem db
	# so that the db does not get removed at the end of a request
	fixture_db_populate_factory(fixture_db_conn_in_mem)
	app.dependency_overrides[EnvManager] = mock_depend_env_manager

	client = TestClient(app, raise_server_exceptions=False)
	return client