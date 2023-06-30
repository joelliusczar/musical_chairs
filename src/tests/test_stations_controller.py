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
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	RulePriorityLevel,
	UserRoleDomain,
	MinItemSecurityLevel
)



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

def test_get_station_user_rule_selection(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_november", client)

	response = client.get(
		"stations/2/romeo_station/catalogue",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert len(data["stationRules"]) == 2

	assert data["stationRules"][0]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][0]["priority"] \
		== RulePriorityLevel.STATION_PATH.value
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Station.value
	assert data["stationRules"][0]["count"] == 5
	assert data["stationRules"][0]["span"] == 300

	assert data["stationRules"][1]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][1]["priority"] == RulePriorityLevel.SITE.value
	assert data["stationRules"][1]["domain"] == UserRoleDomain.Site.value
	assert data["stationRules"][1]["count"] == 10
	assert data["stationRules"][1]["span"] == 300

	response = client.get(
		"stations/2/4/catalogue",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert data["stationRules"]
	assert len(data["stationRules"]) == 1
	assert data["stationRules"][0]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][0]["priority"] == RulePriorityLevel.SITE.value
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Site.value
	assert data["stationRules"][0]["count"] == 10
	assert data["stationRules"][0]["span"] == 300

	headers = login_test_user("testUser_oscar", client)

	response = client.get(
		"stations/testUser_bravo/3/catalogue",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert data["stationRules"]
	assert len(data["stationRules"]) == 2
	assert data["stationRules"][0]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][0]["priority"] \
		== RulePriorityLevel.STATION_PATH.value + 1
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Site.value
	assert data["stationRules"][0]["count"] == 5
	assert data["stationRules"][0]["span"] == 120

	assert data["stationRules"][1]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][1]["priority"] \
		== RulePriorityLevel.STATION_PATH.value
	assert data["stationRules"][1]["domain"] == UserRoleDomain.Station.value
	assert data["stationRules"][1]["count"] == 5
	assert data["stationRules"][1]["span"] == 60

	headers = login_test_user("testUser_papa", client)

	response = client.get(
		"stations/2/3/catalogue",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert data["stationRules"]
	assert len(data["stationRules"]) == 2
	assert data["stationRules"][0]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][0]["priority"] \
		== RulePriorityLevel.STATION_PATH.value
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Station.value
	assert data["stationRules"][0]["count"] == 25
	assert data["stationRules"][0]["span"] == 300

	assert data["stationRules"][1]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][1]["priority"] == RulePriorityLevel.SITE.value
	assert data["stationRules"][1]["domain"] == UserRoleDomain.Site.value
	assert data["stationRules"][1]["count"] == 20
	assert data["stationRules"][1]["span"] == 300

	headers = login_test_user("testUser_quebec", client)

	response = client.get(
		"stations/testUser_bravo/romeo_station/catalogue",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert data["stationRules"]
	assert len(data["stationRules"]) == 2
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Station.value
	assert data["stationRules"][0]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][0]["priority"] \
		== RulePriorityLevel.STATION_PATH.value
	assert data["stationRules"][0]["domain"] == UserRoleDomain.Station.value
	assert data["stationRules"][0]["count"] == 25
	assert data["stationRules"][0]["span"] == 300

	assert data["stationRules"][1]["name"] == UserRoleDef.STATION_REQUEST.value
	assert data["stationRules"][1]["priority"] == RulePriorityLevel.SITE.value
	assert data["stationRules"][1]["domain"] == UserRoleDomain.Site.value
	assert data["stationRules"][1]["count"] == 15
	assert data["stationRules"][1]["span"] == 300

@pytest.mark.usefixtures("fixture_clean_station_folders")
def test_post_with_invalid_security_levels(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_tango", client)
	testData: dict[str, Any] = {
		"name": "test_station",
		"viewSecurityLevel": MinItemSecurityLevel.OWENER_USER.value,
		"requestSecurityLevel": MinItemSecurityLevel.ANY_USER.value,
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)

	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["msg"] \
		== "Request Security cannot be public or lower than view security"
	assert data["detail"][0]["field"] == "requestSecurityLevel"

	testData: dict[str, Any] = {
		"name": "test_station",
		"viewSecurityLevel": MinItemSecurityLevel.PUBLIC.value,
		"requestSecurityLevel": MinItemSecurityLevel.PUBLIC.value,
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 422
	assert data["detail"][0]["msg"] \
		== "Request Security cannot be public or lower than view security"
	assert data["detail"][0]["field"] == "requestSecurityLevel"

	testData: dict[str, Any] = {
		"name": "test_station",
		"viewSecurityLevel": MinItemSecurityLevel.ANY_USER.value,
		"requestSecurityLevel": MinItemSecurityLevel.ANY_USER.value,
	}

	response = client.post(
		"stations",
		headers=headers,
		json=testData
	)
	data = json.loads(response.content)
	assert response.status_code == 200

def test_get_station_for_edit_with_view_security(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client

	response = client.get(
		"stations/testUser_bravo/romeo_station",
	)

	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == 3
	assert data["name"] == "romeo_station"
	assert data["owner"]["username"] == "testUser_bravo"
	assert data["requestSecurityLevel"] == MinItemSecurityLevel.ANY_USER.value
	assert data["viewSecurityLevel"] == MinItemSecurityLevel.PUBLIC.value
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/bravo_station_rerun",
	)

	assert response.status_code == 404

	headers = login_test_user("testUser_romeo", client)

	response = client.get(
		"stations/testUser_bravo/romeo_station",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/bravo_station_rerun",
		headers=headers,
	)

	data = json.loads(response.content)
	assert response.status_code == 200

	assert data["id"] == 13
	assert data["name"] == "bravo_station_rerun"
	assert data["owner"]["username"] == "testUser_victor"
	assert data["requestSecurityLevel"] == MinItemSecurityLevel.ANY_USER.value
	assert data["viewSecurityLevel"] == MinItemSecurityLevel.ANY_USER.value
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/alpha_station_rerun",
		headers=headers,
	)

	assert response.status_code == 404

	headers = login_test_user("testUser_whiskey", client)

	response = client.get(
		"stations/testUser_bravo/romeo_station",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == [{
			"name": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value,
			"domain": "site"
	}]


	response = client.get(
		"stations/testUser_victor/bravo_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == [{
			"name": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value,
			"domain": "site"
	}]

	response = client.get(
		"stations/testUser_victor/alpha_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == 12
	assert data["name"] == "alpha_station_rerun"
	assert data["owner"]["username"] == "testUser_victor"
	assert data["requestSecurityLevel"] == MinItemSecurityLevel.RULED_USER.value
	assert data["viewSecurityLevel"] == MinItemSecurityLevel.RULED_USER.value
	assert data["rules"] == [{
			"name": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.SITE.value,
			"domain": "site"
	}]

	headers = login_test_user("testUser_xray", client)

	response = client.get(
		"stations/testUser_bravo/romeo_station",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/bravo_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/alpha_station_rerun",
		headers=headers,
	)

	assert response.status_code == 404

	response = client.get(
		"stations/testUser_victor/charlie_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == 14
	assert data["name"] == "charlie_station_rerun"
	assert data["owner"]["username"] == "testUser_victor"
	assert data["requestSecurityLevel"] == MinItemSecurityLevel.INVITED_USER.value
	assert data["viewSecurityLevel"] == MinItemSecurityLevel.INVITED_USER.value
	assert data["rules"] == [{
			"name": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.STATION_PATH.value,
			"domain": "station"
	}]

	headers = login_test_user("testUser_yankee", client)

	response = client.get(
		"stations/testUser_bravo/romeo_station",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/bravo_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["rules"] == []

	response = client.get(
		"stations/testUser_victor/alpha_station_rerun",
		headers=headers,
	)
	assert response.status_code == 404

	response = client.get(
		"stations/testUser_victor/charlie_station_rerun",
		headers=headers,
	)
	assert response.status_code == 404

	response = client.get(
		"stations/testUser_victor/delta_station_rerun",
		headers=headers,
	)
	assert response.status_code == 404

	response = client.get(
		"stations/testUser_yankee/delta_station_rerun",
		headers=headers,
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["id"] == 15
	assert data["name"] == "delta_station_rerun"
	assert data["owner"]["username"] == "testUser_yankee"
	assert data["requestSecurityLevel"] == MinItemSecurityLevel.OWENER_USER.value
	assert data["viewSecurityLevel"] == MinItemSecurityLevel.OWENER_USER.value
	assert sorted(data["rules"], key=lambda d: d["name"]) == [
		{
			"name": UserRoleDef.STATION_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		},
		{
			"name": UserRoleDef.STATION_DELETE.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		},
		{
			"name": UserRoleDef.STATION_EDIT.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		},
		{
			"name": UserRoleDef.STATION_USER_ASSIGN.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		},
		{
			"name": UserRoleDef.STATION_USER_LIST.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		},
		{
			"name": UserRoleDef.STATION_VIEW.value,
			"span":0,
			"count":0,
			"priority": RulePriorityLevel.OWNER.value,
			"domain": "station"
		}
	]


def test_rule_adding_validation(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	#can request on station 3
	headers = login_test_user("testUser_oomdwell", client)

	rule = {
		"name": UserRoleDef.STATION_VIEW.value,
		"span": 0,
		"count": 0,
		"priority": None,
	}
	response = client.post(
		f"stations/10/zulu_station/user_role?subjectUserKey={28}",
		headers=headers,
		json=rule
	)
	data = json.loads(response.content)
	assert response.status_code == 200
	assert data["name"] == UserRoleDef.STATION_VIEW.value
	assert data["span"] == 0
	assert data["count"] == 0
	assert data["priority"] == RulePriorityLevel.STATION_PATH.value

	rule["name"] = "dumb_shit"

	response = client.post(
		f"stations/10/zulu_station/user_role?subjectUserKey={28}",
		headers=headers,
		json=rule
	)
	assert response.status_code == 422

	rule["name"] = UserRoleDef.PATH_EDIT.value

	response = client.post(
		f"stations/10/zulu_station/user_role?subjectUserKey={28}",
		headers=headers,
		json=rule
	)
	assert response.status_code == 422

	rule["name"] = UserRoleDef.STATION_REQUEST.value

	response = client.post(
		f"stations/2/1/user_role?subjectUserKey={28}",
		headers=headers,
		json=rule
	)
	assert response.status_code == 403

	rule["name"] = UserRoleDef.PATH_EDIT.value

	response = client.post(
		f"stations/2/1/user_role?subjectUserKey={28}",
		headers=headers,
		json=rule
	)
	assert response.status_code == 403
