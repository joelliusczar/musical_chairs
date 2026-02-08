import musical_chairs_libs.dtos_and_utilities as dtos
from typing import Optional
from fastapi import (
	Depends,
	HTTPException,
	status,
)
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	UserRoleSphere,
	build_error_obj,
	PlaylistInfo,
	get_playlist_owner_roles,
	ActionRule,
)
from api_dependencies import (
	get_playlist_by_name_and_owner,
	subject_user
)

def validate_playlist_rule(
	rule: ActionRule,
	user: Optional[dtos.User] = Depends(subject_user),
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
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
	playlistInfo: PlaylistInfo = Depends(get_playlist_by_name_and_owner),
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