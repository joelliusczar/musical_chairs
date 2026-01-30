#pyright: reportMissingTypeStubs=false
import ipaddress
from datetime import timedelta
from typing import (
	Any,
	Iterator,
	Tuple,
	Optional,
	Union,
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
	FSEventsQueryService,
	BasicUserProvider,
	VisitorTrackingService,
	StationService,
	QueueService,
	SongInfoService,
	ProcessService,
	FSEventsLoggingService,
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
	CurrentUserProvider,
	VisitorService,
)
from musical_chairs_libs.services.events import (
	AggregateEventsLoggingService,
	InMemEventsLoggingService,
	WhenNextCalculator
)
from musical_chairs_libs.protocols import (
	FileService,
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
	DbConnectionProvider,
	get_datetime,
	InMemEventRecordMap,
	int_or_str,
	NotLoggedInError,
	UserRoleDef,
	TrackingInfo,
	PlaylistInfo,
	SimpleQueryParameters,
	UserRoleSphere,
	WrongPermissionsError,
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


class GlobalStore:
	
	def __init__(self) -> None:
		self.events_store = InMemEventRecordMap()
		self.visitor_id_map: dict[str, Any] = {}


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
	connProvider: DbConnectionProvider=Depends(DbConnectionProvider)
) -> Iterator[Connection]:
	if not connProvider:
		connProvider = ConfigAcessors()
	with connProvider.sqlite_connection() as conn:
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
		ipv6Address=ipaddresses[1],
		url=request.url.path
	)

def global_store(request: Request) -> GlobalStore | None:
	try:
		return request.app.state.global_store
	except AttributeError:
		pass


def visitor_service(
		globalStore: GlobalStore | None = Depends(global_store),
	conn: Connection=Depends(get_configured_db_connection)
) -> VisitorService:
	return VisitorService(
		conn, 
		globalStore.visitor_id_map\
		if globalStore else None
	)


def vistor_tracking_service(
	trackingInfo: TrackingInfo = Depends(get_tracking_info),
	visitorService: VisitorService = Depends(visitor_service)
) -> VisitorTrackingService:
	return VisitorTrackingService(trackingInfo, visitorService)


def fs_events_query_service() -> FSEventsQueryService:
	return FSEventsQueryService()


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


def in_mem_events_logging_service(
	globalStore: GlobalStore | None = Depends(global_store),
	vistorTrackingService: VisitorTrackingService = Depends(
		vistor_tracking_service
	),
	basicUserProvider: BasicUserProvider = Depends(basic_user_provider),
	eventsQueryService: FSEventsQueryService = Depends(
		fs_events_query_service
	),
	getDatetime: Callable[[], datetime] = Depends(datetime_provider)
) -> InMemEventsLoggingService:

	service =  InMemEventsLoggingService(
		vistorTrackingService,
		basicUserProvider,
		globalStore.events_store if globalStore else None
	)

	if len(globalStore.events_store if globalStore else (1,)) == 0:
		fromTimestamp = (getDatetime() - timedelta(days=1)).timestamp()
		for record in eventsQueryService.get_user_events(
			None,
			fromTimestamp,
			set()
		):
			service.add_event_record(record)
	return service



def fs_events_logging_service(
	visitorTrackingService: VisitorTrackingService = Depends(
		vistor_tracking_service
	),
	basicUserProvider: BasicUserProvider = Depends(basic_user_provider),
) -> FSEventsLoggingService:
	return FSEventsLoggingService(
		visitorTrackingService,
		basicUserProvider
	)


def aggregate_events_logging_service(
		inMem: InMemEventsLoggingService =  Depends(in_mem_events_logging_service),
		fs: FSEventsLoggingService = Depends(fs_events_logging_service)
):
	return AggregateEventsLoggingService(fs, inMem)


def when_next_calculator(
	inMemEventsLoggingServiice: InMemEventsLoggingService = Depends(
		in_mem_events_logging_service
	),
	userProvider: BasicUserProvider = Depends(basic_user_provider)
) -> WhenNextCalculator:
	return WhenNextCalculator(
		inMemEventsLoggingServiice,
		userProvider
	)


def current_user_provider(
	securityScopes: SecurityScopes,
	basicUserProvider: BasicUserProvider = Depends(basic_user_provider),
	currentUserTrackingService: VisitorTrackingService = Depends(
		vistor_tracking_service
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> CurrentUserProvider:
	return CurrentUserProvider(
		basicUserProvider,
		currentUserTrackingService,
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


def account_management_service(
	conn: Connection=Depends(get_configured_db_connection),
	userProvider: CurrentUserProvider = Depends(
		current_user_provider
	),
	accountsAccessService: AccountAccessService = Depends(account_access_service)
) -> AccountManagementService:
	return AccountManagementService(
		conn,
		userProvider,
		accountsAccessService,
	)


def account_token_creator(
	conn: Connection=Depends(get_configured_db_connection),
) -> AccountTokenCreator:
	return AccountTokenCreator(conn)


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
	songInfoService: SongInfoService = Depends(song_info_service),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> QueueService:
	return QueueService(
		conn,
		currentUserProvider,
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



def open_provided_user(
	userkey: int | str | None,
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
	user = open_provided_user(subjectuserkey, accountManagementService)
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
	user = open_provided_user(subjectuserkey, accountManagementService)
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
	return open_provided_user(ownerkey, accountManagement)


def get_owner_from_path(
	ownerkey: Union[int, str, None] = Depends(owner_key_path),
	accountsService: AccountManagementService = Depends(
		account_management_service
	)
) -> Optional[AccountInfo]:
	return open_provided_user(ownerkey, accountsService)


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
		if UserRoleSphere.Playlist.conforms(s)
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


def check_top_level_rate_limit(sphere: str):
		
	def __check_rate_limit(
		securityScopes: SecurityScopes,
		currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
		whenNextCalculator: WhenNextCalculator = Depends(
			when_next_calculator
		),
	):
		user = currentUserProvider.current_user()
		if user.isadmin:
			return
		scopeSet = {s for s in securityScopes.scopes}
		rules = ActionRule.sorted((r for r in user.roles if r.name in scopeSet))
		if not rules and scopeSet:
			raise WrongPermissionsError()
		whenNextCalculator.check_if_user_can_perform_rate_limited_action(
			scopeSet,
			rules,
			sphere
		)
	
	return __check_rate_limit

