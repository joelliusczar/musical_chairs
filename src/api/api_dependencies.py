#pyright: reportMissingTypeStubs=false
from typing import Iterator
from fastapi import Depends, HTTPException, status

from sqlalchemy.engine import Connection
from musical_chairs_libs.env_manager import EnvManager
from musical_chairs_libs.history_service import HistoryService
from musical_chairs_libs.station_service import StationService
from musical_chairs_libs.queue_service import QueueService
from musical_chairs_libs.accounts_service import AccountsService, UserRoleDef
from musical_chairs_libs.dtos import AccountInfo
from musical_chairs_libs.simple_functions import build_error_obj
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="accounts/open"
)

def get_configured_db_connection(
	envManager: EnvManager=Depends(EnvManager)
) -> Iterator[Connection]:
	if not envManager:
		envManager = EnvManager()
	conn = envManager.get_configured_db_connection(checkSameThread=False)
	try:
		yield conn
	finally:
		conn.close()

def station_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationService:
	return StationService(conn)

def history_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> HistoryService:
	return HistoryService(conn)

def queue_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> QueueService:
	return QueueService(conn)

def accounts_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> AccountsService:
	return AccountsService(conn)

def get_current_user_base(
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	user = accountsService.get_user_from_token(token)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=[build_error_obj("Could not validate credentials")],
			headers={"WWW-Authenticate": "Bearer"}
		)
	return user

def get_current_user(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_base),
) -> AccountInfo:
	if user.isAdmin:
		return user
	for scope in securityScopes.scopes:
		if scope in map(
			lambda r: UserRoleDef.extract_role_segments(r)[0],
			user.roles
		):
			break
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=[build_error_obj(
				"Insufficient permissions to perform that action"
			)],
			headers={"WWW-Authenticate": "Bearer"}
		)
	return user


def get_account_if_can_edit(
	userId: int,
	currentUser: AccountInfo = Depends(get_current_user_base),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	if userId != currentUser.id and not currentUser.isAdmin:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=[build_error_obj(
				"Insufficient permissions to perform that action"
			)],
			headers={"WWW-Authenticate": "Bearer"}
		)
	prev = accountsService.get_account_for_edit(userId) if userId else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev