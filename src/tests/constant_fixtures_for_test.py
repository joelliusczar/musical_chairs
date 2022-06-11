import pytest
import bcrypt
from musical_chairs_libs.dtos import AccountInfo
from datetime import datetime, timezone

def mock_password() -> bytes:
	return bcrypt.hashpw(b"testPassword", bcrypt.gensalt())

def mock_bad_password() -> bytes:
	return bcrypt.hashpw(b"badPassword", bcrypt.gensalt())

@pytest.fixture
def fixture_mock_password() -> bytes:
	return mock_password()


def primary_user(mockPassword: bytes) -> AccountInfo:
	return AccountInfo(
		1,
		"testUser_alpha",
		mockPassword,
		email="test@test.com"
	)

@pytest.fixture
def fixture_primary_user(fixture_mock_password: bytes) -> AccountInfo:
	return primary_user(fixture_mock_password)

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

def test_dates_ordered_fixture(fixture_mock_ordered_date_list: list[datetime]):
	assert True