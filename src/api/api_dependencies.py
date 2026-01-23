#pyright: reportMissingTypeStubs=false
import ipaddress
from typing import (
	Iterator,
	Tuple,
	Optional,
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
	AccountAccessService,
	AccountManagementService,
	AccountTokenCreator,
	EventsQueryService,
	BasicUserProvider,
	CurrentUserTrackingService,
	StationService,
	QueueService,
	SongInfoService,
	ProcessService,
	EventsLoggingService,
	SongFileService,
	PathRuleService,
	ArtistService,
	AlbumService,
	JobsService,
	PlaylistService,
	PlaylistsUserService,
	PlaylistsSongsService,
	StationsAlbumsService,
	StationsPlaylistsService,
	StationsSongsService,
	StationsUsersService,
	StationProcessService,
	CollectionQueueService,
	CurrentUserProvider,
	UserAgentService,
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
	ActionRule,
	AlbumInfo,
	ArtistInfo,
	build_error_obj,
	ConfigAcessors,
	DirectoryTransfer,
	get_datetime,
	normalize_opening_slash,
	NotLoggedInError,
	UserRoleDef,
	StationInfo,
	int_or_str,
	TrackingInfo,
	PlaylistInfo,
	SimpleQueryParameters,
	UserRoleDomain,
	WrongPermissionsError,
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
	ownerkey: Union[int, str, None]  = Query(None),
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


def account_access_service(
	conn: Connection=Depends(get_configured_db_connection),
) -> AccountAccessService:
	return AccountAccessService(conn)


def get_user_from_token(
	token: str,
	accountAccessService: AccountAccessService
) -> Tuple[AccountInfo, float]:
	if not token:
		raise build_not_logged_in_error()
	try:
		user, expiration = accountAccessService.get_user_from_token(token)
		if not user:
			raise build_not_wrong_credentials_error()
		return user, expiration
	except ExpiredSignatureError:
		raise build_expired_credentials_error()


def get_current_user_simple(
	request: Request,
	token: str = Depends(oauth2_scheme),
	accountsAccessService: AccountAccessService = Depends(account_access_service)
) -> AccountInfo:
	cookieToken = request.cookies.get("access_token", None)
	user, _ = get_user_from_token(
		token or parse.unquote(cookieToken or ""),
		accountsAccessService
	)
	return user


def get_optional_user_from_token(
	request: Request,
	token: str = Depends(oauth2_scheme),
	accountAccessService: AccountAccessService = Depends(account_access_service),
) -> Optional[AccountInfo]:
	cookieToken = request.cookies.get("access_token", None)
	if not token and not cookieToken:
		return None
	try:
		user, _ = accountAccessService.get_user_from_token(
			token or parse.unquote(cookieToken or "")
		)
		return user
	except ExpiredSignatureError:
		raise build_expired_credentials_error()


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


def user_agent_service(
	conn: Connection=Depends(get_configured_db_connection)
) -> UserAgentService:
	return UserAgentService(conn)


def current_user_tracking_service(
	trackingInfo: TrackingInfo = Depends(get_tracking_info),
	userAgentService: UserAgentService = Depends(user_agent_service)
) -> CurrentUserTrackingService:
	return CurrentUserTrackingService(trackingInfo, userAgentService)


def actions_history_query_service() -> EventsQueryService:
	return EventsQueryService()


def file_service() -> FileService:
	return S3FileService()


def basic_user_provider(
	user: AccountInfo = Depends(get_optional_user_from_token),
) -> BasicUserProvider:
	return BasicUserProvider(user)


def path_rule_service(
	conn: Connection = Depends(get_configured_db_connection),
	fileService: FileService = Depends(file_service),
	userProvider: BasicUserProvider = Depends(basic_user_provider)
) -> PathRuleService:
	return PathRuleService(conn, fileService, userProvider)


def current_user_provider(
	securityScopes: SecurityScopes,
	basicUserProvider: BasicUserProvider = Depends(basic_user_provider),
	currentUserTrackingService: CurrentUserTrackingService = Depends(
		current_user_tracking_service
	),
	actionsHistoryQueryService: EventsQueryService = Depends(
		actions_history_query_service
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> CurrentUserProvider:
	return CurrentUserProvider(
		basicUserProvider,
		currentUserTrackingService,
		actionsHistoryQueryService,
		pathRuleService,
		set(securityScopes.scopes)
	)

def __check_scope__(
	securityScopes: SecurityScopes,
	currentUser: AccountInfo,
):
	scopeSet = {s for s in securityScopes.scopes}
	hasRole = currentUser.isadmin or\
		any(r.name in scopeSet for r in currentUser.roles)
	if not hasRole:
		raise build_wrong_permissions_error()

def check_scope(
	securityScopes: SecurityScopes,
	currentUser: AccountInfo = Depends(get_current_user_simple),
):
	__check_scope__(securityScopes, currentUser)


def actions_history_management_service(
	currentUserTrackingService: CurrentUserTrackingService = Depends(
		current_user_tracking_service
	),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	)
) -> EventsLoggingService:
	return EventsLoggingService(
		currentUserTrackingService,
		userProvider
	)


def account_management_service(
	conn: Connection=Depends(get_configured_db_connection),
	userActionHistoryService: EventsLoggingService =
		Depends(actions_history_management_service),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
	accountsAccessService: AccountAccessService = Depends(account_access_service)
) -> AccountManagementService:
	return AccountManagementService(
		conn,
		userProvider,
		accountsAccessService,
		userActionHistoryService,
	)


def account_token_creator(
	conn: Connection=Depends(get_configured_db_connection),
	userActionHistoryService: EventsLoggingService =
		Depends(actions_history_management_service)
) -> AccountTokenCreator:
	return AccountTokenCreator(conn, userActionHistoryService)


def playlists_songs_service(
	conn: Connection=Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> PlaylistsSongsService:
	return PlaylistsSongsService(conn, currentUserProvider, pathRuleService)


def song_info_service(
	conn: Connection=Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	pathRuleService: PathRuleService = Depends(path_rule_service)
) -> SongInfoService:
	return SongInfoService(conn, currentUserProvider, pathRuleService)


def queue_service(
	conn: Connection=Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	userActionHistoryService: EventsLoggingService =
		Depends(actions_history_management_service),
	songInfoService: SongInfoService = Depends(song_info_service),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> QueueService:
	return QueueService(
		conn,
		currentUserProvider,
		userActionHistoryService,
		songInfoService,
		pathRuleService,
	)


def station_service(
	conn: Connection = Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> StationService:
	return StationService(conn, userProvider, pathRuleService)


def stations_albums_service(
	conn: Connection = Depends(get_configured_db_connection),
	stationService: StationService = Depends(station_service),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
) -> StationsAlbumsService:
	return StationsAlbumsService(conn, stationService, userProvider)


def album_service(
	conn: Connection = Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	stationsAlbumsService: StationsAlbumsService = Depends(
		stations_albums_service
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> AlbumService:
	return AlbumService(
		conn,
		currentUserProvider,
		stationsAlbumsService,
		pathRuleService
	)


def station_process_service(
	conn: Connection=Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
	stationService: StationService = Depends(station_service),
) -> StationProcessService:
	return StationProcessService(conn, userProvider, stationService)


def stations_songs_service(
	conn: Connection=Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
) -> StationsSongsService:
	return StationsSongsService(conn, userProvider)


def stations_playlists_service(
	conn: Connection=Depends(get_configured_db_connection),
	stationService: StationService = Depends(station_service),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
) -> StationsPlaylistsService:
	return StationsPlaylistsService(conn, stationService, userProvider)


def stations_users_service(
	conn: Connection=Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
) -> StationsUsersService:
	return StationsUsersService(conn, userProvider)


def playlist_service(
	conn: Connection=Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
	stationsPlaylistsService: StationsPlaylistsService = Depends(
		stations_playlists_service
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> PlaylistService:
	return PlaylistService(
		conn,
		userProvider,
		stationsPlaylistsService,
		pathRuleService,
	)


def playlists_users_service(
	conn: Connection=Depends(get_configured_db_connection),
	pathRuleService: PathRuleService = Depends(path_rule_service),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
) -> PlaylistsUserService:
	return PlaylistsUserService(conn, pathRuleService, userProvider)


def artist_service(
	conn: Connection=Depends(get_configured_db_connection),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> ArtistService:
	return ArtistService(conn, currentUserProvider, pathRuleService)


def song_file_service(
	conn: Connection = Depends(get_configured_db_connection),
	fileService: FileService = Depends(file_service),
	artistService: ArtistService = Depends(artist_service),
	albumService: AlbumService = Depends(album_service),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> SongFileService:
	return SongFileService(
		conn,
		fileService,
		artistService,
		albumService,
		currentUserProvider
	)


def job_service(
	conn: Connection=Depends(get_configured_db_connection),
	fileService: FileService=Depends(file_service)
) -> JobsService:
	return JobsService(conn, fileService)


def process_service() -> ProcessService:
	return ProcessService()


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
	return ""


def get_prefix(
	prefix:Optional[str] = Depends(get_optional_prefix)
) -> str:
	if prefix is not None:
		return prefix
	raise HTTPException(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		detail=[build_error_obj("prefix and nodeId both missing")
		]
	)


def get_read_secured_prefix(
	prefix: str = Depends(get_prefix),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> str:
	currentUserProvider.get_path_rule_loaded_current_user()
	return prefix


def get_write_secured_prefix(
	securityScopes: SecurityScopes,
	prefix: str = Depends(get_prefix),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> str:
	user = currentUserProvider.get_path_rule_loaded_current_user()
	if user.isadmin:
		return prefix
	if not securityScopes:
		return prefix
	
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	if prefix:
		userPrefixTrie = user.get_permitted_paths_tree()
		currentUserProvider.check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie,
		)
	return prefix


def get_secured_directory_transfer(
	transfer: DirectoryTransfer,
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> DirectoryTransfer:
	user = currentUserProvider.get_path_rule_loaded_current_user()
	userPrefixTrie = user.get_permitted_paths_tree()
	scopes = (
		(transfer.path, UserRoleDef.PATH_DELETE),
		(transfer.newprefix, UserRoleDef.PATH_EDIT)
	)

	for path, scope in scopes:
		currentUserProvider.check_if_can_use_path(
			[scope.value],
			path,
			user,
			userPrefixTrie
		)
	return transfer

def __open_user_from_request__(
	userkey: Union[int, str, None],
	accountManagementService: AccountManagementService
) -> Optional[AccountInfo]:
	if userkey:
		try:
			userkey = int(userkey)
			owner = accountManagementService.get_account_for_edit(userkey)
		except:
			owner = accountManagementService.get_account_for_edit(userkey)
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
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> AccountInfo:
	user = __open_user_from_request__(subjectuserkey, accountManagementService)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj("subjectuserkey missing")
			]
		)
	return user


def get_from_query_subject_user(
	subjectuserkey: Union[int, str] = Depends(subject_user_key_query),
	accountManagementService: AccountManagementService = Depends(
		account_management_service
	)
) -> AccountInfo:
	user = __open_user_from_request__(subjectuserkey, accountManagementService)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj("subjectuserkey missing")
			]
		)
	return user


def get_owner_from_query(
	ownerkey: Union[int, str, None] = Depends(owner_key_query),
	accountManagement: AccountManagementService = Depends(
		account_management_service
	)
) -> Optional[AccountInfo]:
	return __open_user_from_request__(ownerkey, accountManagement)


def get_owner_from_path(
	ownerkey: Union[int, str, None] = Depends(owner_key_path),
	accountsService: AccountManagementService = Depends(
		account_management_service
	)
) -> Optional[AccountInfo]:
	return __open_user_from_request__(ownerkey, accountsService)


def get_playlist_by_name_and_owner(
	playlistkey: Union[int, str] = Depends(playlist_key_path),
	owner: Optional[AccountInfo] = Depends(get_owner_from_path),
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
	),None)
	if not playlist:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"station with key {playlistkey} not found")
			]
		)
	return playlist


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


def __check_playlist_scopes__(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo,
	currentUserProvider : CurrentUserProvider
):
	user = currentUserProvider.current_user(optional=True)
	minScope = (not securityScopes.scopes or\
		UserRoleDef.PLAYLIST_VIEW.value in securityScopes.scopes
	)
	if not playlist.viewsecuritylevel and minScope:
		return user
	if not user:
		raise NotLoggedInError()
	if user.isadmin:
		return user
	scopes = {s for s in securityScopes.scopes \
		if UserRoleDomain.Playlist.conforms(s)
	}
	rules = ActionRule.aggregate(
		playlist.rules,
		filter=lambda r: r.name in scopes
	)
	if not rules:
		raise WrongPermissionsError()


def get_secured_playlist_by_id(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo=Depends(get_playlist_by_id),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> PlaylistInfo:
	__check_playlist_scopes__(securityScopes, playlist, currentUserProvider)
	return playlist


def get_secured_playlist_by_name_and_owner(
	securityScopes: SecurityScopes,
	playlist: PlaylistInfo=Depends(get_playlist_by_name_and_owner),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> PlaylistInfo:
	__check_playlist_scopes__(securityScopes, playlist, currentUserProvider)
	return playlist


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


def get_stations_by_ids(
	stationids: list[int]=Query(default=[]),
	stationService: StationService = Depends(station_service),
) -> Collection[StationInfo]:
	if not stationids:
		return ()
	return list(stationService.get_stations(
		stationids
	))


def get_station_by_name_and_owner(
	stationkey: Union[int, str] = Depends(station_key_path),
	owner: Optional[AccountInfo] = Depends(get_owner_from_path),
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
		ownerId=ownerId
	),None)
	if not station:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(f"station with key {stationkey} not found")
			]
		)
	return station


def get_secured_station_by_id(
	station: StationInfo = Depends(get_station_by_id),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> StationInfo:
	currentUserProvider.get_station_user(station)
	return station


def get_secured_station_by_name_and_owner(
	station: StationInfo = Depends(get_station_by_name_and_owner),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> StationInfo:
	currentUserProvider.get_station_user(station)
	return station


def get_album_by_id(
		albumid: int=Path(),
		albumService: AlbumService = Depends(album_service),
) -> AlbumInfo:
	album = next(albumService.get_albums(albumKeys=albumid), None)
	if not album:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"Album not found for id {albumid}"
			)]
		)
	return album

def get_secured_album_by_id(
	securityScopes: SecurityScopes,
	album: AlbumInfo = Depends(get_album_by_id),
	currentUser: AccountInfo = Depends(get_current_user_simple),
) -> AlbumInfo:
	if album.owner.id == currentUser.id:
		return album
	__check_scope__(securityScopes, currentUser)
	return album


def get_artist_by_id(
		artistid: int=Path(),
		artist_service: ArtistService = Depends(artist_service),
) -> ArtistInfo:
	artist = next(artist_service.get_artists(artistKeys=artistid), None)
	if not artist:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[build_error_obj(
				f"Album not found for id {artistid}"
			)]
		)
	return artist


def get_secured_artist_by_id(
	securityScopes: SecurityScopes,
	artist: ArtistInfo = Depends(get_artist_by_id),
	currentUser: AccountInfo = Depends(get_current_user_simple),
) -> ArtistInfo:
	if artist.owner.id == currentUser.id:
		return artist
	__check_scope__(securityScopes, currentUser)
	return artist


def station_radio_pusher(
	station: StationInfo = Depends(get_station_by_name_and_owner),
	conn: Connection = Depends(get_configured_db_connection),
	queueService: QueueService =  Depends(queue_service),
	currentUserProvider: CurrentUserProvider = Depends(current_user_provider),
) -> RadioPusher:
	if station.typeid == StationTypes.SONGS_ONLY.value:
		return queueService
	if station.typeid == StationTypes.ALBUMS_ONLY.value\
		or station.typeid == StationTypes.PLAYLISTS_ONLY.value\
		or station.typeid == StationTypes.ALBUMS_AND_PLAYLISTS.value\
			:
		return CollectionQueueService(
			conn,
			queueService,
			currentUserProvider
		)
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


def impersonated_user_id(
	impersonateduserid: Optional[int],
	user: AccountInfo = Depends(get_current_user_simple)
) -> Optional[int]:
	if user.isadmin or any(r.conforms(UserRoleDef.USER_IMPERSONATE.value) \
			for r in user.roles):
		return impersonateduserid
	return None


def check_subjectuser(
	securityScopes: SecurityScopes,
	subjectuserkey: Union[int, str] = Depends(subject_user_key_path),
	currentUser: AccountInfo = Depends(get_current_user_simple),
):
	isCurrentUser = subjectuserkey == currentUser.id or\
		subjectuserkey == currentUser.username
	scopeSet = {s for s in securityScopes.scopes}
	hasEditRole = currentUser.isadmin or\
		any(r.name in scopeSet for r in currentUser.roles)
	if not isCurrentUser and not hasEditRole:
		raise build_wrong_permissions_error()


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


def check_back_key(
	x_back_key: str = Header(),
	envManager: ConfigAcessors=Depends(ConfigAcessors)
):
	if not envManager:
		envManager = ConfigAcessors()
	if envManager.back_key() != x_back_key:
		raise build_wrong_permissions_error()


def get_query_params(
	limit: int = 50,
	page: int = Depends(get_page_num),
	orderby: Optional[str]=None,
	sortdir: Optional[str]=None,
) -> SimpleQueryParameters:
		return SimpleQueryParameters(
			page=page,
			limit=limit,
			orderby=orderby,
			sortdir=sortdir
		)

def get_secured_query_params(
	securityScopes: SecurityScopes,
	queryParams: SimpleQueryParameters=Depends(get_query_params),
	currentUser: AccountInfo = Depends(get_current_user_simple),
) -> SimpleQueryParameters:
	__check_scope__(securityScopes, currentUser)
	return queryParams


def check_rate_limit(domain: str):
		
	def __check_rate_limit(
		currentUserProvider : CurrentUserProvider = Depends(current_user_provider)
	):
		currentUserProvider.get_rate_limited_user(domain)
	
	return __check_rate_limit


def log_event():
	yield
	print("Hi here")