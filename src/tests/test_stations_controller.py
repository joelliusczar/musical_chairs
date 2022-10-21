import json
from typing import Any
from .api_test_dependencies import login_test_user,\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .mocks.db_population import get_initial_stations, get_initial_tags




def test_invalid_post_duplicate_name(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "oscar_station",
		"displayName":"Oscar the grouch",
		"tags":[]
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["msg"] == "oscar_station is already used."
	assert data["detail"][0]["field"] == "name"

	testData = {
			"name": "oscar_station",
			"displayName":"Oscar the grouch",
			"tags":[
				{ "id": 2, "name": "badlima_tag"},
				{ "id": 2, "name": "november_tag"},
				{ "id": 7, "name": "badromeo_tag"}
			]
	}

def test_post_with_only_name(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	initialStations = get_initial_stations()
	headers = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "test_station",
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	nextId = data["id"]
	assert nextId == len(initialStations) + 1

	response = client.get("stations", params={ "id": nextId })
	fetched = json.loads(response.content)
	assert response.status_code == 200
	assert fetched["name"] == "test_station"
	assert fetched["displayName"] == ""
	assert fetched["tags"] == []

def test_invalid_post_with_duplicate_tags(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client

	headers = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "test_station",
		"tags":[
				{ "id": 2, "name": "badlima_tag"},
				{ "id": 2, "name": "november_tag"},
				{ "id": 7, "name": "badromeo_tag"}
			]
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["msg"] == \
		"Tag with id 2 has been added 2 times but it is only legal to add it once."
	assert data["detail"][0]["field"] == "tags"

def test_post_with_nonexistent_tags(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	initialTags = get_initial_tags()
	headers = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "test_station",
		"tags":[
				{ "id": len(initialTags) + 1, "name": "badlima_tag"},
			]
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 422
	expected = \
		f"Tags associated with ids {{{len(initialTags) + 1}}} do not exist"
	assert data["detail"][0]["msg"] == expected
	assert data["detail"][0]["field"] == "tags"