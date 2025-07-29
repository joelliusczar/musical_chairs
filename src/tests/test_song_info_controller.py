import copy
from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .helpers import normalize_dict, mismatched_properties
from .constant_fixtures_for_test import (
	fixture_primary_user as fixture_primary_user
)
from .mocks.db_data import kilo_user_id, station_saver_user_id
from musical_chairs_libs.dtos_and_utilities import (
	MinItemSecurityLevel,
	UserRoleDef,
	path_owner_rules
)



def test_song_ls_hit(
	fixture_api_test_client: TestClient,
	fixture_primary_user: AccountInfo,
):
	client = fixture_api_test_client

	headers = login_test_user(fixture_primary_user.username, client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

	response = client.get(
		"/song-info/songs/ls?prefix=f",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 1

def test_song_ls_with_site_path_permissions(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client

	headers = login_test_user("paulBear_testUser", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

	response = client.get(
		"/song-info/songs/ls?prefix=",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4


	headers = login_test_user("quirkyAdmon_testUser", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

	response = client.get(
		"/song-info/songs/ls?prefix=",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

	headers = login_test_user("radicalPath_testUser", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

	response = client.get(
		"/song-info/songs/ls?prefix=",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 4

def test_song_ls_with_path_permissions(fixture_api_test_client: TestClient):

	client = fixture_api_test_client

	headers_foo_owner = login_test_user("testUser_kilo", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers_foo_owner
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["path"])
	assert len(items) == 1
	assert items[0]["path"] == "foo/"
	rules = items[0]["rules"]
	assert rules
	assert len(rules) == len(path_owner_rules)


	headers_no_owner = login_test_user("testUser_bravo", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers_no_owner
	)
	assert response.status_code == 403

	headers_foo_goo_boo_user = login_test_user("testUser_lima", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["path"])
	assert len(items) == 1
	assert items[0]["path"] == "foo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["path"])
	assert len(items) == 1
	assert items[0]["path"] == "foo/goo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/goo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["path"])
	assert len(items) == 1
	assert items[0]["path"] == "foo/goo/boo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/goo/boo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["path"])
	assert len(items) == 5
	assert items[0]["path"] == "foo/goo/boo/sierra"
	assert items[1]["path"] == "foo/goo/boo/tango"
	assert items[2]["path"] == "foo/goo/boo/uniform"
	assert items[3]["path"] == "foo/goo/boo/victor"
	assert items[4]["path"] == "foo/goo/boo/victor_2"

def test_song_ls_with_station_permissions(fixture_api_test_client: TestClient):

	client = fixture_api_test_client

	headers = login_test_user("testUser_oomdwell", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 403

	headers = login_test_user("testUser_alice", client)

	response = client.get(
		"/song-info/songs/ls",
		headers=headers
	)
	assert response.status_code == 403

def test_song_save(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_india", client)
	getResponseBefore = client.get(
		f"song-info/songs/{1}",
		headers=headers
	)

	assert getResponseBefore.status_code == 200
	data = json.loads(getResponseBefore.content)
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update"
	sendData["album"] = {
		"id": 8,
		"name": "shoo_album",
		"year": 2003,
		"owner": {"id":kilo_user_id },
		"albumartist": {
			"id": 6,
			"name": "foxtrot_artist",
			"owner": {"id":kilo_user_id },
		},
		"versionnote": ""
	}
	sendData["genre"] = "pop_update"
	sendData["comment"] = "Kazoos make good swimmers update"
	sendData["primaryartist"] = {
		"id": 10,
		"name": "juliet_artist",
		"owner": { "id": kilo_user_id},
	}
	sendData["stations"] = [
		{ "id": 2,
			"name": "papa_station",
			"displayname": "Come to papa",
			"owner": None,
			"requestsecuritylevel": None,
			"viewsecuritylevel": None
		},
		{
			"id": 7,
			"name": "uniform_station",
			"displayname": "Asshole at the wheel",
			"owner": None,
			"requestsecuritylevel": None,
			"viewsecuritylevel": None
		},
		{
			"id": 10,
			"name": "xray_station",
			"displayname": "Pentagular",
			"owner": None,
			"requestsecuritylevel": None,
			"viewsecuritylevel": None
		}
	]
	sendData["artists"] = [
		{ "id": 9, "name": "india_artist", "owner": { "id": kilo_user_id } },
		{ "id": 13, "name": "november_artist", "owner": { "id": kilo_user_id } },
		{ "id": 3, "name": "charlie_artist", "owner": { "id": kilo_user_id } }
	]

	putResponse = client.put(
		f"song-info/songs/{1}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/{1}",
		headers=headers
	)

	assert getResponseAfter.status_code == 200
	data = json.loads(getResponseAfter.content)
	for s in sendData["stations"]:
		s["isrunning"] = False
	sendData["album"]["owner"]["username"] = "testUser_kilo"
	sendData["album"]["owner"]["displayname"] = None
	sendData["album"]["albumartist"]["owner"]["username"] = "testUser_kilo"
	sendData["album"]["albumartist"]["owner"]["displayname"] = None
	sendData["primaryartist"]["owner"]["username"] = "testUser_kilo"
	sendData["primaryartist"]["owner"]["displayname"] = None
	sendData["artists"][0]["owner"]["username"] = "testUser_kilo"
	sendData["artists"][0]["owner"]["displayname"] = None
	sendData["artists"][1]["owner"]["username"] = "testUser_kilo"
	sendData["artists"][1]["owner"]["displayname"] = None
	sendData["artists"][2]["owner"]["username"] = "testUser_kilo"
	sendData["artists"][2]["owner"]["displayname"] = None

	sendData["stations"][0]["owner"] = {
		"id": 2,
		"username":"testUser_bravo",
		"displayname": "Bravo Test User",
	}
	sendData["stations"][0]["rules"] = []
	sendData["stations"][1]["owner"] = {
		"id": 2,
		"username":"testUser_bravo",
		"displayname": "Bravo Test User",
	}
	sendData["stations"][1]["rules"] = []
	sendData["stations"][2]["owner"] = {
		"id": 2,
		"username":"testUser_bravo",
		"displayname": "Bravo Test User",
	}
	sendData["stations"][2]["rules"] = []
	mismatches = mismatched_properties(
		normalize_dict(data),
		normalize_dict(sendData)
	)
	assert not mismatches

def test_song_save_with_unpermitted_stations(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_hotel", client)
	getResponseBefore = client.get(
		f"song-info/songs/{1}",
		headers=headers
	)
	data = json.loads(getResponseBefore.content)
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update_3"

	putResponse = client.put(
		f"song-info/songs/{1}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200
	stations = sendData["stations"]
	stations.append({
		"id": 7,
		"name": "uniform_station",
		"displayname": "Asshole at the wheel"
	})

	putResponse = client.put(
		f"song-info/songs/{1}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 422

def test_song_save_no_roles(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	goodHeaders = login_test_user("testUser_india", client)
	getResponseBefore = client.get(
		f"song-info/songs/{1}",
		headers=goodHeaders
	)
	data = json.loads(getResponseBefore.content)
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update_2"

	headers = login_test_user("testUser_romeo", client)
	putResponse = client.put(
		f"song-info/songs/{1}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 403

def test_song_save_with_path_permission(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_mike", client)
	getResponseBefore = client.get(
		f"song-info/songs/{1}",
		headers=headers
	)
	data = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update_3"
	putResponse = client.put(
		f"song-info/songs/{1}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/{1}",
		headers=headers
	)

	assert getResponseAfter.status_code == 200
	data = json.loads(getResponseAfter.content)
	mismatches = mismatched_properties(
		normalize_dict(data),
		normalize_dict(sendData)
	)
	assert not mismatches

def test_song_save_different_station_owner(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("stationSaver_testUser", client)
	getResponseBefore = client.get(
		f"song-info/songs/{51}",
		headers=headers
	)

	assert getResponseBefore.status_code == 200
	data = json.loads(getResponseBefore.content)
	sendData = data
	sendData["name"] = "Baseline update"

	putResponse = client.put(
		f"song-info/songs/{51}",
		headers=headers,
		json=sendData
	)
	assert putResponse.status_code == 200
	data = json.loads(putResponse.content)
	mismatches = mismatched_properties(
		normalize_dict(data),
		normalize_dict(sendData)
	)
	assert not mismatches
	sendData = data
	sendData["stations"].append({
		"id": 19,
		"name": "india_station_rerun",
		"displayname": "bitchingly fast!",
		"owner": {
			"id": station_saver_user_id,
			"username": "stationSaver_testUser",
			"displayname": "Station Saver"
		},
		"isrunning": False,
		"rules": [],
		"requestsecuritylevel": MinItemSecurityLevel.INVITED_USER.value,
		"viewsecuritylevel": MinItemSecurityLevel.INVITED_USER.value
	})
	putResponse = client.put(
		f"song-info/songs/{51}",
		headers=headers,
		json=sendData
	)
	assert putResponse.status_code == 200

def test_get_songs_for_multi_edit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client

	headers = login_test_user("testUser_lima", client)

	response = client.get(
		f"song-info/songs/multi/?itemIds=2&itemIds=3",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200
	touched = data["touched"]
	assert data["id"] == 0
	assert data["name"] == None
	assert "name" not in touched
	assert data["path"] == ""
	assert "path" not in touched
	assert data["album"]["id"] == 11
	assert data["album"]["name"] == "boo_album"
	assert "album" in touched
	assert data["primaryartist"] == None
	assert "primaryartist" in touched
	assert data["artists"] == [{
		"id": 4,
		"name":
		"delta_artist",
		"owner": {
			"id": kilo_user_id,
			"username": "testUser_kilo",
			"displayname": None
		}
	}]
	assert "artists" in touched
	assert data["covers"] == []
	assert data["track"] == None
	assert "track" not in touched
	assert data["disc"] == 1
	assert "disc" in touched
	assert data["genre"] == "pop"
	assert "genre" in touched
	assert data["bitrate"] == 144
	assert "bitrate" in touched
	assert data["samplerate"] == None
	assert "samplerate" in touched
	assert data["comment"] == None
	assert "comment" not in touched
	assert data["duration"] == None
	assert "duration" in touched
	assert data["explicit"] == None
	assert "explicit" not in touched
	assert data["lyrics"] == None
	assert "lyrics" in touched
	assert data["stations"] == [
		{ "id": 1,
			"name": "oscar_station",
			"displayname": "Oscar the grouch",
			"isrunning": False,
			"owner": {
				"id": 2,
				"username": "testUser_bravo",
				"displayname": "Bravo Test User"
			},
			"rules": [],
			"requestsecuritylevel": None,
			"viewsecuritylevel": None
		}
	]
	assert "stations" in touched
	assert "touched" not in touched

def test_song_save_for_multi_edit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_india", client)

	idList = "?itemIds=10&itemIds=4&itemIds=17&itemIds=11&itemIds=15"

	getResponseBefore = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)

	data0 = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	assert data0
	assert len(set(d["id"] for d in data0)) == len(data0)
	assert len(set(d["path"] for d in data0)) == len(data0)
	assert len(set(d["name"] for d in data0)) == len(data0)
	assert len(set(d["album"]["id"] for d in data0 if d["album"])) == 4
	assert len(set(d["primaryartist"] for d in data0 if d["primaryartist"])) == 0
	artistsLen = len(set(
		(*sorted(a["id"] for a in d["artists"]),)
		for d in data0 if d["artists"])
	)
	assert artistsLen == 4
	coversLen = len(set(
		(*sorted(a["id"] for a in d["covers"]),)
		for d in data0 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data0)) == 4
	assert len(set(d["disc"] for d in data0)) == 2
	assert len(set(d["genre"] for d in data0)) == 2
	assert len(set(d["bitrate"] for d in data0)) == 2
	assert len(set(d["samplerate"] for d in data0)) == 1
	assert len(set(d["comment"] for d in data0)) == 4
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 5

	sendData: dict[str, Any] = {
		"album": {
			"id": 12, "name": "garoo_album", "owner": {"id": kilo_user_id }
		},
		"stations": [
			{
				"id": 6,
				"name": "yankee_station",
				"displayname": "Blurg the blergos"
			},
			{
				"id": 8,
				"name": "victor_station",
				"displayname": "Fat, drunk, and stupid"
			}
		],
		"primaryartist": {
			"id": 14,
			"name":
			"oscar_artist",
			"owner": {"id": kilo_user_id }
		},
		"artists": [
			{ "id": 8, "name": "hotel_artist", "owner": {"id": kilo_user_id } },
			{ "id": 1, "name": "alpha_artist", "owner": {"id": kilo_user_id } }
		],
		"touched": ["album", "stations", "primaryartist", "artists"]
	}

	putResponse = client.put(
		f"song-info/songs/multi/{idList}",
		headers=headers,
		json=sendData
	)

	data1 = json.loads(putResponse.content)
	assert putResponse.status_code == 200

	getListResponseAfter = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)
	data2 = json.loads(getListResponseAfter.content)
	assert getListResponseAfter.status_code == 200

	assert len(set(d["id"] for d in data2)) == len(data2)
	assert len(set(d["path"] for d in data2)) == len(data2)
	assert len(set(d["name"] for d in data2)) == len(data2)
	assert len(set(d["album"]["id"] for d in data2 if d["album"])) == 1
	assert len(set(d["primaryartist"]["id"] for d in data2
		if d["primaryartist"])
	) == 1
	artistsLen = len(set(
		(*sorted(a["id"] for a in d["artists"]),)
		for d in data2 if d["artists"])
	)
	assert artistsLen == 1
	coversLen = len(set(
		(*sorted(a["id"] for a in d["covers"]),)
		for d in data2 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data2)) == 4
	assert len(set(d["disc"] for d in data2)) == 2
	assert len(set(d["genre"] for d in data2)) == 2
	assert len(set(d["bitrate"] for d in data2)) == 2
	assert len(set(d["samplerate"] for d in data2)) == 1
	assert len(set(d["comment"] for d in data2)) == 4
	assert len(set(d["duration"] for d in data2)) == 1
	assert len(set(d["explicit"] for d in data2)) == 1
	assert len(set(d["lyrics"] for d in data2)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data2 if d["stations"])
	)
	assert stationsLen == 1

	getResponseAfter = client.get(
		f"song-info/songs/multi/{idList}",
		headers=headers
	)
	data3 = json.loads(getResponseAfter.content)
	assert getResponseAfter.status_code == 200
	data1_n = normalize_dict(data1)
	data3_n = normalize_dict(data3)
	assert data1_n == data3_n

def test_song_save_for_multi_edit_artist_to_primary(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_india", client)

	idList = "?itemIds=29&itemIds=28&itemIds=27"\
		"&itemIds=26&itemIds=25&itemIds=24&itemIds=23"

	getResponseBefore = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)

	data0 = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	assert data0
	assert len(set(d["id"] for d in data0)) == len(data0)
	assert len(set(d["path"] for d in data0)) == len(data0)
	assert len(set(d["name"] for d in data0)) == len(data0)
	assert len(set(d["album"]["id"] for d in data0 if d["album"])) == 2
	assert len(set(d["primaryartist"] for d in data0 if d["primaryartist"])) == 0
	artistsLen = len(set(
		(*sorted(a["id"] for a in d["artists"]),)
		for d in data0 if d["artists"])
	)
	assert artistsLen == 1
	coversLen = len(set(
		(*sorted(a["id"] for a in d["covers"]),)
		for d in data0 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data0)) == 1
	assert len(set(d["disc"] for d in data0)) == 1
	assert len(set(d["genre"] for d in data0)) == 1
	assert len(set(d["bitrate"] for d in data0)) == 1
	assert len(set(d["samplerate"] for d in data0)) == 1
	assert len(set(d["comment"] for d in data0)) == 1
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 2

	sendData: dict[str, Any] = {
		"album": {
			"id": 12, "name": "garoo_album","owner": { "id": kilo_user_id}
		},
		"stations": [
			{
				"id": 6,
				"name": "yankee_station",
				"displayname": "Blurg the blergos"
			},
			{
				"id": 8,
				"name": "victor_station",
				"displayname": "Fat, drunk, and stupid"
			},
		],
		"artists": [],
		"primaryartist": {
			"id": 5,
			"name":
			"foxtrot_artist",
			"owner": { "id": kilo_user_id}
		},
		"touched": ["album", "stations", "primaryartist", "artists"]
	}

	putResponse = client.put(
		f"song-info/songs/multi/{idList}",
		headers=headers,
		json=sendData
	)

	data1 = json.loads(putResponse.content)
	assert putResponse.status_code == 200

	getListResponseAfter = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)
	data2 = json.loads(getListResponseAfter.content)
	assert getListResponseAfter.status_code == 200


	assert len(set(d["id"] for d in data2)) == len(data2)
	assert len(set(d["path"] for d in data2)) == len(data2)
	assert len(set(d["name"] for d in data2)) == len(data2)
	assert len(set(d["album"]["id"] for d in data2 if d["album"])) == 1
	assert len(set(d["primaryartist"]["id"] for d in data2
		if d["primaryartist"])
	) == 1
	artistsLen = len(set(
		(*sorted(a["id"] for a in d["artists"]),)
		for d in data2 if d["artists"])
	)
	assert artistsLen == 0
	coversLen = len(set(
		(*sorted(a["id"] for a in d["covers"]),)
		for d in data2 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data2)) == 1
	assert len(set(d["disc"] for d in data2)) == 1
	assert len(set(d["genre"] for d in data2)) == 1
	assert len(set(d["bitrate"] for d in data2)) == 1
	assert len(set(d["samplerate"] for d in data2)) == 1
	assert len(set(d["comment"] for d in data2)) == 1
	assert len(set(d["duration"] for d in data2)) == 1
	assert len(set(d["explicit"] for d in data2)) == 1
	assert len(set(d["lyrics"] for d in data2)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data2 if d["stations"])
	)
	assert stationsLen == 1

	getResponseAfter = client.get(
		f"song-info/songs/multi/{idList}",
		headers=headers
	)
	data3 = json.loads(getResponseAfter.content)
	assert getResponseAfter.status_code == 200
	data1_n = normalize_dict(data1)
	data3_n = normalize_dict(data3)
	assert data1_n == data3_n

def test_more_restrictive_path(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_sierra", client)
	getResponse = client.get(
		f"song-info/songs/{5}",
		headers=headers
	)

	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "victor_song_update"
	putResponse = client.put(
		f"song-info/songs/{5}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponse = client.get(
		f"song-info/songs/{6}",
		headers=headers
	)

	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "whiskey_song_update"
	putResponse = client.put(
		f"song-info/songs/{6}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 403

	headers = login_test_user("testUser_india", client)

	putResponse = client.put(
		f"song-info/songs/{6}",
		headers=headers,
		json=sendData
	)


	assert putResponse.status_code == 200

@pytest.mark.echo(False)
def test_get_path_users(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_kilo", client)
	getResponse = client.get(
		"song-info/path/user_list?prefix=/foo/goo",
		headers=headers
	)
	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	items = sorted(data["items"], key=lambda u: u["id"])
	assert len(items) == 4
	assert items[0]["username"] == "testUser_alpha"
	rules = sorted(items[0]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)
	assert rules[0]["name"] == UserRoleDef.PATH_DELETE.value
	assert rules[1]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[2]["name"] == UserRoleDef.PATH_LIST.value
	assert rules[3]["name"] == UserRoleDef.PATH_MOVE.value
	assert rules[4]["name"] == UserRoleDef.PATH_UPLOAD.value
	assert rules[5]["name"] == UserRoleDef.PATH_USER_ASSIGN.value
	assert rules[6]["name"] == UserRoleDef.PATH_USER_LIST.value
	assert rules[7]["name"] == UserRoleDef.PATH_VIEW.value
	assert items[1]["username"] == "testUser_kilo"
	rules = sorted(items[1]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)
	assert rules[0]["name"] == UserRoleDef.PATH_DELETE.value
	assert rules[1]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[2]["name"] == UserRoleDef.PATH_LIST.value
	assert rules[3]["name"] == UserRoleDef.PATH_MOVE.value
	assert rules[4]["name"] == UserRoleDef.PATH_UPLOAD.value
	assert rules[5]["name"] == UserRoleDef.PATH_USER_ASSIGN.value
	assert rules[6]["name"] == UserRoleDef.PATH_USER_LIST.value
	assert rules[7]["name"] == UserRoleDef.PATH_VIEW.value
	assert items[2]["username"] == "testUser_mike"
	rules = sorted(items[2]["roles"], key=lambda r: r["name"])
	assert len(rules) == 2
	assert rules[0]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[1]["name"] == UserRoleDef.PATH_VIEW.value
	assert items[3]["username"] == "testUser_sierra"
	rules = sorted(items[3]["roles"], key=lambda r: r["name"])
	assert len(rules) == 2
	assert rules[0]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[1]["name"] == UserRoleDef.PATH_VIEW.value

	getResponse = client.get(
		"song-info/path/user_list?prefix=/foo/goo/boo",
		headers=headers
	)
	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	items = sorted(data["items"], key=lambda u: u["id"])
	assert len(items) == 6
	assert items[0]["username"] == "testUser_alpha"
	rules = sorted(items[0]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)
	assert items[1]["username"] == "testUser_foxtrot"
	rules = sorted(items[1]["roles"], key=lambda r: r["name"])
	assert len(rules) == 1
	assert rules[0]["name"] == UserRoleDef.PATH_EDIT.value

	assert items[2]["username"] == "testUser_kilo"
	rules = sorted(items[2]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)

	assert items[3]["username"] == "testUser_lima"
	rules = sorted(items[3]["roles"], key=lambda r: r["name"])
	assert len(rules) == 2
	assert rules[0]["name"] == UserRoleDef.PATH_LIST.value
	assert rules[1]["name"] == UserRoleDef.PATH_VIEW.value


	assert items[4]["username"] == "testUser_mike"
	rules = sorted(items[4]["roles"], key=lambda r: r["name"])
	assert len(rules) == 2

	assert items[5]["username"] == "testUser_sierra"
	rules = sorted(items[5]["roles"], key=lambda r: r["name"])
	assert len(rules) == 2

	getResponse = client.get(
		"song-info/path/user_list?prefix=/foo/x",
		headers=headers
	)
	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	items = sorted(data["items"], key=lambda u: u["id"])
	assert len(items) == 2
	assert items[0]["username"] == "testUser_alpha"
	rules = sorted(items[0]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)

	assert items[1]["username"] == "testUser_kilo"
	rules = sorted(items[1]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)

	headers = login_test_user("tossedSlash_testUser", client)
	getResponse = client.get(
		"song-info/path/user_list?prefix=/tossedSlash/guess",
		headers=headers
	)
	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	items = sorted(data["items"], key=lambda u: u["id"])
	assert len(items) == 2
	assert items[0]["username"] == "testUser_alpha"
	rules = sorted(items[0]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)

	assert items[1]["username"] == "tossedSlash_testUser"
	rules = sorted(items[1]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)