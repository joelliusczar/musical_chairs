import pytest
import bcrypt
from musical_chairs_libs.dtos import AccountInfo
from datetime import datetime, timezone

@pytest.fixture
def test_password():
	return bcrypt.hashpw(b"testPassword", bcrypt.gensalt())

@pytest.fixture
def primary_user(test_password: bytes) -> AccountInfo:
	return AccountInfo(
		1,
		"testUser_alpha",
		test_password,
		email="test@test.com"
	)

@pytest.fixture
def test_date_ordered_list() -> list[datetime]:
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

def test_dates_ordered_fixture(test_date_ordered_list: list[datetime]):
	assert True