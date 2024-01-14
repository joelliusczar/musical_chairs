#pyright: reportMissingTypeStubs=false
from typing import (
	Iterator,
	Tuple,
	Optional,
	Iterable,
	Union,
	Collection,
	Callable
)
from urllib import parse
from fastapi import (
	Depends,
	HTTPException,
	status,
	Query,
	Request,
	Path
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.services import (
	EnvManager,
	StationService,
	QueueService,
	SongInfoService,
	AccountsService,
	ProcessService,
	UserActionsHistoryService,
	SongFileService,
	PathRuleService,
)
from musical_chairs_libs.services.fs import (
	LocalFileService,
	FileServiceBase,
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
	StationInfo,
	int_or_str
)
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose.exceptions import ExpiredSignatureError
from api_error import (
	build_not_logged_in_error,
	build_not_wrong_credentials_error,
	build_expired_credentials_error,
	build_wrong_permissions_error,
	build_too_many_requests_error
)
from datetime import datetime


oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="accounts/open",
	auto_error=False
)


def subject_user_key_path(
	subjectuserkey: Union[int, str]  = Path()
) -> Union[int, str]:
	return int_or_str(subjectuserkey)

def subject_user_key_query(
	subjectuserkey: Union[int, str]  = Query()
) -> Union[int, str]:
	return int_or_str(subjectuserkey)

def owner_key_path(
	ownerkey: Union[int, str]  = Path()
) -> Union[int, str]:
	return int_or_str(ownerkey)

def owner_key_query(
	ownerkey: Union[int, str, None]  = Query(None)
) -> Union[int, str, None]:
	if ownerkey is None:
		return ownerkey
	return int_or_str(ownerkey)

def station_key_path(
	stationkey: Union[int, str]
) -> Union[int, str]:
	return int_or_str(stationkey)

def datetime_provider() -> Callable[[], datetime]:
	return get_datetime

def get_configured_db_connection(
	envManager: EnvManager=Depends(EnvManager)
) -> Iterator[Connection]:
	if not envManager:
		envManager = EnvManager()
	conn = envManager.get_configured_api_connection("musical_chairs_db")
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

def path_rule_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> PathRuleService:
	return PathRuleService(conn)

def file_service() -> FileServiceBase:
	return LocalFileService()

def song_file_service(
	conn: Connection=Depends(get_configured_db_connection),
	fileService: FileServiceBase=Depends(file_service)
) -> SongFileService:
	return SongFileService(conn, fileService)

def queue_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> QueueService:
	return QueueService(conn)

def accounts_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> AccountsService:
	return AccountsService(conn)

def process_service() -> ProcessService:
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

def __open_user_from_request__(
	userkey: Union[int, str, None],
	accountsService: AccountsService
) -> Optional[AccountInfo]:
	if userkey:
		try:
			userkey = int(userkey)
			owner = accountsService.get_account_for_edit(userkey)
		except:
			owner = accountsService.get_account_for_edit(userkey)
		if owner:
			return owner
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"User with key {userkey} not found")
			]
		)
	return None

def get_from_path_subject_user(
	subjectuserkey: Union[int, str] = Depends(subject_user_key_path),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	user = __open_user_from_request__(subjectuserkey, accountsService)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj("subjectuserkey missing")
			]
		)
	return user

def get_from_query_subject_user(
	subjectuserkey: Union[int, str] = Depends(subject_user_key_query),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	user = __open_user_from_request__(subjectuserkey, accountsService)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj("subjectuserkey missing")
			]
		)
	return user

def get_owner_from_query(
	ownerkey: Union[int, str, None] = Depends(owner_key_query),
	accountsService: AccountsService = Depends(accounts_service)
) -> Optional[AccountInfo]:
	return __open_user_from_request__(ownerkey, accountsService)


def get_owner_from_path(
	ownerkey: Union[int, str, None] = Depends(owner_key_path),
	accountsService: AccountsService = Depends(accounts_service)
) -> Optional[AccountInfo]:
	return __open_user_from_request__(ownerkey, accountsService)

def get_stations_by_ids(
	stationids: list[int]=Query(default=[]),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
) -> Collection[StationInfo]:
	if not stationids:
		return ()
	return list(stationService.get_stations(
		stationids,
		user=user
	))

def get_station_by_name_and_owner(
	stationkey: Union[int, str] = Depends(station_key_path),
	owner: Optional[AccountInfo] = Depends(get_owner_from_path),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	stationService: StationService = Depends(station_service),
) -> StationInfo:
	if type(stationkey) == str and not owner:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"owner for station with key {stationkey} not found"
			)]
		)
	#owner id is okay to be null if stationKey is an int
	ownerId = owner.id if owner else None
	station = next(stationService.get_stations(
		stationkey,
		ownerId=ownerId,
		user=user
	),None)
	if not station:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"station with key {stationkey} not found")
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
	if user.isadmin:
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
	if user.isadmin:
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
	impersonateduserid: Optional[int],
	user: AccountInfo = Depends(get_current_user_simple)
) -> Optional[int]:
	if user.isadmin or any(r.conforms(UserRoleDef.USER_IMPERSONATE.value) \
			for r in user.roles):
		return impersonateduserid
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


def get_path_rule_loaded_current_user(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_simple),
	pathRuleService: PathRuleService = Depends(path_rule_service)
) -> AccountInfo:
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	}
	if user.isadmin:
		return user
	if not scopes:
		raise build_wrong_permissions_error()
	rules = ActionRule.aggregate(
		user.roles,
		(p for p in pathRuleService.get_paths_user_can_see(user.id)),
		(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
	)
	roleNameSet = {r.name for r in rules}
	if any(s for s in scopes if s not in roleNameSet):
		raise build_wrong_permissions_error()
	userDict = user.model_dump()
	userDict["roles"] = rules
	resultUser = AccountInfo(
		**userDict,
	)
	return resultUser

def check_optional_path_for_current_user(
	securityScopes: SecurityScopes,
	prefix: Optional[str]=None,
	itemid: Optional[int]=None,
	user: AccountInfo = Depends(get_path_rule_loaded_current_user),
	songFileService: SongFileService = Depends(song_file_service),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isadmin:
		return user
	if prefix is None:
		if itemid:
			prefix = next(songFileService.get_song_path(itemid, False), "")
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
	itemids: list[int]=Query(default=[]),
	user: AccountInfo=Depends(get_path_rule_loaded_current_user),
	songFileService: SongFileService = Depends(song_file_service),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isadmin:
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
	prefixes = songFileService.get_song_path(itemids, False)
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
	if user.isadmin:
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
	userDict = user.model_dump()
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
	if user.isadmin:
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
	subjectuserkey: Union[int, str] = Depends(subject_user_key_path),
	currentUser: AccountInfo = Depends(get_current_user_simple),
	accountsService: AccountsService = Depends(accounts_service)
) -> AccountInfo:
	isCurrentUser = subjectuserkey == currentUser.id or\
		subjectuserkey == currentUser.username
	scopeSet = {s for s in securityScopes.scopes}
	hasEditRole = currentUser.isadmin or\
		any(r.name in scopeSet for r in currentUser.roles)
	if not isCurrentUser and not hasEditRole:
		raise build_wrong_permissions_error()
	prev = accountsService.get_account_for_edit(subjectuserkey) \
		if subjectuserkey else None
	if not prev:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj("Account not found")],
		)
	return prev

def get_prefix_if_owner(
	prefix: str,
	currentUser: AccountInfo = Depends(get_current_user_simple),
) -> str:
	if not currentUser.dirroot:
		raise build_wrong_permissions_error()
	normalizedPrefix = normalize_opening_slash(prefix)
	if not normalizedPrefix.startswith(
		normalize_opening_slash(currentUser.dirroot)
	):
		raise build_wrong_permissions_error()
	return prefix