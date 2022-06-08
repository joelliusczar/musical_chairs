import json
import pytest
from musical_chairs_libs.env_manager import EnvManager
from .api_test_dependencies import mock_depend_env_manager
from fastapi.testclient import TestClient
from api.index import app

app.dependency_overrides[EnvManager] = mock_depend_env_manager

client = TestClient(app)

def test_create_account_success():
	testUser = {
		"username": "testUser",
		"email": "testPerson@gmail.com",
		"password": "hello12",
		"displayName": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == 6
	usedName = "testUser_bravo"
	testUser["username"] = usedName

@pytest.mark.xfail
def test_create_account_fail_username():
	usedName = "testUser_bravo"
	testUser = {
		"username": usedName,
		"email": "testPerson@gmail.com",
		"password": "hello12",
		"displayName": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"] == "Username testUser_bravo is already used."

	testUser["username"] = usedName.upper()
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"] == "Username TESTUSER_BRAVO is already used."

	testUser["username"] = "tëstUser_bravo"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"] == "Username TESTUSER_BRAVO is already used."
