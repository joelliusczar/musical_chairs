from typing import Union, Iterable, Optional
from fastapi import (
	Depends,
	HTTPException,
	status,
	Request
)
from musical_chairs_libs.services import SongInfoService, StationService
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	UserRoleDef,
	build_error_obj,
	ValidatedSongAboutInfo,
	PathsActionRule,
	UserRoleDomain,
	normalize_opening_slash,
	get_path_owner_roles
)
from api_dependencies import (
	song_info_service,
	station_service,
	get_path_user,
	get_subject_user
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
		user=user,
	) if any(r.name == UserRoleDef.STATION_ASSIGN.value for r in s.rules)}


def get_song_ids(request: Request) -> Iterable[int]:
	result: set[int] = set()
	fieldName = ""
	try:
		fieldName = "itemId"
		itemId = request.path_params.get(fieldName, None)
		if not itemId is None:
			result.add(int(itemId))
		fieldName = "itemIds"
		itemIds = request.query_params.getlist(fieldName)
		result.update(itemIds)

	except ValueError:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[
				build_error_obj(
					f"Not a valid integer",
					fieldName
				)],
		)
	return result

def __validate_song_stations(
	song: ValidatedSongAboutInfo,
	songIds: Iterable[int],
	user: AccountInfo,
	stationService: StationService,
	songInfoService: SongInfoService,
):
	if not song.stations:
		return
	stationIds = {s.id for s in song.stations or []}
	linkedStationIds = {s.stationId for s in \
		songInfoService.get_station_songs(songIds=songIds)}
	permittedStations = {s.id for s in \
			stationService.get_stations(
			stationIds,
			user=user,
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

def __validate_song_artists(
	song: ValidatedSongAboutInfo,
	user: AccountInfo,
	songInfoService: SongInfoService,
):
	if not song.allArtists:
		return
	artistIds = {a.id for a in song.allArtists}
	dbArtists = {a.id for a in songInfoService.get_artists(
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

def __validate_song_album(
	song: ValidatedSongAboutInfo,
	user: AccountInfo,
	songInfoService: SongInfoService,
):
	if song.album:
		dbAlbum = next(songInfoService.get_albums(
			albumKeys=song.album.id,
			userId=user.id if not user.has_roles(UserRoleDef.PATH_EDIT) else None
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
	songIds: Iterable[int] = Depends(get_song_ids),
	user: AccountInfo = Depends(get_path_user),
	stationService: StationService = Depends(station_service),
	songInfoService: SongInfoService = Depends(song_info_service),
) -> ValidatedSongAboutInfo:
	__validate_song_stations(
		song,
		songIds,
		user,
		stationService,
		songInfoService
	)
	__validate_song_artists(song, user, songInfoService)
	__validate_song_album(song, user, songInfoService)
	return song

def validate_path_rule(
	rule: PathsActionRule,
	prefix: str,
	user: Optional[AccountInfo] = Depends(get_subject_user),
) -> PathsActionRule:
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
	user: Optional[AccountInfo] = Depends(get_subject_user),
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