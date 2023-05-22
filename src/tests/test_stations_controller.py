import json
import pytest
from typing import Any
from .api_test_dependencies import (
	login_test_user,
	fixture_api_test_client as fixture_api_test_client
)
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .mocks.db_population import get_initial_stations
from .common_fixtures import (
	fixture_clean_station_folders as fixture_clean_station_folders,
	datetime_monkey_patch as datetime_monkey_patch
)
from .constant_fixtures_for_test import mock_ordered_date_list




def test_invalid_post_duplicate_name(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	julietHeaders = login_test_user("testUser_juliet", client)
	testData: dict[str, Any] = {
		"name": "oscar_station",
		"displayName":"Oscar the grouch"
	}

	response = client.post(
		"stations",
		headers=julietHeaders,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 403

	client = fixture_api_test_client
	bravoHeaders = login_test_user("testUser_bravo", client)
	testData: dict[str, Any] = {
		"name": "oscar_station",
		"displayName":"Oscar the grouch"
	}

	response = client.post(
		"stations",
		headers=bravoHeaders,
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
	headers = login_test_user("testUser_tango", client)
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

	response = client.get(f"stations/20/{nextId}")
	fetched = json.loads(response.content)
	assert response.status_code == 200
	assert fetched["name"] == "test_station"
	assert fetched["displayName"] == ""

def test_updating_unchanged(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_bravo", client)
	response = client.get(
		"stations/check/?name=romeo_station&id=3",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert not data["name"]

	response = client.get(
		"stations/check/?name=romeo_station&id=4",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["name"]


def test_request_song(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	#can request on station 3
	headers = login_test_user("testUser_kilo", client)

	response = client.post(
		"stations/testUser_bravo/romeo_station/request/36",
		headers=headers
	)
	assert response.status_code == 200

	#can request on any station
	headers = login_test_user("testUser_lima", client)

	response = client.post(
		"stations/testUser_bravo/romeo_station/request/36",
		headers=headers
	)
	assert response.status_code == 200

	headers = login_test_user("testUser_mike", client)

	response = client.post(
		"stations/testUser_bravo/romeo_station/request/36",
		headers=headers
	)
	assert response.status_code == 200


def test_request_song_only_one_staion_allowed(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	#can request on station 3
	headers = login_test_user("testUser_kilo", client)

	response = client.post(
		"stations/testUser_bravo/romeo_station/request/36",
		headers=headers
	)
	assert response.status_code == 200

	response = client.post(
		"stations/testUser_bravo/papa_station/request/40",
		headers=headers
	)
	assert response.status_code == 403

def test_request_song_any_station(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_mike", client)

	response = client.post(
		"stations/2/romeo_station/request/36",
		headers=headers
	)
	assert response.status_code == 200

	response = client.post(
		"stations/2/papa_station/request/40",
		headers=headers
	)
	assert response.status_code == 200

	response = client.post(
		"stations/2/oscar_station/request/30",
		headers=headers
	)
	assert response.status_code == 200

	response = client.post(
		"stations/2/sierra_station/request/15",
		headers=headers
	)
	assert response.status_code == 200

@pytest.mark.testDatetimes(mock_ordered_date_list[2:])
def test_request_song_timeout(
	datetime_monkey_patch: MockDatetimeProvider,
	fixture_api_test_client: TestClient
):
	datetimeProvider = datetime_monkey_patch
	client = fixture_api_test_client
	headers = login_test_user("testUser_november", client)

	#1 t=0 [2]
	#2 t=s+15 [3]
	#3 t=s+20 [4]
	#4 t=s+25 [5]
	#5 t=m+3, s+7 [6]
	for _ in datetimeProvider(5):
		response = client.post(
			"stations/testUser_bravo/3/request/36",
			headers=headers
		)
		assert response.status_code == 200

	pass
	#6 t=m+4, s+7 [7]
	#7 t=m+4, s+30 [8]
	#8 t=m+4, s+45 [9]
	#9 t=m+4, s+55 [10]
	#10 t=m+4, s+59 [11]
	for _ in datetimeProvider(5):
		response = client.post(
			"stations/testUser_bravo/3/request/36",
			headers=headers
		)
		assert response.status_code == 429

	next(datetimeProvider)

	#12 t=m+5 [12]
	response = client.post(
			"stations/testUser_bravo/3/request/36",
			headers=headers
	)
	assert response.status_code == 200

	next(datetimeProvider)

	#13 t=m+5, s+14 [13]
	response = client.post(
			"stations/testUser_bravo/3/request/36",
			headers=headers
	)
	assert response.status_code == 429

