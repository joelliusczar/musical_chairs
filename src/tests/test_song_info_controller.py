import copy
from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .helpers import normalize_dict, mismatched_properties
from .constant_fixtures_for_test import (
	fixture_primary_user as fixture_primary_user
)



def test_song_ls_hit(
	fixture_api_test_client: TestClient,
	fixture_primary_user: AccountInfo,
):
	client = fixture_api_test_client

	headers = login_test_user(fixture_primary_user.username, client)

	response = client.get(
		"/song-info/songs/tree",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 3

	response = client.get(
		"/song-info/songs/tree?prefix=f",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("items", [])
	assert len(items) == 1

def test_song_ls_with_path_permissions(fixture_api_test_client: TestClient):

	client = fixture_api_test_client

	headers_foo_owner = login_test_user("testUser_kilo", client)

	response = client.get(
		"/song-info/songs/tree",
		headers=headers_foo_owner
	)
	assert response.status_code == 200

	headers_no_owner = login_test_user("testUser_bravo", client)

	response = client.get(
		"/song-info/songs/tree",
		headers=headers_no_owner
	)
	assert response.status_code == 422

	headers_foo_goo_boo_user = login_test_user("testUser_lima", client)

	response = client.get(
		"/song-info/songs/tree",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 200

	response = client.get(
		"/song-info/songs/tree?prefix=foo",
		headers=headers_foo_goo_boo_user
	)
	assert response.status_code == 404

def test_song_save(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_foxtrot", client)
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
		"albumArtist": {
			"id": 6,
			"name": "foxtrot_artist"
		}
	}
	sendData["genre"] = "pop_update"
	sendData["comment"] = "Kazoos make good swimmers update"
	sendData["primaryArtist"] = {
		"id": 10,
		"name": "juliet_artist"
	}
	sendData["stations"] = [
		{ "id": 2,
			"name": "papa_station",
			"displayName": "Come to papa"
		},
		{
			"id": 7,
			"name": "uniform_station",
			"displayName": "Asshole at the wheel"
		},
		{
			"id": 10,
			"name": "xray_station",
			"displayName": "Pentagular"
		}
	]
	sendData["artists"] = [
		{ "id": 9, "name": "india_artist" },
		{ "id": 13, "name": "november_artist" },
		{ "id": 3, "name": "charlie_artist" }
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
		s["isRunning"] = False
	mismatches = mismatched_properties(
		normalize_dict(data),
		normalize_dict(sendData)
	)
	assert not mismatches

def test_get_songs_for_multi_edit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	response = client.get(
		f"song-info/songs/multi/?id=2&id=3"
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
	assert data["primaryArtist"] == None
	assert "primaryArtist" in touched
	assert data["artists"] == [{ "id": 4, "name": "delta_artist"}]
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
	assert data["sampleRate"] == None
	assert "sampleRate" in touched
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
			"displayName": "Oscar the grouch",
			"isRunning": False
		}
	]
	assert "stations" in touched
	assert "touched" not in touched

def test_song_save_for_multi_edit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	headers = login_test_user("testUser_foxtrot", client)

	idList = "?id=10&id=4&id=17&id=11&id=15"

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
	assert len(set(d["primaryArtist"] for d in data0 if d["primaryArtist"])) == 0
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
	assert len(set(d["sampleRate"] for d in data0)) == 1
	assert len(set(d["comment"] for d in data0)) == 4
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 5

	sendData = {
		"album": {
			"id": 12, "name": "garoo_album"
		},
		"stations": [
			{
				"id": 6,
				"name": "yankee_station",
				"displayName": "Blurg the blergos"
			},
			{
				"id": 8,
				"name": "victor_station",
				"displayName": "Fat, drunk, and stupid"
			}
		],
		"primaryArtist": { "id": 14, "name": "oscar_artist" },
		"artists": [
			{ "id": 8, "name": "hotel_artist" },
			{ "id": 1, "name": "alpha_artist" }
		],
		"touched": ["album", "stations", "primaryArtist", "artists"]
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
	assert len(set(d["primaryArtist"]["id"] for d in data2
		if d["primaryArtist"])
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
	assert len(set(d["sampleRate"] for d in data2)) == 1
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
	headers = login_test_user("testUser_foxtrot", client)

	idList = "?id=29&id=28&id=27&id=26&id=25&id=24&id=23"

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
	assert len(set(d["primaryArtist"] for d in data0 if d["primaryArtist"])) == 0
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
	assert len(set(d["sampleRate"] for d in data0)) == 1
	assert len(set(d["comment"] for d in data0)) == 1
	assert len(set(d["duration"] for d in data0)) == 1
	assert len(set(d["explicit"] for d in data0)) == 1
	assert len(set(d["lyrics"] for d in data0)) == 1
	stationsLen = len(set(
		(*sorted(a["id"] for a in d["stations"]),)
		for d in data0 if d["stations"])
	)
	assert stationsLen == 2

	sendData = {
		"album": {
			"id": 12, "name": "garoo_album"
		},
		"stations": [
			{
				"id": 6,
				"name": "yankee_station",
				"displayName": "Blurg the blergos"
			},
			{
				"id": 8,
				"name": "victor_station",
				"displayName": "Fat, drunk, and stupid"
			},
		],
		"artists": [],
		"primaryArtist": { "id": 5, "name": "foxtrot_artist" },
		"touched": ["album", "stations", "primaryArtist", "artists"]
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
	assert len(set(d["primaryArtist"]["id"] for d in data2
		if d["primaryArtist"])
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
	assert len(set(d["sampleRate"] for d in data2)) == 1
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

