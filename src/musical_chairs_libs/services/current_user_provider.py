from .basic_user_provider import BasicUserProvider
from musical_chairs_libs.dtos_and_utilities import (
	ActionRule,
	InternalUser,
	TrackingInfo,
	get_datetime,
	get_path_owner_roles,
	normalize_opening_slash,
	UserRoleSphere,
	WrongPermissionsError,
)
from musical_chairs_libs.protocols import (
	TrackingInfoProvider,
	UserProvider
)
from .path_rule_service import PathRuleService
from typing import (Any, Literal, overload)

class CurrentUserProvider(TrackingInfoProvider, UserProvider):

	def __init__(
		self,
		basicUserProvider: BasicUserProvider,
		trackingInfoProvider: TrackingInfoProvider,
		pathRuleService: PathRuleService,
		securityScopes: set[str] | None = None,
	) -> None:
		self.basic_user_provider = basicUserProvider
		self.__path_rule_loaded_user__: InternalUser | None = None
		self.tracking_info_provider = trackingInfoProvider
		self.get_datetime = get_datetime
		self.security_scopes = securityScopes or set()
		self.path_rule_service = pathRuleService

	@overload
	def current_user(self) -> InternalUser:
		...

	@overload
	def current_user(self, optional: Literal[False]) -> InternalUser:
		...

	@overload
	def current_user(self, optional: Literal[True]) -> InternalUser | None:
		...

	def current_user(self, optional: bool=False) -> InternalUser | None:
		return self.basic_user_provider.current_user(optional=optional)
	

	def is_loggedIn(self) -> bool:
		return self.basic_user_provider.is_loggedIn()


	def set_session_user(self, user: InternalUser):
		self.basic_user_provider.set_session_user(user)


	def optional_user_id(self) -> int | None:
		return self.basic_user_provider.optional_user_id()


	def tracking_info(self) -> TrackingInfo:
		return self.tracking_info_provider.tracking_info()


	def visitor_id(self) -> int:
		return self.tracking_info_provider.visitor_id()


	def impersonate(self, user: InternalUser) -> Any:
		return self.basic_user_provider.impersonate(user)


	@overload
	def get_path_rule_loaded_current_user(self) -> InternalUser:
		...

	@overload
	def get_path_rule_loaded_current_user(
		self,
		optional: Literal[False]
	) -> InternalUser:
		...

	@overload
	def get_path_rule_loaded_current_user(
		self,
		optional: Literal[True]
	) -> InternalUser | None:
		...

	def get_path_rule_loaded_current_user(
		self,
		optional: bool = False
	) -> InternalUser | None:
		user = self.current_user(optional=optional)
		if not user:
			return None
		if self.__path_rule_loaded_user__  \
			and user.id == self.__path_rule_loaded_user__.id\
		:
			return self.__path_rule_loaded_user__
		scopes = {s for s in self.security_scopes \
			if UserRoleSphere.Path.conforms(s)
		}
		if user.isadmin:
			return user
		if not scopes and self.security_scopes:
			raise WrongPermissionsError()
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.path_rule_service.get_paths_user_can_see(user.id)),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
		)
		roleNameSet = {r.name for r in rules}
		if any(s for s in scopes if s not in roleNameSet):
			raise WrongPermissionsError()
		userDict = user.model_dump()
		userDict["roles"] = rules
		resultUser = InternalUser(
			**userDict,
		)
		self.__path_rule_loaded_user__ = resultUser
		return resultUser


