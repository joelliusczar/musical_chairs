#pyright: reportMissingTypeStubs=false
from typing import Iterator
from fastapi import Depends, HTTPException, status

from sqlalchemy.engine import Connection
from musical_chairs_libs.services import\
	EnvManager,\
	HistoryService,\
	StationService,\
	QueueService,\
	SongInfoService,\
	AccountsService,\
	ProcessService
from musical_chairs_libs.dtos_and_utilities import\
	AccountInfo,\
	build_error_obj,\
	seconds_to_tuple,\
	build_timespan_msg,\
	UserRoleDef
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose.exceptions import ExpiredSignatureError

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

def song_info_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> SongInfoService:
	return SongInfoService(conn)

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

def process_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> ProcessService:
	return ProcessService(conn)

def get_current_user_base(
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	try:
		user = accountsService.get_user_from_token(token)
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail=[build_error_obj("Could not validate credentials")],
				headers={"WWW-Authenticate": "Bearer"}
			)
		return user
	except ExpiredSignatureError:
		raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail=[build_error_obj("Credentials are expired")],
				headers={
					"WWW-Authenticate": "Bearer",
					"X-AuthExpired": "true"
				}
			)

def time_til_user_can_do_action(
	user: AccountInfo,
	role: UserRoleDef,
	accountsService: AccountsService
) -> int:
	if not user:
		return -1
	if user.isAdmin:
		return 0
	requestRoles = [r for r in user.roles \
		if r.startswith(role())]
	if not any(requestRoles):
		return -1
	timeout = min([UserRoleDef.extract_role_segments(r)[1] for r \
		in requestRoles]) * 60
	lastRequestedTimestamp = 0
	if role == UserRoleDef.STATION_REQUEST:
		lastRequestedTimestamp = accountsService.last_request_timestamp(user)
	timeLeft = lastRequestedTimestamp + timeout - accountsService\
		.get_datetime().timestamp()
	return int(timeLeft) if timeLeft > 0 else 0


def get_current_user(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_base),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	roleMap = {r():r for r in UserRoleDef}
	roleModSet = {UserRoleDef.extract_role_segments(r)[0] for r in user.roles}
	for scope in securityScopes.scopes:
		if scope in roleModSet:
			timeleft = time_til_user_can_do_action(
				user,
				roleMap[scope],
				accountsService
			)
			if timeleft:
				raise HTTPException(
					status_code=status.HTTP_429_TOO_MANY_REQUESTS,
					detail=[build_error_obj(
						f"Please wait {build_timespan_msg(seconds_to_tuple(timeleft))} "
						"before trying again")
					]
				)
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