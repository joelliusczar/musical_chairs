#pyright: reportMissingTypeStubs=false
from typing import Iterator, Tuple, Optional, Iterable
from urllib import parse
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.engine import Connection
from musical_chairs_libs.services import (
	EnvManager,
	StationService,
	QueueService,
	SongInfoService,
	AccountsService,
	ProcessService,
	UserActionsHistoryService
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	build_error_obj,
	StationUserInfo,
	UserRoleDomain,
	IllegalOperationError,
	ActionRule,
	get_datetime,
	AbsorbentTrie,
	UserRoleDef,
	PathPrefixInfo,
	PathsActionRule
)
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose.exceptions import ExpiredSignatureError
from dataclasses import asdict
from api_error import (
	build_expired_error,
	build_not_logged_in_error,
	build_not_wrong_credentials_error,
	build_expired_credentials_error,
	build_wrong_permissions_error,
	build_too_many_requests_error
)

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

def user_actions_history_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> UserActionsHistoryService:
	return UserActionsHistoryService(conn)

def get_user_from_token_optional(
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service),
) -> Optional[AccountInfo]:
	try:
		user, _ = accountsService.get_user_from_token(token)
		return user
	except ExpiredSignatureError:
		raise build_expired_error()

def get_user_from_token(
	token: str,
	accountsService: AccountsService
) -> Tuple[AccountInfo, float]:
	if not token:
		raise build_not_logged_in_error()
	try:
		user, expiration = accountsService.get_user_from_token(token)
		if not user:
			raise build_not_wrong_credentials_error()
		return user, expiration
	except ExpiredSignatureError:
		raise build_expired_credentials_error()


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

def get_user_with_simple_scopes(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_simple)
) -> AccountInfo:
	if user.isAdmin:
		return user
	for scope in securityScopes.scopes:
		if not any(r for r in user.roles if r.name == scope):
			raise build_wrong_permissions_error()
	return user

def get_path_owner_roles() -> list[ActionRule]:
	return [
		ActionRule(UserRoleDef.PATH_EDIT.value, priority=2),
		ActionRule(UserRoleDef.PATH_DOWNLOAD.value, priority=2),
		ActionRule(UserRoleDef.PATH_LIST.value, priority=2),
		ActionRule(UserRoleDef.PATH_VIEW.value, priority=2)
	]

def get_paths_for_scopes(
	scopes: Iterable[str],
	pathRules: Iterable[PathPrefixInfo]
) -> Iterator[PathsActionRule]:
	scopes2Path = {s:PathsActionRule(s) for s in scopes}
	for r in ((p.path, rl) for p
		in pathRules for rl in p.rules if rl.name in scopes2Path
	):
		pathRule = scopes2Path[r[1].name]
		pathRule.paths.append(r[0])
	yield from (r for r in scopes2Path.values())


def check_if_can_use_path(
	scopes: Iterable[str],
	prefix: str,
	user: AccountInfo,
	userPrefixTrie: AbsorbentTrie[list[ActionRule]],
	userActionHistoryService: UserActionsHistoryService
):
	rules = userPrefixTrie.get(prefix, [])
	if user.dirRoot and prefix.startswith(user.dirRoot):
		rules.extend(get_path_owner_roles())
	if not rules:
		raise build_wrong_permissions_error()
	for scope in scopes:
		selectedRule = next(
			ActionRule.best_rules_generator(
				r for r in rules if r.conforms(scope)
			),
			None
		)
		if selectedRule:
			try:
				whenNext = userActionHistoryService.calc_when_user_can_next_do_action(
					user.id,
					selectedRule
				)
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise build_too_many_requests_error(int(timeleft))
			except IllegalOperationError:
				raise build_wrong_permissions_error()
		else:
			raise build_wrong_permissions_error()

def get_path_user(
	securityScopes: SecurityScopes,
	prefix: Optional[str]=None,
	itemId: Optional[int]=None,
	user: AccountInfo = Depends(get_current_user_simple),
	songInfoService: SongInfoService = Depends(song_info_service),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	userPrefixes = [*songInfoService.get_paths_user_can_see(user.id)]
	userPrefixTrie = AbsorbentTrie(((p.path, p.rules) for p in userPrefixes))
	if prefix == None:
		if itemId:
			prefix = next(songInfoService.get_song_path(itemId), "")
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	if prefix:
		check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie,
			userActionHistoryService
		)
		return user
	else:
		pathRuleMap = {p.name:p for p in get_paths_for_scopes(
			scopes,
			userPrefixes
		)}
		userDict = asdict(user)
		userDict["roles"] = [pathRuleMap.get(r.name, r) for r in user.roles]
		return AccountInfo(
			**userDict,
		)

def get_multi_path_user(
	securityScopes: SecurityScopes,
	itemIds: Iterable[int],
	user: AccountInfo = Depends(get_current_user_simple),
	songInfoService: SongInfoService = Depends(song_info_service),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	userPrefixes = songInfoService.get_paths_user_can_see(user.id)
	userPrefixTrie = AbsorbentTrie(((p.path, p.rules) for p in userPrefixes))
	prefixes = songInfoService.get_song_path(itemIds)
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	for prefix in prefixes:
		check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie,
			userActionHistoryService
		)
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
					raise build_too_many_requests_error(int(timeleft))
			except IllegalOperationError:
				raise build_wrong_permissions_error()
		else:
			raise build_wrong_permissions_error()
	return stationUser


def get_account_if_can_edit(
	userId: Optional[int]=None,
	username: Optional[str]=None,
	currentUser: AccountInfo = Depends(get_current_user_simple),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	if userId != currentUser.id and username != currentUser.username and\
		not currentUser.isAdmin:
		raise build_wrong_permissions_error()
	prev = accountsService.get_account_for_edit(userId, username) \
		if userId or username else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev