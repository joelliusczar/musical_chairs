#pyright: reportMissingTypeStubs=false
import ipaddress
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
	Path,
	Header
)
from sqlalchemy.engine import Connection
from musical_chairs_libs.services import (
	StationService,
	QueueService,
	SongInfoService,
	AccountsService,
	ProcessService,
	UserActionsHistoryService,
	SongFileService,
	PathRuleService,
	ArtistService,
	AlbumService,
	JobsService,
	PlaylistService,
	PlaylistsUserService,
	PlaylistsSongsService,
	StationsPlaylistsService,
	StationsSongsService,
	StationsUsersService,
	AlbumQueueService,
	StationProcessService,
	PlaylistQueueService,
	CollectionQueueService,
	CurrentUserProvider,
)
from musical_chairs_libs.protocols import (
	FileService,
	RadioPusher
)
from musical_chairs_libs.services.fs import (
	S3FileService
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	build_error_obj,
	ConfigAcessors,
	UserRoleDomain,
	ActionRule,
	get_datetime,
	get_path_owner_roles,
	PathsActionRule,
	ChainedAbsorbentTrie,
	normalize_opening_slash,
	UserRoleDef,
	StationInfo,
	int_or_str,
	DirectoryTransfer,
	TrackingInfo,
	PlaylistInfo,
)
from musical_chairs_libs.dtos_and_utilities.constants import (
	StationRequestTypes,
	StationTypes,
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
from base64 import urlsafe_b64decode



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

def playlist_key_path(
	playlistkey: Union[int, str]
) -> Union[int, str]:
	return int_or_str(playlistkey)

def datetime_provider() -> Callable[[], datetime]:
	return get_datetime


def get_configured_db_connection(
	envManager: ConfigAcessors=Depends(ConfigAcessors)
) -> Iterator[Connection]:
	if not envManager:
		envManager = ConfigAcessors()
	conn = envManager.get_configured_api_connection("musical_chairs_db")
	try:
		yield conn
	finally:
		conn.close()


def station_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationService:
	return StationService(conn)


def station_process_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationProcessService:
	return StationProcessService(conn)


def stations_songs_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationsSongsService:
	return StationsSongsService(conn)


def stations_playlists_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationsPlaylistsService:
	return StationsPlaylistsService(conn)


def stations_users_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> StationsUsersService:
	return StationsUsersService(conn)


def playlist_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> PlaylistService:
	return PlaylistService(conn)


def playlists_users_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> PlaylistsUserService:
	return PlaylistsUserService(conn)


def song_info_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> SongInfoService:
	return SongInfoService(conn)


def artist_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> ArtistService:
	return ArtistService(conn)


def album_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> AlbumService:
	return AlbumService(conn)


def path_rule_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> PathRuleService:
	return PathRuleService(conn)


def file_service() -> FileService:
	return S3FileService()


def song_file_service(
	conn: Connection=Depends(get_configured_db_connection),
	fileService: FileService=Depends(file_service)
) -> SongFileService:
	return SongFileService(conn, fileService)


def job_service(
	conn: Connection=Depends(get_configured_db_connection),
	fileService: FileService=Depends(file_service)
) -> JobsService:
	return JobsService(conn, fileService)


def queue_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> QueueService:
	return QueueService(conn)


def album_queue_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> AlbumQueueService:
	return AlbumQueueService(conn)


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


def get_optional_prefix(
	prefix: Optional[str]=Query(None),
	nodeId: Optional[str]=Query(None)
) -> Optional[str]:
	if prefix is not None:
		return prefix
	if nodeId is not None:
		translated = nodeId
		decoded = urlsafe_b64decode(translated).decode()
		return decoded


def get_prefix(
	prefix: Optional[str]=Query(None),
	nodeId: Optional[str]=Query(None)
) -> str:
	prefix = get_optional_prefix(prefix, nodeId)
	if prefix is not None:
		return prefix
	raise HTTPException(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		detail=[build_error_obj("prefix and nodeId both missing")
		]
	)


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
		raise build_expired_credentials_error()


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


def get_station_by_id(
		stationid: int=Path(),
		stationService: StationService = Depends(station_service),
) -> StationInfo:
	station = next(stationService.get_stations(stationKeys=stationid), None)
	if not station:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"station not found for id {stationid}"
			)]
		)
	return station


def get_playlist_by_id(
		playlistid: int=Path(),
		playlistService: PlaylistService = Depends(playlist_service),
) -> PlaylistInfo:
	playlist = next(playlistService.get_playlists(playlistKeys=playlistid), None)
	if not playlist:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"station not found for id {playlistid}"
			)]
		)
	return playlist


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


def get_playlist_by_name_and_owner(
	playlistkey: Union[int, str] = Depends(playlist_key_path),
	owner: Optional[AccountInfo] = Depends(get_owner_from_path),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	playlistService: PlaylistService = Depends(playlist_service),
) -> PlaylistInfo:
	if type(playlistkey) == str and not owner:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"owner for station with key {playlistkey} not found"
			)]
		)
	#owner id is okay to be null if stationKey is an int
	ownerId = owner.id if owner else None
	playlist = next(playlistService.get_playlists(
		playlistkey,
		ownerId=ownerId,
		user=user
	),None)
	if not playlist:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"station with key {playlistkey} not found")
			]
		)
	return playlist


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

def station_radio_pusher(
	station: StationInfo = Depends(get_station_by_name_and_owner),
	conn: Connection = Depends(get_configured_db_connection)
) -> RadioPusher:
	if station.typeid == StationTypes.SONGS_ONLY.value:
		return QueueService(conn)
	if station.typeid == StationTypes.ALBUMS_ONLY.value:
		return AlbumQueueService(conn)
	if station.typeid == StationTypes.PLAYLISTS_ONLY.value:
		return PlaylistQueueService(conn)
	if station.typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value:
		return CollectionQueueService(conn)
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[build_error_obj(f"Station type: {station.typeid} not found")
		]
	)

def validated_station_request_type(
	requesttypeid: int = Path(),
	radioPusher: RadioPusher = Depends(station_radio_pusher)
) -> StationRequestTypes:
	requestType = StationRequestTypes(requesttypeid)
	if requestType not in radioPusher.accepted_request_types():
		raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{requestType.name} cannot be requested of that station"
					)
				]
			)
	return requestType


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
	userPrefixTrie: ChainedAbsorbentTrie[PathsActionRule],
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
	prefix: Optional[str]=Depends(get_optional_prefix),
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
			prefix = next(songFileService.get_song_path(itemid), "")
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	if prefix:

		userPrefixTrie = user.get_permitted_paths_tree()
		check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie,
			userActionHistoryService
		)
	return user


def check_directory_transfer(
	transfer: DirectoryTransfer,
	user: AccountInfo = Depends(get_path_rule_loaded_current_user),
	userActionHistoryService: UserActionsHistoryService =
		Depends(user_actions_history_service)
) -> AccountInfo:
	if user.isadmin:
		return user
	userPrefixTrie = user.get_permitted_paths_tree()
	scopes = (
		(transfer.path, UserRoleDef.PATH_DELETE),
		(transfer.newprefix, UserRoleDef.PATH_EDIT)
	)

	for path, scope in scopes:
		check_if_can_use_path(
			[scope.value],
			path,
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
	userPrefixTrie = user.get_permitted_paths_tree()
	prefixes = songFileService.get_song_path(itemids)
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

filter_permitter_query_songs = get_multi_path_user

def __get_station_user__(
	securityScopes: SecurityScopes,
	station: StationInfo,
	user: Optional[AccountInfo],
	userActionHistoryService: UserActionsHistoryService
)-> Optional[AccountInfo]:
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


def get_station_user_by_id(
	securityScopes: SecurityScopes,
	station: StationInfo=Depends(get_station_by_id),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
)-> Optional[AccountInfo]:
	return __get_station_user__(
		securityScopes,
		station,
		user,
		userActionHistoryService
	)


def get_station_user(
	securityScopes: SecurityScopes,
	station: StationInfo=Depends(get_station_by_name_and_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
	userActionHistoryService: UserActionsHistoryService=
		Depends(user_actions_history_service)
) -> Optional[AccountInfo]:
	return __get_station_user__(
		securityScopes,
		station,
		user,
		userActionHistoryService
	)


def get_multi_station_user(
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
	prefix: str=Depends(get_prefix),
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


def get_page_num(
	page: int = 1,
) -> int:
	if page > 0:
		page -= 1
	return page


def user_for_filters(
	securityScopes: SecurityScopes,
	user: AccountInfo = Depends(get_current_user_simple)
) -> Optional[AccountInfo]:
	if user.isadmin:
		return None
	scopeSet = {s for s in securityScopes.scopes}
	if any(r.name in scopeSet for r in user.roles):
		return None
	return user

def extract_ip_address(request: Request) -> Tuple[str, str]:
	candidate = request.headers.get("x-real-ip", "")
	if not candidate and request.client:
		candidate = request.client.host
	try:
		address = ipaddress.ip_address(candidate)
		if isinstance(address, ipaddress.IPv4Address):
			return (candidate, "")
		else:
			return ("", candidate)
	except:
		return ("","")


def get_tracking_info(request: Request):
	userAgent = request.headers["user-agent"]
	ipaddresses = extract_ip_address(request)
	
	return TrackingInfo(
		userAgent,
		ipv4Address=ipaddresses[0],
		ipv6Address=ipaddresses[1]
	)

def check_back_key(
	x_back_key: str = Header(),
	envManager: ConfigAcessors=Depends(ConfigAcessors)
):
	if not envManager:
		envManager = ConfigAcessors()
	if envManager.back_key() != x_back_key:
		raise build_wrong_permissions_error()
	
def __get_playlist_user__(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo,
	user: Optional[AccountInfo]
)-> Optional[AccountInfo]:
	minScope = (not securityScopes.scopes or\
		securityScopes.scopes[0] == UserRoleDef.PLAYLIST_VIEW.value
	)
	if not playlist.viewsecuritylevel and minScope:
		return user
	if not user:
		raise build_not_logged_in_error()
	if user.isadmin:
		return user
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Station.conforms(s)
	}
	rules = ActionRule.aggregate(
		playlist.rules,
		filter=lambda r: r.name in scopes
	)
	if not rules:
		raise build_wrong_permissions_error()
	userDict = user.model_dump()
	userDict["roles"] = rules
	return AccountInfo(**userDict)


def get_playlist_user_by_id(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo=Depends(get_playlist_by_id),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token)
)-> Optional[AccountInfo]:
	return __get_playlist_user__(
		securityScopes,
		playlist,
		user
	)

def get_playlist_user(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo=Depends(get_playlist_by_name_and_owner),
	user: Optional[AccountInfo] = Depends(get_optional_user_from_token),
) -> Optional[AccountInfo]:
	return __get_playlist_user__(
		securityScopes,
		playlist,
		user
	)


def current_user_provider(
	user: AccountInfo = Depends(get_current_user_simple)
) -> CurrentUserProvider:
	return CurrentUserProvider(user.id)


def playlists_songs_service(
	conn: Connection=Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider)
) -> PlaylistsSongsService:
	return PlaylistsSongsService(conn, currentUserProvider)