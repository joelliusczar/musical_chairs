import copy
from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .helpers import normalize_dict, mismatched_properties
from .constant_fixtures_for_test import (
	fixture_primary_user as fixture_primary_user
)
from .mocks.db_data import (
	bravo_user_id,
	kilo_user_id,
	public_tokens,
	station_saver_user_id,
)
from musical_chairs_libs.dtos_and_utilities.constants import StationTypes
from musical_chairs_libs.dtos_and_utilities import (
	ConfigAcessors,
	RulePriorityLevel,
	UserRoleDef,
	path_owner_rules
)




def test_song_ls_hit(
	fixture_api_test_client: TestClient,
	fixture_primary_user: dtos.InternalUser,
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
	items = sorted(data.get("items", []), key=lambda i: i["treepath"])
	assert len(items) == 1
	assert items[0]["treepath"] == "foo/"
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
	items = sorted(data.get("items", []), key=lambda i: i["treepath"])
	assert len(items) == 1
	assert items[0]["treepath"] == "foo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["treepath"])
	assert len(items) == 1
	assert items[0]["treepath"] == "foo/goo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/goo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["treepath"])
	assert len(items) == 1
	assert items[0]["treepath"] == "foo/goo/boo/"

	response = client.get(
		"/song-info/songs/ls?prefix=foo/goo/boo/",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = sorted(data.get("items", []), key=lambda i: i["treepath"])
	assert len(items) == 5
	assert items[0]["treepath"] == "foo/goo/boo/sierra"
	assert items[1]["treepath"] == "foo/goo/boo/tango"
	assert items[2]["treepath"] == "foo/goo/boo/uniform"
	assert items[3]["treepath"] == "foo/goo/boo/victor"
	assert items[4]["treepath"] == "foo/goo/boo/victor_2"

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
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers
	)

	assert getResponseBefore.status_code == 200
	data = json.loads(getResponseBefore.content)
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update"
	sendData["album"] = {
		"id": dtos.encode_id(8),
		"name": "shoo_album",
		"year": 2003,
		"albumartist": {
			"id": dtos.encode_id(6),
			"name": "foxtrot_artist",
			"isprimaryartist": False
		},
		"versionnote": "",
		"rules": [],
		"viewsecuritylevel": 0,
	}
	sendData["genre"] = "pop_update"
	sendData["notes"] = "Kazoos make good swimmers update"
	sendData["primaryartist"] = {
		"id": dtos.encode_id(10),
		"name": "juliet_artist",
		"isprimaryartist": True
	}
	sendData["stations"] = [
		{ "id": dtos.encode_id(2),
			"name": "papa_station",
			"displayname": "Come to papa",
			"owner": None,
			"requestsecuritylevel": 9,
			"viewsecuritylevel": 0,
			"isrunning": False,
			"typeid": StationTypes.SONGS_ONLY.value,
			"bitratekps": None,
			"playnum": 1
		},
		{
			"id": dtos.encode_id(7),
			"name": "uniform_station",
			"displayname": "Asshole at the wheel",
			"owner": None,
			"requestsecuritylevel": 9,
			"viewsecuritylevel": 0,
			"isrunning": False,
			"typeid": StationTypes.SONGS_ONLY.value,
			"bitratekps": None,
			"playnum": 1
		},
		{
			"id": dtos.encode_id(10),
			"name": "xray_station",
			"displayname": "Pentagular",
			"owner": None,
			"requestsecuritylevel": 9,
			"viewsecuritylevel": 0,
			"isrunning": False,
			"typeid": StationTypes.SONGS_ONLY.value,
			"bitratekps": None,
			"playnum": 1
		}
	]
	sendData["artists"] = [
		{ 
			"id": dtos.encode_id(9), 
			"name": "india_artist", 
			"isprimaryartist": False
		},
		{ 
			"id": dtos.encode_id(13), 
			"name": "november_artist", 
			"isprimaryartist": False
		},
		{ 
			"id": dtos.encode_id(3), 
			"name": "charlie_artist", 
			"isprimaryartist": False
		}
	]

	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers
	)

	assert getResponseAfter.status_code == 200
	data = json.loads(getResponseAfter.content)
	for s in sendData["stations"]:
		s["isrunning"] = False


	sendData["stations"][0]["rules"] = []
	sendData["stations"][1]["rules"] = []
	sendData["stations"][2]["rules"] = []
	mismatches = mismatched_properties(
		normalize_dict(data),
		normalize_dict(sendData),
		{
			'album.owner',
			'album.albumartist.owner',
			'primaryartist.owner',
			'artists[].owner',
			'stations[].owner'
		}
	)
	assert not mismatches

def test_song_save_with_unpermitted_stations(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_hotel", client)
	getResponseBefore = client.get(
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers
	)
	data = json.loads(getResponseBefore.content)
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update_3"

	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(1)}",
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
		f"song-info/songs/{dtos.encode_id(1)}",
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
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers
	)
	data = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "sierra_song_update_3"
	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(1)}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/{dtos.encode_id(1)}",
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
		f"song-info/songs/{dtos.encode_id(51)}",
		headers=headers
	)

	assert getResponseBefore.status_code == 200
	data = json.loads(getResponseBefore.content)
	sendData = data
	sendData["name"] = "Baseline update"

	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(51)}",
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
		"id": dtos.encode_id(19),
		"name": "india_station_rerun",
		"displayname": "bitchingly fast!",
		"owner": {
			"id": dtos.encode_id(station_saver_user_id),
			"username": "stationSaver_testUser",
			"displayname": "Station Saver"
		},
		"isrunning": False,
		"rules": [],
		"requestsecuritylevel": RulePriorityLevel.REQUIRES_INVITE.value,
		"viewsecuritylevel": RulePriorityLevel.REQUIRES_INVITE.value
	})
	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(51)}",
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
		"song-info/songs/multi/"
		f"?itemIds={dtos.encode_id(2)}&itemIds={dtos.encode_id(3)}",
		headers=headers
	)

	data = json.loads(response.content)
	assert response.status_code == 200
	touched = data["touched"]
	assert data["id"] == ""
	assert data["name"] == ""
	assert "name" not in touched
	assert data["treepath"] == ""
	assert "treepath" not in touched
	assert data["album"]["id"] == dtos.encode_id(11)
	assert data["album"]["name"] == "boo_album"
	assert "album" in touched
	assert data["primaryartist"] == None
	assert "primaryartist" in touched
	assert data["artists"] == [{
		"id": dtos.encode_id(4),
		"name": "delta_artist",
		"owner": {
			"id": kilo_user_id,
			"username": "testUser_kilo",
			"displayname": "",
			"publictoken": public_tokens[kilo_user_id]
		},
		"isprimaryartist": False
	}]
	assert "artists" in touched
	assert data["covers"] == []
	assert data["track"] == None
	assert "track" not in touched
	assert data["discnum"] == 1
	assert "discnum" in touched
	assert data["genre"] == "pop"
	assert "genre" in touched
	assert data["bitrate"] == 144
	assert "bitrate" in touched
	assert data["samplerate"] == None
	assert "samplerate" in touched
	assert data["notes"] == None
	assert "notes" not in touched
	assert data["duration"] == None
	assert "duration" in touched
	assert data["explicit"] == None
	assert "explicit" not in touched
	assert data["lyrics"] == ""
	assert "lyrics" in touched
	assert data["stations"] == [
		{ "id": dtos.encode_id(1),
			"name": "oscar_station",
			"displayname": "Oscar the grouch",
			"isrunning": False,
			"owner": {
				"id": bravo_user_id,
				"username": "testUser_bravo",
				"displayname": "Bravo Test User",
				"publictoken": public_tokens[bravo_user_id]
			},
			"rules": [],
			"requestsecuritylevel": 9,
			"viewsecuritylevel": 0,
			"typeid": StationTypes.SONGS_ONLY.value,
			"bitratekps": None,
			"playnum": 1
		}
	]
	assert "stations" in touched
	assert "touched" not in touched

def test_song_save_for_multi_edit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_india", client)
	envManager = ConfigAcessors()
	back_key = envManager.back_key()
	headers["x-back-key"] = back_key

	idList = f"?itemIds={dtos.encode_id(10)}&itemIds={dtos.encode_id(4)}"\
		f"&itemIds={dtos.encode_id(17)}&itemIds={dtos.encode_id(11)}"\
		f"&itemIds={dtos.encode_id(15)}"

	getResponseBefore = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)

	data0 = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	assert data0
	assert len(set(d["id"] for d in data0)) == len(data0)
	assert len(set(d["treepath"] for d in data0)) == len(data0)
	assert len(set(d["name"] for d in data0)) == len(data0)
	assert len(set(d["album"]["id"] for d in data0 if d["album"])) == 4
	assert len(set(d["primaryartist"] for d in data0 if d["primaryartist"])) == 0
	artistsLen = len(set(
		(*(a["id"] for a in d["artists"]),)
		for d in data0 if d["artists"])
	)
	assert artistsLen == 4
	coversLen = len(set(
		(*(a["id"] for a in d["covers"]),)
		for d in data0 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data0)) == 4
	assert len(set(d["discnum"] for d in data0)) == 2
	assert len(set(d["genre"] for d in data0)) == 2
	assert len(set(d["bitrate"] for d in data0)) == 2
	assert len(set(d["samplerate"] for d in data0)) == 1
	assert len(set(d["notes"] for d in data0)) == 4
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 5

	sendData: dict[str, Any] = {
		"name": "",
		"album": {
			"id": dtos.encode_id(12),
			"name": "garoo_album",
			"owner": {"id": kilo_user_id }
		},
		"stations": [
			{
				"id": dtos.encode_id(6),
				"name": "yankee_station",
				"displayname": "Blurg the blergos"
			},
			{
				"id": dtos.encode_id(8),
				"name": "victor_station",
				"displayname": "Fat, drunk, and stupid"
			}
		],
		"primaryartist": {
			"id": dtos.encode_id(14),
			"name":
			"oscar_artist",
			"owner": {"id": kilo_user_id },
			"isprimaryartist": True
		},
		"artists": [
			{ "id": dtos.encode_id(8), 
				"name": "hotel_artist",
				"owner": {"id": kilo_user_id } 
			},
			{ "id": dtos.encode_id(1), 
				"name": "alpha_artist",
				"owner": {"id": kilo_user_id } 
			}
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
	assert len(set(d["treepath"] for d in data2)) == len(data2)
	assert len(set(d["name"] for d in data2)) == len(data2)
	assert len(set(d["album"]["id"] for d in data2 if d["album"])) == 1
	assert len(set(d["primaryartist"]["id"] for d in data2
		if d["primaryartist"])
	) == 1
	artistsLen = len(set(
		(*(a["id"] for a in d["artists"]),)
		for d in data2 if d["artists"])
	)
	assert artistsLen == 1
	coversLen = len(set(
		(*(a["id"] for a in d["covers"]),)
		for d in data2 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data2)) == 4
	assert len(set(d["discnum"] for d in data2)) == 2
	assert len(set(d["genre"] for d in data2)) == 2
	assert len(set(d["bitrate"] for d in data2)) == 2
	assert len(set(d["samplerate"] for d in data2)) == 1
	assert len(set(d["notes"] for d in data2)) == 4
	assert len(set(d["duration"] for d in data2)) == 1
	assert len(set(d["explicit"] for d in data2)) == 1
	assert len(set(d["lyrics"] for d in data2)) == 1
	stationsLen = len(set(
		(*(a["id"] for a in d["stations"]),)
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
	envManager = ConfigAcessors()
	back_key = envManager.back_key()
	headers["x-back-key"] = back_key

	idList = f"?itemIds={dtos.encode_id(29)}&itemIds={dtos.encode_id(28)}"\
			f"&itemIds={dtos.encode_id(27)}&itemIds={dtos.encode_id(26)}"\
			f"&itemIds={dtos.encode_id(25)}&itemIds={dtos.encode_id(24)}"\
			f"&itemIds={dtos.encode_id(23)}"

	getResponseBefore = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)

	data0 = json.loads(getResponseBefore.content)
	assert getResponseBefore.status_code == 200
	assert data0
	assert len(set(d["id"] for d in data0)) == len(data0)
	assert len(set(d["treepath"] for d in data0)) == len(data0)
	assert len(set(d["name"] for d in data0)) == len(data0)
	assert len(set(d["album"]["id"] for d in data0 if d["album"])) == 2
	assert len(set(d["primaryartist"] for d in data0 if d["primaryartist"])) == 0
	artistsLen = len(set(
		(*(a["id"] for a in d["artists"]),)
		for d in data0 if d["artists"])
	)
	assert artistsLen == 1
	coversLen = len(set(
		(*(a["id"] for a in d["covers"]),)
		for d in data0 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data0)) == 1
	assert len(set(d["discnum"] for d in data0)) == 1
	assert len(set(d["genre"] for d in data0)) == 1
	assert len(set(d["bitrate"] for d in data0)) == 1
	assert len(set(d["samplerate"] for d in data0)) == 1
	assert len(set(d["notes"] for d in data0)) == 1
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 2

	sendData: dict[str, Any] = {
		"name": "",
		"album": {
			"id": dtos.encode_id(12),
			"name": "garoo_album",
			"owner": { "id": kilo_user_id}
		},
		"stations": [
			{
				"id": dtos.encode_id(6),
				"name": "yankee_station",
				"displayname": "Blurg the blergos"
			},
			{
				"id": dtos.encode_id(8),
				"name": "victor_station",
				"displayname": "Fat, drunk, and stupid"
			},
		],
		"artists": [],
		"primaryartist": {
			"id": dtos.encode_id(5),
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
	assert len(set(d["treepath"] for d in data2)) == len(data2)
	assert len(set(d["name"] for d in data2)) == len(data2)
	assert len(set(d["album"]["id"] for d in data2 if d["album"])) == 1
	assert len(set(d["primaryartist"]["id"] for d in data2
		if d["primaryartist"])
	) == 1
	artistsLen = len(set(
		(*(a["id"] for a in d["artists"]),)
		for d in data2 if d["artists"])
	)
	assert artistsLen == 0
	coversLen = len(set(
		(*(a["id"] for a in d["covers"]),)
		for d in data2 if d["covers"])
	)
	assert coversLen == 0
	assert len(set(d["track"] for d in data2)) == 1
	assert len(set(d["discnum"] for d in data2)) == 1
	assert len(set(d["genre"] for d in data2)) == 1
	assert len(set(d["bitrate"] for d in data2)) == 1
	assert len(set(d["samplerate"] for d in data2)) == 1
	assert len(set(d["notes"] for d in data2)) == 1
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
		f"song-info/songs/{dtos.encode_id(5)}",
		headers=headers
	)

	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "victor_song_update"
	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(5)}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 200

	getResponse = client.get(
		f"song-info/songs/{dtos.encode_id(6)}",
		headers=headers
	)

	data = json.loads(getResponse.content)
	assert getResponse.status_code == 200
	sendData = copy.deepcopy(data)
	sendData["name"] = "whiskey_song_update"
	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(6)}",
		headers=headers,
		json=sendData
	)

	assert putResponse.status_code == 403

	headers = login_test_user("testUser_india", client)

	putResponse = client.put(
		f"song-info/songs/{dtos.encode_id(6)}",
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
	assert rules[1]["name"] == UserRoleDef.PATH_DOWNLOAD.value
	assert rules[2]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[3]["name"] == UserRoleDef.PATH_LIST.value
	assert rules[4]["name"] == UserRoleDef.PATH_MOVE.value
	assert rules[5]["name"] == UserRoleDef.PATH_UPLOAD.value
	assert rules[6]["name"] == UserRoleDef.PATH_USER_ASSIGN.value
	assert rules[7]["name"] == UserRoleDef.PATH_USER_LIST.value
	assert rules[8]["name"] == UserRoleDef.PATH_VIEW.value
	assert items[1]["username"] == "testUser_kilo"
	rules = sorted(items[1]["roles"], key=lambda r: r["name"])
	assert len(rules) == len(path_owner_rules)
	assert rules[0]["name"] == UserRoleDef.PATH_DELETE.value
	assert rules[1]["name"] == UserRoleDef.PATH_DOWNLOAD.value
	assert rules[2]["name"] == UserRoleDef.PATH_EDIT.value
	assert rules[3]["name"] == UserRoleDef.PATH_LIST.value
	assert rules[4]["name"] == UserRoleDef.PATH_MOVE.value
	assert rules[5]["name"] == UserRoleDef.PATH_UPLOAD.value
	assert rules[6]["name"] == UserRoleDef.PATH_USER_ASSIGN.value
	assert rules[7]["name"] == UserRoleDef.PATH_USER_LIST.value
	assert rules[8]["name"] == UserRoleDef.PATH_VIEW.value
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