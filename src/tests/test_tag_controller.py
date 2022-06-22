import json
from .api_test_dependencies import login_test_user,\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from .mocks.db_population import get_starting_tags
from .mocks.special_strings_reference import chinese1
from fastapi.testclient import TestClient




def test_save_tag(fixture_api_test_client: TestClient):
	client = fixture_api_test_client
	headers = login_test_user("testUser_india", client)
	starting_tags_list = get_starting_tags()
	response = client.post(
		"/tags",
		headers=headers,
		params={ "tagName": "posted_tag" }
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["name"] == "posted_tag"
	assert data["id"] == len(starting_tags_list) + 1

	tagIds = [data["id"]]
	response = client.get("/tags", params={ "tagIds": tagIds})
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["totalRows"] == len(starting_tags_list) + 1
	assert len(data["items"]) == 1

	response = client.get("/tags")
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["totalRows"] == len(starting_tags_list) + 1
	assert len(data["items"]) == len(starting_tags_list) + 1

	response = client.post(
		"/tags",
		headers=headers,
		params={ "tagName": "oscar_tag" }
	)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["msg"] == "oscar_tag is already used."
	assert data["detail"][0]["field"] == "tagName"

	response = client.post(
		"/tags",
		headers=headers,
		params={ "tagName": chinese1 }
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["name"] == chinese1
	assert data["id"] == len(starting_tags_list) + 2