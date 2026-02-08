from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient
from .constant_fixtures_for_test import (
	fixture_primary_user as fixture_primary_user
)
from .mocks.db_population import get_initial_songs



def test_fetch_null_album(
	fixture_api_test_client: TestClient,
	fixture_primary_user: dtos.InternalUser,
):
	client = fixture_api_test_client

	headers = login_test_user(fixture_primary_user.username, client)

	response = client.get(
		"/albums/0",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)
	items = data.get("songs", [])
	noAlbumSongs = [s for s in get_initial_songs() if "albumfk" not in s]
	assert len(items) == len(noAlbumSongs)

def test_album_update(
	fixture_api_test_client: TestClient,
	fixture_primary_user: dtos.InternalUser,
):
	client = fixture_api_test_client

	headers = login_test_user(fixture_primary_user.username, client)

	response = client.get(
		"/albums/7",
		headers=headers
	)
	assert response.status_code == 200
	data = json.loads(response.content)

	data["versionnote"] = "from the bottom of my heart"

	putRespose = client.put(
		"/albums/7",
		headers=headers,
		json=data
	)
	data = json.loads(response.content)
	assert putRespose.status_code == 200


