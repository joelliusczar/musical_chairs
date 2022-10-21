from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient


def test_song_ls_hit(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	response = client.get(
		"/song-info/tree")
	assert response.status_code == 200