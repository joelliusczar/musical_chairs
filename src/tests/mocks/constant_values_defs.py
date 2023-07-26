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

mock_ordered_date_list = [
		datetime( #0
			year=2021,
			month=5,
			day=27,
			hour=19,
			minute=13,
			tzinfo=timezone.utc
		),
		datetime( #1
			year=2022,
			month=5,
			day=27,
			hour=19,
			minute=13,
			tzinfo=timezone.utc
		),
		datetime( #2
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=10, #5min 1
			tzinfo=timezone.utc
		),
		datetime( #3
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=10,
			second=15, #5min 2
			tzinfo=timezone.utc
		),
		datetime( #4
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=10,
			second=20, #5min 3
			tzinfo=timezone.utc
		),
		datetime( #5
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=10,
			second=25, #5min 4
			tzinfo=timezone.utc
		),
		datetime( #6
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=13,
			second=7, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #7
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=14,
			second=7, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #8
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=14,
			second=30, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #9
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=14,
			second=45, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #10
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=14,
			second=55, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #11
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=14,
			second=59, #5min 5
			tzinfo=timezone.utc
		),
		datetime( #12
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=15,
			second=0, #5min 4 -> 5
			microsecond=10,
			tzinfo=timezone.utc
		),
		datetime( #13
			year=2023,
			month=2,
			day=11,
			hour=13,
			minute=15,
			second=14, #5min 5 -> 5
			tzinfo=timezone.utc
		)
	]


