import json
import pytest
from typing import Any
from .api_test_dependencies import login_test_user,\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .mocks.db_population import get_initial_stations
from .common_fixtures import\
	fixture_clean_station_folders as fixture_clean_station_folders




def test_invalid_post_duplicate_name(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "oscar_station",
		"displayName":"Oscar the grouch"
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
			"displayName":"Oscar the grouch"
	}

@pytest.mark.usefixtures("fixture_clean_station_folders")
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

def test_updating_unchanged(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	response = client.get(
		"stations/check/?name=romeo_station&id=3",
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert not data["name"]

	response = client.get(
		"stations/check/?name=romeo_station&id=4",
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["name"]