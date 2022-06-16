import json
from datetime import datetime
from typing import Any, List
from fastapi import Depends
from fastapi.testclient import TestClient
from .constant_fixtures_for_test import\
	mock_ordered_date_list,\
	mock_password,\
	primary_user,\
	clear_mock_password
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.env_manager import EnvManager
from .mocks.mock_db_constructors import construct_mock_connection_constructor


def mock_depend_primary_user():
	return primary_user()

def mock_depend_env_manager(
	orderedDateList: List[datetime] = Depends(mock_ordered_date_list),
	primaryUser: AccountInfo = Depends(mock_depend_primary_user),
	mockPassword: bytes = Depends(mock_password)
) -> EnvManager:
	envMgr = EnvManager()
	envMgr.get_configured_db_connection = \
		construct_mock_connection_constructor(
			orderedDateList,
			primaryUser,
			mockPassword
		)
	return envMgr

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