#pyright: reportMissingTypeStubs=false
from typing import Iterator, Tuple, Optional, Iterable, Union, Collection
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
	ActionRule,
	get_datetime,
	get_path_owner_roles,
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

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="accounts/open",
	auto_error=False
)


def get_configured_db_connection(
	envManager: EnvManager=Depends(EnvManager)
) -> Iterator[Connection]:
	if not envManager:
		envManager = EnvManager()
	conn = envManager.get_configured_db_connection()
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
	return ProcessService()

def user_actions_history_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> UserActionsHistoryService:
	return UserActionsHistoryService(conn)

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

def get_subject_user(
	subjectUserKey: Union[int, str] = Query(None),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
		try:
			subjectUserKey = int(subjectUserKey)
			owner = accountsService.get_account_for_edit(subjectUserKey)
		except:
			owner = accountsService.get_account_for_edit(subjectUserKey)
		if owner:
			return owner
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"User with key {subjectUserKey} not found")
			]
		)

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

def get_stations_by_ids(
	stationIds: list[int]=Query(default=[]),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
) -> Collection[StationInfo]:
	if not stationIds:
		return ()
	return list(stationService.get_stations(
		stationIds,
		user=user
	))

def get_station_by_name_and_owner(
	stationKey: Union[int, str],
	owner: Optional[AccountInfo] = Depends(get_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
) -> StationInfo:
	if type(stationKey) == str and not owner:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"owner for station with key {stationKey} not found"
			)]
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
	scopeSet = set(securityScopes.scopes)
	rules = ActionRule.sorted((r for r in user.roles if r.name in scopeSet))
	if not rules:
		raise build_wrong_permissions_error()
	timeoutLookup = \
		userActionHistoryService.calc_lookup_for_when_user_can_next_do_action(
			user.id,
			rules
		)
	for scope in scopeSet:
		if scope in timeoutLookup:
			whenNext = timeoutLookup[scope]
			if whenNext is None:
				raise build_wrong_permissions_error()
			if whenNext > 0:
				currentTimestamp = get_datetime().timestamp()
				timeleft = whenNext - currentTimestamp
				raise build_too_many_requests_error(int(timeleft))
	return user

def impersonated_user_id(
	impersonatedUserId: Optional[int],
	user: AccountInfo = Depends(get_current_user_simple)
) -> Optional[int]:
	if user.isAdmin or any(r.conforms(UserRoleDef.USER_IMPERSONATE.value) \
			for r in user.roles):
		return impersonatedUserId
	return None

def check_if_can_use_path(
	scopes: Iterable[str],
	prefix: str,
	user: AccountInfo,
	userPrefixTrie: ChainedAbsorbentTrie[ActionRule],
	userActionHistoryService: UserActionsHistoryService
):
	scopeSet = set(scopes)
	rules = ActionRule.sorted(
		(r for i in userPrefixTrie.values(normalize_opening_slash(prefix)) \
			for r in i if r.name in scopeSet)
	)
	if not rules:
		raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=[build_error_obj(f"{prefix} not found")
					]
				)
	timeoutLookup = \
		userActionHistoryService.calc_lookup_for_when_user_can_next_do_action(
			user.id,
			rules
		)
	for scope in scopeSet:
		if scope in timeoutLookup:
			whenNext = timeoutLookup[scope]
			if whenNext is None:
				raise build_wrong_permissions_error()
			if whenNext > 0:
				currentTimestamp = get_datetime().timestamp()
				timeleft = whenNext - currentTimestamp
				raise build_too_many_requests_error(int(timeleft))


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
		(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
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
			if type(r) == ActionRule \
				and (UserRoleDomain.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
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
		if type(r) == ActionRule \
			and (UserRoleDomain.Path.conforms(r.name) \
					or r.name == UserRoleDef.ADMIN.value
			)
	), shouldEmptyUpdateTree=False)
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


def get_station_user(
	securityScopes: SecurityScopes,
	station: StationInfo=Depends(get_station_by_name_and_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
) -> Optional[AccountInfo]:
	minScope = (not securityScopes.scopes or\
		securityScopes.scopes[0] == UserRoleDef.STATION_VIEW.value
	)
	if not station.viewsecuritylevel and minScope:
		return user
	if not user:
		raise build_not_logged_in_error()
	if user.isAdmin:
		return user
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	}
	rules = ActionRule.aggregate(
		station.rules,
		filter=lambda r: r.name in scopes
	)
	if not rules:
		raise build_wrong_permissions_error()
	timeoutLookup = \
		userActionHistoryService\
		.calc_lookup_for_when_user_can_next_do_station_action(
			user.id,
			(station,)
		).get(station.id, {})
	for scope in scopes:
		if scope in timeoutLookup:
			whenNext = timeoutLookup[scope]
			if whenNext is None:
				raise build_wrong_permissions_error()
			if whenNext > 0:
				currentTimestamp = get_datetime().timestamp()
				timeleft = whenNext - currentTimestamp
				raise build_too_many_requests_error(int(timeleft))
	userDict = asdict(user)
	userDict["roles"] = rules
	return AccountInfo(**userDict)

def get_station_user_2(
	securityScopes: SecurityScopes,
	stations: Collection[StationInfo]=Depends(get_stations_by_ids),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
) -> Optional[AccountInfo]:
	minScope = (not securityScopes.scopes or\
		securityScopes.scopes[0] == UserRoleDef.STATION_VIEW.value
	)
	if not any(s.viewsecuritylevel for s in stations) and minScope:
		return user
	if not user:
		raise build_not_logged_in_error()
	if user.isAdmin:
		return user
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	}
	unpermittedStations = [s for s in stations
		if not any(r.name in scopes for r in s.rules)
	]
	if unpermittedStations:
		raise build_wrong_permissions_error()
	timeoutLookup = \
		userActionHistoryService\
		.calc_lookup_for_when_user_can_next_do_station_action(
			user.id,
			stations
		)
	for station in stations:
		for scope in scopes:
			if station.id in timeoutLookup and scope in timeoutLookup[station.id]:
				whenNext = timeoutLookup[station.id][scope]
				if whenNext is None:
					raise build_wrong_permissions_error()
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise build_too_many_requests_error(int(timeleft))
	return user

def get_account_if_has_scope(
	securityScopes: SecurityScopes,
	subjectUserKey: Union[int, str],
	currentUser: AccountInfo = Depends(get_current_user_simple),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	isCurrentUser = subjectUserKey == currentUser.id or\
		subjectUserKey == currentUser.username
	scopeSet = {s for s in securityScopes.scopes}
	hasEditRole = currentUser.isAdmin or\
		any(r.name in scopeSet for r in currentUser.roles)
	if not isCurrentUser and not hasEditRole:
		raise build_wrong_permissions_error()
	prev = accountsService.get_account_for_edit(subjectUserKey) if subjectUserKey else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev

