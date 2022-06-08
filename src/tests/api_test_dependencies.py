from datetime import datetime
from typing import List
from fastapi import Depends
from .constant_fixtures_for_test import\
	mock_ordered_date_list,\
	mock_password,\
	primary_user
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.env_manager import EnvManager
from .mocks.mock_db_constructors import construct_mock_connection_constructor

def mock_depend_primary_user(mockPassword: bytes = Depends(mock_password)):
	return primary_user(mockPassword)

def mock_depend_env_manager(
	orderedDateList: List[datetime] = Depends(mock_ordered_date_list),
	primaryUser: AccountInfo = Depends(mock_depend_primary_user),
	mockPassword: bytes = Depends(mock_password)
) -> EnvManager:
	envMgr = EnvManager()
	envMgr.get_configured_db_connection = \
		construct_mock_connection_constructor(
			orderedDateList,
			primaryUser,
			mockPassword
		)
	return envMgr