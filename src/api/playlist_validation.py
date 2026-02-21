import musical_chairs_libs.dtos_and_utilities as dtos
from typing import Optional
from fastapi import (
	Depends,
	HTTPException,
	Request,
	status,
)
from fastapi.security import SecurityScopes
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	UserRoleSphere,
	build_error_obj,
	PlaylistInfo,
	get_playlist_owner_roles,
	ActionRule,
)
from musical_chairs_libs.services import (
	AccountAccessService,
	CurrentUserProvider,
	PlaylistService
)
from api_dependencies import (
	account_access_service,
	current_user_provider,
	open_provided_user,
	playlist_service,
	subject_user
)


def get_playlists(
	request: Request,
	playlistService: PlaylistService = Depends(playlist_service),
	accountAccessService: AccountAccessService = Depends(
		account_access_service
	)
) -> list[dtos.PlaylistInfo]:
	result = None
	pathId = request.path_params.get("playlistid", None)
	if pathId is not None:
		return playlistService.get_playlists(dtos.decode_id(pathId))
	
	pathName = request.path_params.get("playlistkey", None)
	if pathName is not None:
		ownerKey = request.path_params.get("ownerkey", None)
		if ownerKey is not None:
			owner = open_provided_user(ownerKey, accountAccessService)
			if owner:
				return playlistService.get_playlists (
					dtos.int_or_str(pathName),
					ownerId=owner.id
				)
			else:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=[
						build_error_obj(
							f"Owner not found for {ownerKey}",
							"ownerKey"
						)],
				)

	queryIds = request.query_params.getlist("playlistids")
	if queryIds:
		result = playlistService.get_playlists((int(s) for s in queryIds))
	if result:
		return result
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[
				build_error_obj(
					f"Stations wer not found",
					"Station"
				)],
		)
	

def get_playlist(
	playlists: list[dtos.PlaylistInfo] = Depends(get_playlists)
) -> dtos.PlaylistInfo:

	playlist = next(iter(playlists), None)
	if playlist:
		return playlist
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=[
			build_error_obj(
				f"Playlist was not found",
				"Playlist"
			)],
	)


def conforming_scopes(securityScopes: SecurityScopes) -> set[str]:
	return {s for s in securityScopes.scopes \
		if UserRoleSphere.Playlist.conforms(s)
	}


def __get_playlist_rules__(
	conformingSopes: set[str],
	playlist: dtos.PlaylistInfo,
	currentUserProvider: CurrentUserProvider,
) -> list[ActionRule]:
	minScope = (not conformingSopes or\
		UserRoleDef.PLAYLIST_VIEW.value in conformingSopes
	)
	user = currentUserProvider.current_user()
	if not playlist.viewsecuritylevel and minScope:
		return playlist.rules

	if user.isadmin:
		return playlist.rules
	scopes = conformingSopes
	rules = ActionRule.aggregate(
		playlist.rules,
		filter=lambda r: r.name in scopes
	)
	if not rules:
		raise dtos.WrongPermissionsError()
	return rules


def get_playlist_rules(
	conformingSopes: set[str] = Depends(conforming_scopes),
	station: dtos.PlaylistInfo = Depends(get_playlist),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> list[ActionRule]:
	return __get_playlist_rules__(conformingSopes, station, currentUserProvider)
	

def get_secured_playlist(
	conformingSopes: set[str] = Depends(conforming_scopes),
	station: dtos.PlaylistInfo = Depends(get_playlist),
	currentUserProvider : CurrentUserProvider = Depends(current_user_provider),
) -> dtos.PlaylistInfo:
	__get_playlist_rules__(conformingSopes, station, currentUserProvider)
	return station


def validate_playlist_rule(
	rule: ActionRule,
	user: Optional[dtos.User] = Depends(subject_user),
	playlistInfo: PlaylistInfo = Depends(get_playlist),
) -> ActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set(UserRoleSphere.Playlist.value)
	if rule.name not in valid_name_set:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{rule.name} is not a valid rule for stations"
			)],
		)
	if playlistInfo.owner and playlistInfo.owner.id == user.id:
		if any(get_playlist_owner_roles((rule.name, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{rule.name} cannot be added to owner"
				)],
			)
	return rule


def validate_playlist_rule_for_remove(
	user: dtos.User | None = Depends(subject_user),
	ruleName: str | None=None,
	playlistInfo: PlaylistInfo = Depends(get_playlist),
) -> str | None:
	if not user:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					"User is required"
				)],
			)
	if not ruleName:
		if playlistInfo.owner and playlistInfo.owner.id == user.id:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"Cannot remove owner from station"
				)],
			)
		return ruleName
	if ruleName == UserRoleDef.PLAYLIST_VIEW.value:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{ruleName} cannot be removed"
			)],
		)
	if playlistInfo.owner and playlistInfo.owner.id == user.id:
		if any(get_playlist_owner_roles((ruleName, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{ruleName} cannot be removed from owner"
				)],
			)
	return ruleName