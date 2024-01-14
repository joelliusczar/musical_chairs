from .api_test_dependencies import\
	fixture_api_test_client as fixture_api_test_client
from .api_test_dependencies import *
from fastapi.testclient import TestClient


def test_open_api(
	fixture_api_test_client: TestClient
):
	client = fixture_api_test_client
	response = client.get(
		"/openapi.json"
	)
	# data = json.loads(response.content)
	assert response.status_code == 200