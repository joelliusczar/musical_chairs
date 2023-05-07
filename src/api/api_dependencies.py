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
	UserRoleDef,
	PathsActionRule,
	ChainedAbsorbentTrie
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
from itertools import chain, groupby

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

def get_path_owner_roles(ownerDir: str) -> Iterator[PathsActionRule]:
		yield PathsActionRule(
			UserRoleDef.PATH_LIST.value,
			priority=2,
			path=ownerDir
		)
		yield PathsActionRule(
			UserRoleDef.PATH_VIEW.value,
			priority=2,
			path=ownerDir
		)
		yield PathsActionRule(
			UserRoleDef.PATH_EDIT.value,
			priority=2,
			path=ownerDir
		)
		yield PathsActionRule(
			UserRoleDef.PATH_DOWNLOAD.value,
			priority=2,
			path=ownerDir
		)

def check_if_can_use_path(
	scopes: Iterable[str],
	prefix: str,
	user: AccountInfo,
	userPrefixTrie: ChainedAbsorbentTrie[ActionRule],
	userActionHistoryService: UserActionsHistoryService
):
	rules = sorted(r for i in userPrefixTrie.values(prefix) for r in i)
	if not rules:
		raise build_wrong_permissions_error()
	for scope in scopes:
		bestRuleGenerator = (r for g in
			groupby(
				(r for r in rules if r.conforms(scope)),
				lambda k: k.name
			) for r in g[1]
		)
		selectedRule = next(
			bestRuleGenerator,
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
	user: AccountInfo = Depends(get_current_user_simple),
	songInfoService: SongInfoService = Depends(song_info_service)
) -> AccountInfo:
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	}
	if user.isAdmin:
		return user
	if not scopes:
		raise build_wrong_permissions_error()
	roles = sorted(r for r in chain(
		(p for p in songInfoService.get_paths_user_can_see(user.id)),
		(p for p in get_path_owner_roles(user.dirRoot)) if user.dirRoot else ()
	) if r.name in scopes)
	roleNameSet = {r.name for r in roles}
	if any(s for s in scopes if s not in roleNameSet):
		raise build_wrong_permissions_error()
	userDict = asdict(user)
	userDict["roles"] = roles
	return AccountInfo(
		**userDict,
	)

def get_path_user_and_check_optional_path(
	securityScopes: SecurityScopes,
	prefix: Optional[str]=None,
	itemId: Optional[int]=None,
	user: AccountInfo = Depends(get_path_user),
	songInfoService: SongInfoService = Depends(song_info_service),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	if prefix == None:
		if itemId:
			prefix = next(songInfoService.get_song_path(itemId), "")
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	if prefix:
		userPrefixes = (
			r for r in user.roles if isinstance(r, PathsActionRule)
		)

		userPrefixTrie = ChainedAbsorbentTrie[ActionRule](
			(p.path, p) for p in userPrefixes if p.path
		)
		check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie,
			userActionHistoryService
		)
	return user

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
	userPrefixTrie = ChainedAbsorbentTrie[ActionRule](
			(p.path, p) for p in userPrefixes if p.path
		)
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
	scopes = (s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	)
	if not scopes:
		raise build_wrong_permissions_error()
	if user.isAdmin:
		return StationUserInfo(**asdict(user))
	stationUser = stationService.get_station_user(user, stationId, stationName)
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