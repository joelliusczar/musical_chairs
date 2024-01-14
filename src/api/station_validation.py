from typing import Optional
from fastapi import (
	Depends,
	HTTPException,
	status,
)
from musical_chairs_libs.dtos_and_utilities import (
	UserRoleDef,
	StationActionRule,
	UserRoleDomain,
	build_error_obj,
	StationInfo,
	get_station_owner_rules,
	AccountInfo
)
from api_dependencies import (
	get_station_by_name_and_owner,
	get_from_query_subject_user
)

def validate_station_rule(
	rule: StationActionRule,
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
) -> StationActionRule:
	if not user:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				"User is required"
			)],
		)
	valid_name_set = UserRoleDef.as_set(UserRoleDomain.Station.value)
	if rule.name not in valid_name_set:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=[build_error_obj(
				f"{rule.name} is not a valid rule for stations"
			)],
		)
	if stationInfo.owner and stationInfo.owner.id == user.id:
		if any(get_station_owner_rules((rule.name, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{rule.name} cannot be added to owner"
				)],
			)
	return rule

def validate_station_rule_for_remove(
	user: Optional[AccountInfo] = Depends(get_from_query_subject_user),
	ruleName: Optional[str]=None,
	stationInfo: StationInfo = Depends(get_station_by_name_and_owner),
) -> Optional[str]:
	if not user:
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					"User is required"
				)],
			)
	if not ruleName:
		if stationInfo.owner and stationInfo.owner.id == user.id:
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
	if stationInfo.owner and stationInfo.owner.id == user.id:
		if any(get_station_owner_rules((ruleName, ))):
			raise HTTPException(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				detail=[build_error_obj(
					f"{ruleName} cannot be removed from owner"
				)],
			)
	return ruleName