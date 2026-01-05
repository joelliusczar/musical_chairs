from .actions_history_query_service import ActionsHistoryQueryService
from .basic_user_provider import BasicUserProvider, Impersonation
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	ActionRule,
	ChainedAbsorbentTrie,
	get_datetime,
	get_path_owner_roles,
	normalize_opening_slash,
	NotLoggedInError,
	PathsActionRule,
	TooManyRequestsError,
	TrackingInfo,
	StationInfo,
	UserRoleDef,
	UserRoleDomain,
	WrongPermissionsError,
)
from musical_chairs_libs.protocols import (
	TrackingInfoProvider,
	UserProvider
)
from .path_rule_service import PathRuleService
from typing import (Literal, Optional, overload)

class CurrentUserProvider(TrackingInfoProvider, UserProvider):

	def __init__(
		self,
		basicUserProvider: BasicUserProvider,
		trackingInfoProvider: TrackingInfoProvider,
		actionsHistoryQueryService: ActionsHistoryQueryService,
		pathRuleService: PathRuleService,
		securityScopes: Optional[set[str]] = None,
	) -> None:
		self.basic_user_provider = basicUserProvider
		self.__path_rule_loaded_user__: Optional[AccountInfo] = None
		self.tracking_info_provider = trackingInfoProvider
		self.actions_history_query_service = actionsHistoryQueryService
		self.get_datetime = get_datetime
		self.security_scopes = securityScopes or set()
		self.path_rule_service = pathRuleService

	@overload
	def current_user(self) -> AccountInfo:
		...

	@overload
	def current_user(self, optional: Literal[False]) -> AccountInfo:
		...

	@overload
	def current_user(self, optional: Literal[True]) -> Optional[AccountInfo]:
		...

	def current_user(self, optional: bool=False) -> Optional[AccountInfo]:
		return self.basic_user_provider.current_user(optional=optional)
	

	def is_loggedIn(self) -> bool:
		return self.basic_user_provider.is_loggedIn()


	def set_user(self, user: AccountInfo):
		self.basic_user_provider.set_user(user)


	def optional_user_id(self) -> Optional[int]:
		return self.basic_user_provider.optional_user_id()


	def tracking_info(self) -> TrackingInfo:
		return self.tracking_info_provider.tracking_info()


	def get_station_user(
		self,
		station: StationInfo,
	)-> Optional[AccountInfo]:
		minScope = (not self.security_scopes or\
			 UserRoleDef.STATION_VIEW.value in self.security_scopes
		)
		user = self.current_user(optional=True)
		if not station.viewsecuritylevel and minScope:
			return user
		if not user:
			raise NotLoggedInError()
		if user.isadmin:
			return user
		scopes = {s for s in self.security_scopes \
			if UserRoleDomain.Station.conforms(s)
		}
		rules = ActionRule.aggregate(
			station.rules,
			filter=lambda r: r.name in scopes
		)
		if not rules:
			raise WrongPermissionsError()
		timeoutLookup = \
			self.actions_history_query_service\
			.calc_lookup_for_when_user_can_next_do_station_action(
				user.id,
				(station,)
			).get(station.id, {})
		for scope in scopes:
			if scope in timeoutLookup:
				whenNext = timeoutLookup[scope]
				if whenNext is None:
					raise WrongPermissionsError()
				if whenNext > 0:
					currentTimestamp = self.get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise TooManyRequestsError(int(timeleft))
		userDict = user.model_dump()
		userDict["roles"] = rules
		return AccountInfo(**userDict)
	

	def get_rate_limited_user(self) -> AccountInfo:
		user = self.current_user()
		if user.isadmin:
			return user
		scopeSet = self.security_scopes
		rules = ActionRule.sorted((r for r in user.roles if r.name in scopeSet))
		if not rules and scopeSet:
			raise WrongPermissionsError()
		timeoutLookup = \
			self.actions_history_query_service\
				.calc_lookup_for_when_user_can_next_do_action(
					user.id,
					rules
				)
		for scope in scopeSet:
			if scope in timeoutLookup:
				whenNext = timeoutLookup[scope]
				if whenNext is None:
					raise WrongPermissionsError()
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise TooManyRequestsError(int(timeleft))
		return user


	def impersonate(self, user: AccountInfo) -> Impersonation:
		return self.basic_user_provider.impersonate(user)


	def check_if_can_use_path(
		self,
		scopes: list[str],
		prefix: str,
		user: AccountInfo,
		userPrefixTrie: ChainedAbsorbentTrie[PathsActionRule],
	):
		scopeSet = scopes
		rules = ActionRule.sorted(
			(r for i in userPrefixTrie.values(normalize_opening_slash(prefix)) \
				for r in i if r.name in scopeSet)
		)
		if not rules and scopes:
			raise WrongPermissionsError(f"{prefix} not found")
		timeoutLookup = \
			self.actions_history_query_service\
				.calc_lookup_for_when_user_can_next_do_action(
					user.id,
					rules
				)
		for scope in scopeSet:
			if scope in timeoutLookup:
				whenNext = timeoutLookup[scope]
				if whenNext is None:
					raise WrongPermissionsError()
				if whenNext > 0:
					currentTimestamp = get_datetime().timestamp()
					timeleft = whenNext - currentTimestamp
					raise TooManyRequestsError(int(timeleft))

	@overload
	def get_path_rule_loaded_current_user(self) -> AccountInfo:
		...

	@overload
	def get_path_rule_loaded_current_user(
		self,
		optional: Literal[False]
	) -> AccountInfo:
		...

	@overload
	def get_path_rule_loaded_current_user(
		self,
		optional: Literal[True]
	) -> Optional[AccountInfo]:
		...

	def get_path_rule_loaded_current_user(
		self,
		optional: bool = False
	) -> Optional[AccountInfo]:
		user = self.current_user(optional=optional)
		if not user:
			return None
		if self.__path_rule_loaded_user__  \
			and user.id == self.__path_rule_loaded_user__.id\
		:
			return self.__path_rule_loaded_user__
		scopes = {s for s in self.security_scopes \
			if UserRoleDomain.Path.conforms(s)
		}
		if user.isadmin:
			return user
		if not scopes and self.security_scopes:
			raise WrongPermissionsError()
		rules = ActionRule.aggregate(
			user.roles,
			(p for p in self.path_rule_service.get_paths_user_can_see()),
			(p for p in get_path_owner_roles(normalize_opening_slash(user.dirroot)))
		)
		roleNameSet = {r.name for r in rules}
		if any(s for s in scopes if s not in roleNameSet):
			raise WrongPermissionsError()
		userDict = user.model_dump()
		userDict["roles"] = rules
		resultUser = AccountInfo(
			**userDict,
		)
		self.__path_rule_loaded_user__ = resultUser
		return resultUser


