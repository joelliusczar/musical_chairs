import pytest
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.simple_functions import hashpw
from datetime import datetime, timezone

def clear_mock_password() -> str:
	return "testPassword"

def mock_password() -> bytes:
	return hashpw(clear_mock_password().encode())

def clear_mock_bad_password_clear() -> str:
	return "badPassword"

@pytest.fixture
def fixture_mock_password() -> bytes:
	return mock_password()


def primary_user() -> AccountInfo:
	return AccountInfo(
		id=1,
		username="testUser_alpha",
		email="test@test.com"
	)

@pytest.fixture
def fixture_primary_user() -> AccountInfo:
	return primary_user()

def mock_ordered_date_list() -> list[datetime]:
	return [
		datetime(
			year=2021,
			month=5,
			day=27,
			hour=19,
			minute=13,
			tzinfo=timezone.utc
		),
		datetime(
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=13,
			tzinfo=timezone.utc
		)
	]

@pytest.fixture
def fixture_mock_ordered_date_list() -> list[datetime]:
	return mock_ordered_date_list()
