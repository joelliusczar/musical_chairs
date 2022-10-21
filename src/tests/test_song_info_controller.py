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