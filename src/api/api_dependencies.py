#pyright: reportMissingTypeStubs=false
from typing import Iterator, Tuple, Optional, Iterable, Union, cast
from urllib import parse
from fastapi import Depends, HTTPException, status, Query, Request
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
	UserRoleDomain,
	IllegalOperationError,
	ActionRule,
	get_datetime,
	get_path_owner_roles,
	get_station_owner_rules,
	PathsActionRule,
	ChainedAbsorbentTrie,
	normalize_opening_slash,
	UserRoleDef,
	StationInfo
)
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose.exceptions import ExpiredSignatureError
from dataclasses import asdict
from api_error import (
	build_not_logged_in_error,
	build_not_wrong_credentials_error,
	build_expired_credentials_error,
	build_wrong_permissions_error,
	build_too_many_requests_error
)
from itertools import groupby

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

def get_optional_user_from_token(
	request: Request,
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service),
) -> Optional[AccountInfo]:
	cookieToken = request.cookies.get("access_token", None)
	if not token and not cookieToken:
		return None
	try:
		user, _ = accountsService.get_user_from_token(
			token or parse.unquote(cookieToken or "")
		)
		return user
	except ExpiredSignatureError:
		return None

def get_owner(
	ownerKey: Union[int, str, None] = Query(None),
	accountsService: AccountsService = Depends(accounts_service)
) -> Optional[AccountInfo]:
	if ownerKey:
		try:
			ownerKey = int(ownerKey)
			owner = accountsService.get_account_for_edit(ownerKey)
		except:
			owner = accountsService.get_account_for_edit(ownerKey)
		if owner:
			return owner
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"User with key {ownerKey} not found")
			]
		)
	return None


def get_station_by_name_and_owner(
	stationKey: Union[int, str],
	owner: Optional[AccountInfo] = Depends(get_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
) -> StationInfo:
	if type(stationKey) == str and not owner:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"user with key {stationKey} not found")
			]
		)
	#owner id is okay to be null if stationKey is an int
	ownerId = owner.id if owner else None
	station = next(stationService.get_stations(
		stationKey,
		ownerId=ownerId,
		user=user
	),None)
	if not station:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"station with key {stationKey} not found")
			]
		)
	return station

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
	request: Request,
	token: str = Depends(oauth2_scheme),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	cookieToken = request.cookies.get("access_token", None)
	user, _ = get_user_from_token(
		token or parse.unquote(cookieToken or ""),
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

def get_user_with_rate_limited_scope(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_simple),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	for scope in securityScopes.scopes:
		check_scope(
			scope,
			user,
			ActionRule.sorted(user.roles),
			userActionHistoryService
		)
	return user

def impersonated_user_id(
	impersonatedUserId: Optional[int],
	user: AccountInfo = Depends(get_current_user_simple)
) -> Optional[int]:
	if user.isAdmin or any(r.conforms(UserRoleDef.USER_IMPERSONATE.value) \
			for r in user.roles):
		return impersonatedUserId
	return None

def check_scope(
	scope: str,
	user: AccountInfo,
	rules: Iterable[ActionRule],
	userActionHistoryService: UserActionsHistoryService
):
	selectedRule = next(
		(r for r in ActionRule.filter_out_repeat_roles(rules) \
			if r.conforms(scope)),
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

def check_if_can_use_path(
	scopes: Iterable[str],
	prefix: str,
	user: AccountInfo,
	userPrefixTrie: ChainedAbsorbentTrie[ActionRule],
	userActionHistoryService: UserActionsHistoryService
):
	rules = ActionRule.sorted(
		(r for i in userPrefixTrie.values(normalize_opening_slash(prefix)) \
			for r in i)
	)
	if not rules:
		raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=[build_error_obj(f"{prefix} not found")
					]
				)
	for scope in scopes:
		check_scope(scope, user, rules, userActionHistoryService)


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
	rules = ActionRule.aggregate(
		user.roles,
		(p for p in songInfoService.get_paths_user_can_see(user.id)),
		(p for p in get_path_owner_roles(normalize_opening_slash(user.dirRoot)))
	)
	roleNameSet = {r.name for r in rules}
	if any(s for s in scopes if s not in roleNameSet):
		raise build_wrong_permissions_error()
	userDict = asdict(user)
	userDict["roles"] = rules
	resultUser = AccountInfo(
		**userDict,
	)
	return resultUser

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
	if prefix is None:
		if itemId:
			prefix = next(songInfoService.get_song_path(itemId, False), "")
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
		userPrefixTrie.add("", (r for r in user.roles \
			if not isinstance(r, PathsActionRule) or not r.path))
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
	itemIds: list[int]=Query(default=[]),
	user: AccountInfo=Depends(get_path_user),
	songInfoService: SongInfoService = Depends(song_info_service),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isAdmin:
		return user
	userPrefixes = (
		r for r in user.roles if isinstance(r, PathsActionRule)
	)
	userPrefixTrie = ChainedAbsorbentTrie[ActionRule](
			(p.path, p) for p in userPrefixes if p.path
		)
	userPrefixTrie.add("", (r for r in user.roles \
			if not isinstance(r, PathsActionRule) or not r.path))
	prefixes = songInfoService.get_song_path(itemIds, False)
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



def __filter_station_rules__(
	scopes: Iterable[str],
	station: StationInfo,
	rules: Iterable[ActionRule],
	ruleDef: UserRoleDef,
	stationAttr: str
) -> Iterator[ActionRule]:
	secLevel = cast(int, getattr(station, stationAttr)) or 0
	if not secLevel:
		yield from rules
		return
	if not any(s == ruleDef.value for s in scopes):
		yield from rules
		return
	for rule in rules:
		if rule.name != ruleDef.value:
			yield rule
			continue
		#shouldn't be any rules for other stations at this point
		if secLevel < rule.priority:
			yield rule
			continue

def get_station_user(
	securityScopes: SecurityScopes,
	station: StationInfo=Depends(get_station_by_name_and_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service)
) -> Optional[AccountInfo]:
	minScope = (not securityScopes.scopes or\
		securityScopes.scopes[0] == UserRoleDef.STATION_VIEW.value
	)
	if not station.viewSecurityLevel and minScope:
		return user
	if not user:
		raise build_not_logged_in_error()
	if user.isAdmin:
		return user
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	]
	sortedRules = ActionRule.aggregate(
		user.roles,
		get_station_owner_rules() \
			if station.owner and user.id == station.owner.id else (),
		stationService.get_station_rules(user.id, station.id, scopes)
	)
	stationFiltered = sortedRules
	for pair in [
		(UserRoleDef.STATION_REQUEST, "requestSecurityLevel"),
		(UserRoleDef.STATION_VIEW, "viewSecurityLevel")
	]:
		stationFiltered = __filter_station_rules__(
			scopes,
			station,
			stationFiltered,
			pair[0],
			pair[1]
		)
	rules = [*ActionRule.filter_out_repeat_roles(
		stationFiltered
	)]
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
				whenNext = stationService.calc_when_user_can_next_do_action(
					user.id,
					selectedRule,
					station.id
				)
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise build_too_many_requests_error(int(timeleft))
			except IllegalOperationError:
				raise build_wrong_permissions_error()
		else:
			raise build_wrong_permissions_error()
	userDict = asdict(user)
	userDict["roles"] = rules
	return AccountInfo(**userDict)


def get_account_if_can_edit(
	userKey: Union[int, str],
	currentUser: AccountInfo = Depends(get_current_user_simple),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	if userKey != currentUser.id and userKey != currentUser.username and\
		not currentUser.isAdmin:
		raise build_wrong_permissions_error()
	prev = accountsService.get_account_for_edit(userKey) if userKey else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev

