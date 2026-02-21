import pytest
from musical_chairs_libs.dtos_and_utilities import InternalUser
from datetime import datetime
from .mocks.constant_values_defs import\
mock_password,\
primary_user,\
mock_ordered_date_list



@pytest.fixture
def fixture_mock_password() -> bytes:
	return mock_password()


@pytest.fixture
def fixture_primary_user() -> InternalUser:
	return primary_user()


@pytest.fixture
def fixture_mock_ordered_date_list() -> list[datetime]:
	return mock_ordered_date_list
