import musical_chairs_libs.dtos_and_utilities as dtos
from base64 import urlsafe_b64decode
from typing import Union, Iterable, Optional
from fastapi import (
	Depends,
	HTTPException,
	status,
	Query,
	Request,
)
from fastapi.security import SecurityScopes
from musical_chairs_libs.services import (
	CurrentUserProvider,
	StationService,
	ArtistService,
	AlbumService,
	PathRuleService,
	StationsSongsService,
)
from musical_chairs_libs.services.events import (
	WhenNextCalculator
)
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	build_error_obj,
	ChainedAbsorbentTrie,
	DirectoryTransfer,
	RoledUser,
	UserRoleDef,
	ValidatedSongAboutInfo,
	UserRoleSphere,
	normalize_opening_slash,
	get_path_owner_roles,
	WrongPermissionsError,
)
from api_dependencies import (
	current_user_provider,
	path_rule_service,
	station_service,
	get_current_user_simple,
	subject_user,
	album_service,
	artist_service,
	stations_songs_service,
	when_next_calculator
)



def __get_station_id_set__(
	user: RoledUser,
	stationService: StationService,
	stationKeys: Union[int,str, Iterable[int], None]=None
) -> set[int]:

	if user.has_site_roles(UserRoleDef.STATION_ASSIGN):
		return {s.decoded_id() for s in stationService.get_stations(
			stationKeys=stationKeys
		)}
	else:
		return {s.decoded_id() for s in stationService.get_stations(
		stationKeys=stationKeys,
	) if any(r.name == UserRoleDef.STATION_ASSIGN.value for r in s.rules)}


def get_song_ids(request: Request) -> list[int]:
	result: set[int] = set()
	fieldName = ""
	try:
		fieldNames = ["itemId", "itemid", "id", "songid"]
		for fieldName in fieldNames:
			key = request.path_params.get(fieldName, None)
			if key is not None:
				result.add(dtos.decode_id(key))

		fieldNames = ["itemids", "songids", "itemIds"]
		for fieldName in fieldNames:
			keys = request.query_params.getlist(fieldName)
			result.update((dtos.decode_id(i) for i in keys))
		
	except ValueError:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Not a valid integer for the song id(s)",
					fieldName
				)],
		)
	return [*result]


def check_if_can_use_path(
	scopes: set[str],
	prefix: str,
	userPrefixTrie: ChainedAbsorbentTrie[ActionRule],
	whenNextCalculator: WhenNextCalculator
):
	scopeSet = scopes
	rules = ActionRule.sorted(
		(r for i in userPrefixTrie.values(normalize_opening_slash(prefix)) \
			for r in i if r.name in scopeSet)
	)
	if not rules and scopes:
		raise WrongPermissionsError(f"{prefix} not found")
	whenNextCalculator.check_if_user_can_perform_rate_limited_action(
		scopes,
		rules,
		UserRoleSphere.Path.value
	)


def get_secured_song_ids(
	securityScopes: SecurityScopes,
	songIds: list[int] = Depends(get_song_ids),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	pathRuleService: PathRuleService = Depends(path_rule_service),
	whenNextCalculator: WhenNextCalculator = Depends(
		when_next_calculator
	),
) -> list[int]:
	user = currentUserProvider.get_path_rule_loaded_current_user().to_roled_user()
	if user.isadmin:
		return songIds
	userPrefixTrie = pathRuleService.get_permitted_paths_tree(user)
	prefixes = [*pathRuleService.get_song_path(songIds)]
	scopes = {s for s in securityScopes.scopes \
		if UserRoleSphere.Path.conforms(s)
	}
	for prefix in prefixes:
		check_if_can_use_path(
			scopes,
			prefix,
			userPrefixTrie,
			whenNextCalculator
		)
	return songIds


def __validate_song_stations__(
	song: ValidatedSongAboutInfo,
	songIds: Iterable[int],
	user: RoledUser,
	stationService: StationService,
	stationsSongsService: StationsSongsService,
):
	if not song.stations:
		return
	stationIds = {s.decoded_id() for s in song.stations or []}
	linkedStationIds = {s.stationid for s in \
		stationsSongsService.get_station_songs(songIds=songIds)}
	permittedStations = {s.decoded_id() for s in \
			stationService.get_stations(
			stationIds,
			scopes=[UserRoleDef.STATION_ASSIGN.value]
		) if not all(r.blocked for r in s.rules)
	} | linkedStationIds #if song is already linked, we will permit
	if not permittedStations:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=[
				build_error_obj(
					"Do not have permission to work with all of stations"
						f" {str(s.id for s in song.stations)}",
					"Stations"
				)],
		)
	#dbStations will only be the stations user can see
	dbStations = __get_station_id_set__(user, stationService, stationIds)
	#stations that user can't see, are not linked, or don't exist
	flagged = stationIds - dbStations - linkedStationIds - permittedStations
	if flagged:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Stations associated with ids {str(stationIds)} do not exist",
					"Stations"
				)],
		)


def __validate_song_artists__(
	song: ValidatedSongAboutInfo,
	user: RoledUser,
	artistService: ArtistService,
):
	if not song.allArtists:
		return
	artistIds = {a.decoded_id() for a in song.allArtists}
	dbArtists = {a.decoded_id() for a in artistService.get_artists(
		artistKeys=artistIds,
		#in theory, this should not create a vulnerability
		#because even if user has path:edit on a non-overlapping path
		#it should get caught above
	)}
	if artistIds - dbArtists:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Artists associated with ids {str(artistIds)} do not exist",
					"artists"
				)],
		)

def __validate_song_album__(
	song: ValidatedSongAboutInfo,
	user: RoledUser,
	albumService: AlbumService,
):
	if song.album:
		dbAlbum = next(albumService.get_albums(
			albumKeys=song.album.decoded_id(),
		), None)
		if not dbAlbum:
			raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Album associated with ids {str(song.album.id)} does not exist",
					"artists"
				)],
		)


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
	whenNextCalculator: WhenNextCalculator = Depends(
		when_next_calculator
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> str:
	user = currentUserProvider.get_path_rule_loaded_current_user().to_roled_user()
	if user.isadmin:
		return prefix
	if not securityScopes:
		return prefix
	
	scopes = {s for s in securityScopes.scopes \
		if UserRoleSphere.Path.conforms(s)
	}
	if prefix:
		userPrefixTrie = pathRuleService.get_permitted_paths_tree(user)
		check_if_can_use_path(
			scopes,
			prefix,
			userPrefixTrie,
			whenNextCalculator
		)
	return prefix


def get_prefix_if_owner(
	prefix: str=Depends(get_prefix),
	currentUser: RoledUser = Depends(get_current_user_simple),
) -> str:
	if not currentUser.dirroot:
		raise WrongPermissionsError()
	normalizedPrefix = normalize_opening_slash(prefix)
	if not normalizedPrefix.startswith(
		normalize_opening_slash(currentUser.dirroot)
	):
		raise WrongPermissionsError()
	return prefix


def get_secured_directory_transfer(
	transfer: DirectoryTransfer,
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	whenNextCalculator: WhenNextCalculator = Depends(
		when_next_calculator
	),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> DirectoryTransfer:
	user = currentUserProvider.get_path_rule_loaded_current_user().to_roled_user()
	userPrefixTrie = pathRuleService.get_permitted_paths_tree(user)
	scopes = (
		(transfer.treepath, UserRoleDef.PATH_DELETE),
		(transfer.newprefix, UserRoleDef.PATH_EDIT)
	)

	for path, scope in scopes:
		check_if_can_use_path(
			{scope.value},
			path,
			userPrefixTrie,
			whenNextCalculator
		)
	return transfer


def extra_validated_song(
	song: ValidatedSongAboutInfo,
	songIds: Iterable[int] = Depends(get_secured_song_ids),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	stationService: StationService = Depends(station_service),
	stationsSongsService: StationsSongsService = Depends(stations_songs_service),
	artistService: ArtistService = Depends(artist_service),
	albumService: AlbumService = Depends(album_service)
) -> ValidatedSongAboutInfo:
	user = currentUserProvider.get_path_rule_loaded_current_user().to_roled_user()
	__validate_song_stations__(
		song,
		songIds,
		user,
		stationService,
		stationsSongsService
	)
	__validate_song_artists__(song, user, artistService)
	__validate_song_album__(song, user, albumService)
	return song

def validate_path_rule(
	rule: ActionRule,
	prefix: str = Depends(get_prefix),
	user: dtos.RoledUser | None = Depends(subject_user),
) -> ActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set(UserRoleSphere.Path.value)
	if rule.name not in valid_name_set:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{rule.name} is not a valid rule for stations"
			)],
		)
	normalizedPrefix = normalize_opening_slash(prefix)
	if user.dirroot and \
		normalizedPrefix.startswith(normalize_opening_slash(user.dirroot))\
	:
		if any(get_path_owner_roles(normalizedPrefix, (rule.name, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{rule.name} cannot be added to owner"
				)],
			)
	return rule


def validate_path_rule_for_remove(
	prefix: str,
	user: dtos.RoledUser | None = Depends(subject_user),
	ruleName: str | None=None
) -> str | None:
	if not user:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					"User is required"
				)],
			)
	normalizedPrefix = normalize_opening_slash(prefix)
	isOwner = user.dirroot and \
		normalizedPrefix.startswith(normalize_opening_slash(user.dirroot))
	if not ruleName:
		if isOwner:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"Cannot remove owner from station"
				)],
			)
		return ruleName
	if ruleName == UserRoleDef.STATION_VIEW.value:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{ruleName} cannot be removed"
			)],
		)
	if isOwner:
		if any(get_path_owner_roles(normalizedPrefix, (ruleName, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{ruleName} cannot be removed from owner"
				)],
			)
	return ruleName