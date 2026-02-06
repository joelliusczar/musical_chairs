from .domain_user_service import DomainUserService
from musical_chairs_libs.dtos_and_utilities import (
	get_station_owner_rules,
	StationInfo,
	AccountInfo,
	ActionRule,
	UserRoleSphere,
)
from typing import (
	Iterator,
	Optional,
)


class StationsUsersService:

	def __init__(
		self,
		domainUserService: DomainUserService
	) -> None:
		self.domain_user_service = domainUserService


	def add_user_rule_to_station(
		self,
		addedUserId: int,
		stationId: int,
		rule: ActionRule
	) -> ActionRule:
		return self.domain_user_service.add_domain_rule_to_user(
			addedUserId,
			UserRoleSphere.Station.value,
			str(stationId),
			rule
		)

	
	def get_station_users(
		self,
		station: StationInfo,
	) -> Iterator[AccountInfo]:
		return self.domain_user_service.get_domain_users(
			station,
			UserRoleSphere.Station,
			get_station_owner_rules
		)


	def remove_user_rule_from_station(
		self,
		userId: int,
		stationId: int,
		ruleName: Optional[str]
	):
		self.domain_user_service.remove_domain_rule_from_user(
			userId,
			UserRoleSphere.Station.value,
			str(stationId),
			ruleName
		)