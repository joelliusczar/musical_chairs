from typing import Union, Iterable, Optional
from fastapi import (
	Depends,
	HTTPException,
	status,
	Request,
)
from fastapi.security import SecurityScopes
from musical_chairs_libs.services import (
	CurrentUserProvider,
	StationService,
	ArtistService,
	AlbumService,
	PathRuleService,
	StationsSongsService
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	build_error_obj,
	ValidatedSongAboutInfo,
	ActionRule,
	UserRoleDomain,
	normalize_opening_slash,
	get_path_owner_roles
)
from api_dependencies import (
	current_user_provider,
	path_rule_service,
	station_service,
	get_from_query_subject_user,
	get_prefix,
	album_service,
	artist_service,
	stations_songs_service,
)



def __get_station_id_set__(
	user: AccountInfo,
	stationService: StationService,
	stationKeys: Union[int,str, Iterable[int], None]=None
) -> set[int]:

	if user.has_roles(UserRoleDef.STATION_ASSIGN):
		return {s.id for s in stationService.get_stations(
			stationKeys=stationKeys
		)}
	else:
		return {s.id for s in stationService.get_stations(
		stationKeys=stationKeys,
	) if any(r.name == UserRoleDef.STATION_ASSIGN.value for r in s.rules)}


def get_song_ids(request: Request) -> list[int]:
	result: set[int] = set()
	fieldName = ""
	try:
		fieldNames = ["itemId", "itemid", "id", "songid"]
		for fieldName in fieldNames:
			key = request.path_params.get(fieldName, None)
			if not key is None:
				result.add(int(key))

		fieldNames = ["itemids", "songids", "itemIds"]
		for fieldName in fieldNames:
			keys = request.query_params.getlist(fieldName)
			result.update((int(i) for i in keys))
		
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


def get_secured_song_ids(
	securityScopes: SecurityScopes,
	songIds: list[int] = Depends(get_song_ids),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	pathRuleService: PathRuleService = Depends(path_rule_service),
) -> list[int]:
	user = currentUserProvider.get_path_rule_loaded_current_user()
	if user.isadmin:
		return songIds
	userPrefixTrie = user.get_permitted_paths_tree()
	prefixes = [*pathRuleService.get_song_path(songIds)]
	scopes = [s for s in securityScopes.scopes \
		if UserRoleDomain.Path.conforms(s)
	]
	for prefix in prefixes:
		currentUserProvider.check_if_can_use_path(
			scopes,
			prefix,
			user,
			userPrefixTrie
		)
	return songIds


def __validate_song_stations__(
	song: ValidatedSongAboutInfo,
	songIds: Iterable[int],
	user: AccountInfo,
	stationService: StationService,
	stationsSongsService: StationsSongsService,
):
	if not song.stations:
		return
	stationIds = {s.id for s in song.stations or []}
	linkedStationIds = {s.stationid for s in \
		stationsSongsService.get_station_songs(songIds=songIds)}
	permittedStations = {s.id for s in \
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
						f" {str(stationIds)}",
					"Stations"
				)],
		)
	#dbStations will only be the stations user can see
	dbStations = __get_station_id_set__(user, stationService, stationIds)
	#stations that user can't see, are not linked, or don't exist
	if stationIds - dbStations - linkedStationIds - permittedStations:
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
	user: AccountInfo,
	artistService: ArtistService,
):
	if not song.allArtists:
		return
	artistIds = {a.id for a in song.allArtists}
	dbArtists = {a.id for a in artistService.get_artists(
		artistKeys=artistIds,
		#in theory, this should not create a vulnerability
		#because even if user has path:edit on a non-overlapping path
		#it should get caught above
		userId=user.id if not user.has_roles(UserRoleDef.PATH_EDIT) else None
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
	user: AccountInfo,
	albumService: AlbumService,
):
	if song.album:
		dbAlbum = next(albumService.get_albums(
			albumKeys=song.album.id,
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


def extra_validated_song(
	song: ValidatedSongAboutInfo,
	songIds: Iterable[int] = Depends(get_secured_song_ids),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
	stationService: StationService = Depends(station_service),
	stationsSongsService: StationsSongsService = Depends(stations_songs_service),
	artistService: ArtistService = Depends(artist_service),
	albumService: AlbumService = Depends(album_service)
) -> ValidatedSongAboutInfo:
	user = currentUserProvider.get_path_rule_loaded_current_user()
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
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
) -> ActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set(UserRoleDomain.Path.value)
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
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
	ruleName: Optional[str]=None
) -> Optional[str]:
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