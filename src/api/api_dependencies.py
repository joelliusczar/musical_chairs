#pyright: reportMissingTypeStubs=false
from typing import Iterator, Tuple, Optional
from urllib import parse
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.engine import Connection
from musical_chairs_libs.services import (
	EnvManager,
	StationService,
	QueueService,
	SongInfoService,
	AccountsService,
	ProcessService
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	build_error_obj,
	StationUserInfo,
	seconds_to_tuple,
	build_timespan_msg,
	UserRoleDomain,
	IllegalOperationError,
	ActionRule,
	get_datetime
)
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose.exceptions import ExpiredSignatureError
from dataclasses import asdict

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="accounts/open",
	auto_error=False
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

def get_user_from_token_optional(
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service),
) -> Optional[AccountInfo]:
	try:
		user, _ = accountsService.get_user_from_token(token)
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

def get_user_from_token(
	token: str,
	accountsService: AccountsService
) -> Tuple[AccountInfo, float]:
	if not token:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=[build_error_obj("Not authenticated")],
			headers={"WWW-Authenticate": "Bearer"}
		)
	try:
		user, expiration = accountsService.get_user_from_token(token)
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail=[build_error_obj("Could not validate credentials")],
				headers={"WWW-Authenticate": "Bearer"}
			)
		return user, expiration
	except ExpiredSignatureError:
		raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail=[build_error_obj("Credentials are expired")],
				headers={
					"WWW-Authenticate": "Bearer",
					"X-AuthExpired": "true"
				}
			)


def get_current_user_simple(
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service),
	access_token: str = Cookie(default=None)
) -> AccountInfo:
	user, _ = get_user_from_token(
		token or parse.unquote(access_token or ""),
		accountsService
	)
	return user

def get_current_user(
	user: AccountInfo = Depends(get_current_user_simple)
) -> AccountInfo:
	return user

def get_station_user(
	securityScopes: SecurityScopes,
	stationId: Optional[int]=None,
	stationName: Optional[str]=None,
	user: AccountInfo = Depends(get_current_user_simple),
	stationService: StationService = Depends(station_service)
) -> StationUserInfo:
	if user.isAdmin:
		return StationUserInfo(**asdict(user))
	stationUser = stationService.get_station_user(user, stationId, stationName)
	scopes = (s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	)
	for scope in scopes:
		selectedRule = next(
			ActionRule.best_rules_generator(
				r for r in stationUser.roles if r.conforms(scope)
			),
			None
		)
		if selectedRule:
			try:
				whenNext = stationService.calc_when_user_can_next_do_action(
					user.id,
					selectedRule,
					stationId,
					stationName
				)
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise HTTPException(
					status_code=status.HTTP_429_TOO_MANY_REQUESTS,
					detail=[build_error_obj(
						"Please wait "
						f"{build_timespan_msg(seconds_to_tuple(int(timeleft)))} "
						"before trying again")
					]
				)
			except IllegalOperationError:
				raise HTTPException(
					status_code=status.HTTP_403_FORBIDDEN,
					detail=[build_error_obj(
						"Insufficient permissions to perform that action"
					)],
				)
		else:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=[build_error_obj(
					"Insufficient permissions to perform that action"
				)],
				headers={"WWW-Authenticate": "Bearer"}
			)
	return stationUser


def get_account_if_can_edit(
	userId: Optional[int]=None,
	username: Optional[str]=None,
	currentUser: AccountInfo = Depends(get_current_user_simple),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	if userId != currentUser.id and username != currentUser.username and\
		not currentUser.isAdmin:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=[build_error_obj(
				"Insufficient permissions to perform that action"
			)],
			headers={"WWW-Authenticate": "Bearer"}
		)
	prev = accountsService.get_account_for_edit(userId, username) \
		if userId or username else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev