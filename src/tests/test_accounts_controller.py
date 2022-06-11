import json
from musical_chairs_libs.env_manager import EnvManager
from .api_test_dependencies import mock_depend_env_manager
from .constant_fixtures_for_test import mock_password, mock_bad_password
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
	assert data["detail"][0]["field"] == "username"
	assert data["detail"][0]["msg"] == "testUser_bravo is already used."

	testUser["username"] = usedName.upper()
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "username"
	assert data["detail"][0]["msg"] == "TESTUSER_BRAVO is already used."

	testUser["username"] = "tëstUser_bravo"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "username"
	assert data["detail"][0]["msg"] == "tëstUser_bravo is already used."

def test_create_account_fail_password():
	testUser = {
		"username": "testUser",
		"email": "testPerson@gmail.com",
		"password": "hello",
		"displayName": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "password"
	assert data["detail"][0]["msg"] == \
		"Password does not meet the length requirement\n"\
		"Mininum Length 6. your password length: 5"

def test_create_account_fail_email():
	testUser = {
		"username": "testUser",
		"email": "testPerson",
		"password": "hello12",
		"displayName": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "email"
	assert data["detail"][0]["msg"] == \
		"The email address is not valid. It must have exactly one @-sign."

	testUser["email"] = "testPerson@fucky"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "email"
	assert data["detail"][0]["msg"] == \
		"The domain name fucky is not valid. It should have a period."

	testUser["email"] = "test4@test.com"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "email"
	assert data["detail"][0]["msg"] == \
		"test4@test.com is already used."

def test_login_fail():
	formData = {
		"username": "testUser_charlie",
		"password": mock_bad_password()
	}
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 401
	assert data["detail"][0]["msg"] == \
		"Incorrect username or password"

	formData["username"] = "noperson"
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 401
	assert data["detail"][0]["msg"] == \
		"Incorrect username or password"

	formData = {}
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "username"
	assert data["detail"][0]["msg"] == "field required"
	assert data["detail"][1]["field"] == "password"
	assert data["detail"][1]["msg"] == "field required"

	formData = { "username": "testUser_charlie" }
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "password"
	assert data["detail"][0]["msg"] == "field required"

	formData = { "password": mock_password() }
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "username"
	assert data["detail"][0]["msg"] == "field required"
