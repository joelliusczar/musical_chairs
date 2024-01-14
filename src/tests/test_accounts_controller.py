import json
from musical_chairs_libs.dtos_and_utilities import UserRoleDef
from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from .mocks.constant_values_defs import\
	clear_mock_password,\
	clear_mock_bad_password_clear,\
	primary_user
from .mocks.db_population import get_initial_users
from fastapi.testclient import TestClient


def test_create_account_success(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	testUser = {
		"username": "testUser",
		"email": "testPerson@gmail.com",
		"password": "hello12",
		"displayname": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 200
	initial_users = get_initial_users()
	assert data["id"] == len(initial_users) + 1

	headers = login_test_user(primary_user().username, client)
	response = client.get("/accounts/list", headers=headers)
	data = json.loads(response.content)
	assert response.status_code == 200


def test_create_account_fail_username(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	usedName = "testUser_bravo"
	testUser = {
		"username": usedName,
		"email": "testPerson@gmail.com",
		"password": "hello12",
		"displayname": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->username"
	assert data["detail"][0]["msg"] == "testUser_bravo is already used."

	testUser["username"] = usedName.upper()
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->username"
	assert data["detail"][0]["msg"] == "TESTUSER_BRAVO is already used."

	testUser["username"] = "tëstUser_bravo"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->username"
	assert data["detail"][0]["msg"] == "tëstUser_bravo is already used."

def test_create_account_fail_password(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	testUser = {
		"username": "testUser",
		"email": "testPerson@gmail.com",
		"password": "hello",
		"displayname": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->password"
	assert data["detail"][0]["msg"] == \
		"Password does not meet the length requirement\n"\
		"Mininum Length 6. your password length: 5"

def test_create_account_fail_email(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	testUser = {
		"username": "testUser",
		"email": "testPerson",
		"password": "hello12",
		"displayname": "Testeroni"
	}
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->email"
	assert data["detail"][0]["msg"] == \
		"The email address is not valid. It must have exactly one @-sign."

	testUser["email"] = "testPerson@fucky"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->email"
	assert data["detail"][0]["msg"] == \
		"The domain name fucky is not valid. It should have a period."

	testUser["email"] = "test4@test.com"
	response = client.post("/accounts/new", json=testUser)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->email"
	assert data["detail"][0]["msg"] == \
		"test4@test.com is already used."

def test_login_success(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	formData = {
		"username": "testUser_foxtrot",
		"password": clear_mock_password()
	}
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert len(data.keys()) == 9
	assert "access_token" in data
	assert "login_timestamp" in data
	assert data["token_type"] == "bearer"
	assert len(data["roles"]) == 3
	assert data["lifetime"] ==  1800
	assert data["email"] == "test6@test.com"


def test_login_fail(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	formData = {
		"username": "testUser_charlie",
		"password": clear_mock_bad_password_clear()
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
	assert data["detail"][0]["field"] == "body->username"
	assert data["detail"][0]["msg"] == "Field required"
	assert data["detail"][1]["field"] == "body->password"
	assert data["detail"][1]["msg"] == "Field required"

	formData = { "username": "testUser_charlie" }
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->password"
	assert data["detail"][0]["msg"] == "Field required"

	formData = { "password": clear_mock_password() }
	response = client.post("/accounts/open", data=formData)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["field"] == "body->username"
	assert data["detail"][0]["msg"] == "Field required"

def test_get_account_list(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	headers = login_test_user("testUser_golf", client)
	initialUsers = get_initial_users()

	response = client.get("/accounts/list", headers=headers)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["totalrows"] ==len(initialUsers)
	assert len(data["items"]) ==len(initialUsers)

	headers = login_test_user("testUser_hotel", client)

	response = client.get("/accounts/list", headers=headers)
	data = json.loads(response.content)
	assert response.status_code == 403
	assert data["detail"][0]["msg"] ==\
		"Insufficient permissions to perform that action"

def test_update_account(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	headers = login_test_user("testUser_golf", client)
	#update email success
	response = client.put(
		"/accounts/account/7",
		headers=headers,
		json={
			"username": "testUser_golf",
			"email": "test_golf@test.com",
		}
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["email"] == "test_golf@test.com"

	#try to update email without being logged in
	response = client.put(
		"/accounts/account/7",
		json={
			"username": "testUser_golf",
			"email": "test_golf@test.com",
		},
	)
	data = json.loads(response.content)
	assert response.status_code == 401
	assert data["detail"][0]["msg"] == "Not authenticated"

	#try to update email while logged in as wrong user
	headers = login_test_user("testUser_foxtrot", client)
	response = client.put(
		"/accounts/account/7",
		headers=headers,
		json={
			"username": "testUser_golf",
			"email": "test_golf@test.com",
		}
	)
	data = json.loads(response.content)
	assert response.status_code == 403
	assert data["detail"][0]["msg"] == \
		"Insufficient permissions to perform that action"

	#update email again success
	headers = login_test_user(primary_user().username, client)
	response = client.put(
		"/accounts/account/7",
		headers=headers,
		json={
			"username": "testUser_golf",
			"email": "test_golf_again@test.com",
			"displayname": "Golf-Test-User"
		}
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["email"] == "test_golf_again@test.com"
	assert data["displayname"] == "Golf-Test-User"

def test_change_roles(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	headers = login_test_user(primary_user().username, client)
	response = client.put(
		"/accounts/update-roles/7",
		headers=headers,
		json=[
			{
				"name": UserRoleDef.USER_LIST.value
			}
		]
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["roles"][0] == {
		"name": UserRoleDef.USER_LIST.value,
		"span": 0,
		"count": 0,
		"priority": 0,
		"domain": "site"
		}

def test_get_account_info(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	user = primary_user()
	headers = login_test_user(user.username, client)
	response = client.get(
		f"/accounts/account/{user.id}",
		headers=headers
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == user.id
	assert data["username"] == user.username
	assert data["displayname"] == None
	assert data["email"] == user.email

	response = client.get(
		f"/accounts/account/{user.username}",
		headers=headers
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == user.id
	assert data["username"] == user.username
	assert data["displayname"] == None
	assert data["email"] == user.email