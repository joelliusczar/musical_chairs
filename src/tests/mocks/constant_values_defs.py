from musical_chairs_libs.dtos_and_utilities import AccountInfo, hashpw
from datetime import datetime, timezone

def clear_mock_password() -> str:
	return "testPassword"

def mock_password() -> bytes:
	return hashpw(clear_mock_password().encode())

def clear_mock_bad_password_clear() -> str:
	return "badPassword"

def primary_user() -> AccountInfo:
	return AccountInfo(
		id=1,
		username="testUser_alpha",
		email="test@test.com"
	)

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