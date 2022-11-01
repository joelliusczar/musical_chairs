import copy
from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .helpers import normalize_dict



def test_song_ls_hit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	response = client.get(
		"/song-info/songs/tree")
	assert response.status_code == 200

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
	sendData["tags"] = [
		{ "id": 2, "name": "lima_tag" },
		{ "id": 7, "name": "romeo_tag" },
		{ "id": 10, "name": "uniform_tag" }
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
	data = normalize_dict(data)
	sendData = normalize_dict(sendData)
	assert data == sendData

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
	assert data["tags"] == [{ "id": 1, "name": "kilo_tag"}]
	assert "tags" in touched
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
	tagsLen = len(set(
		(*sorted(a["id"] for a in d["tags"]),)
		for d in data0 if d["tags"])
	)
	assert tagsLen == 5

	sendData = {
		"album": {
			"id": 12, "name": "garoo_album"
		},
		"tags": [
			{ "id": 6, "name": "papa_tag" },
			{ "id": 8, "name": "sierra_tag" }
		],
		"primaryArtist": { "id": 14, "name": "oscar_artist" },
		"artists": [
			{ "id": 8, "name": "hotel_artist" },
			{ "id": 1, "name": "alpha_artist" }
		],
		"touched": ["album", "tags", "primaryArtist", "artists"]
	}

	putResponse = client.put(
		f"song-info/songs/multi/{idList}",
		headers=headers,
		json=sendData
	)

	data1 = json.loads(putResponse.content)
	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)
	data2 = json.loads(getResponseAfter.content)
	assert getResponseAfter.status_code == 200
	data1_n = sorted((normalize_dict(d) for d in data1), key=lambda d: d["id"])
	data2_n = sorted((normalize_dict(d) for d in data2), key=lambda d: d["id"])
	assert data1_n == data2_n

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
	tagsLen = len(set(
		(*sorted(a["id"] for a in d["tags"]),)
		for d in data2 if d["tags"])
	)
	assert tagsLen == 1


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
	tagsLen = len(set(
		(*sorted(a["id"] for a in d["tags"]),)
		for d in data0 if d["tags"])
	)
	assert tagsLen == 2

	sendData = {
		"album": {
			"id": 12, "name": "garoo_album"
		},
		"tags": [
			{ "id": 6, "name": "papa_tag" },
			{ "id": 8, "name": "sierra_tag" }
		],
		"artists": [],
		"primaryArtist": { "id": 5, "name": "foxtrot_artist" },
		"touched": ["album", "tags", "primaryArtist", "artists"]
	}

	putResponse = client.put(
		f"song-info/songs/multi/{idList}",
		headers=headers,
		json=sendData
	)

	data1 = json.loads(putResponse.content)
	assert putResponse.status_code == 200

	getResponseAfter = client.get(
		f"song-info/songs/list/{idList}",
		headers=headers
	)
	data2 = json.loads(getResponseAfter.content)
	assert getResponseAfter.status_code == 200
	data1_n = sorted((normalize_dict(d) for d in data1), key=lambda d: d["id"])
	data2_n = sorted((normalize_dict(d) for d in data2), key=lambda d: d["id"])
	assert data1_n == data2_n

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
	tagsLen = len(set(
		(*sorted(a["id"] for a in d["tags"]),)
		for d in data2 if d["tags"])
	)
	assert tagsLen == 1

