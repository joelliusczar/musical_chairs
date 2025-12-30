from .actions_history_query_service import ActionsHistoryQueryService
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	ActionRule,
	get_datetime,
	NotLoggedInError,
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
from typing import (Any, Optional)

class CurrentUserProvider(TrackingInfoProvider, UserProvider):

	def __init__(self,
		user: Optional[AccountInfo],
		trackingInfoProvider: TrackingInfoProvider,
		actionsHistoryQueryService: ActionsHistoryQueryService,
		securityScopes: Optional[set[str]] = None
	) -> None:
		self.__user__ = user
		self.tracking_info_provider = trackingInfoProvider
		self.actions_history_query_service = actionsHistoryQueryService
		self.get_datetime = get_datetime
		self.security_scopes = securityScopes or set()


	def current_user(self) -> AccountInfo:
		if self.__user__:
			return self.__user__
		raise RuntimeError(
			"User was not supplied to this instance of CurrentUserProvider"
		)

	def set_user(self, user: AccountInfo):
		self.__user__ = user

	def optional_user(self) -> Optional[AccountInfo]:
		return self.__user__


	def optional_user_id(self) -> Optional[int]:
		return self.__user__.id if self.__user__ else None


	def tracking_info(self) -> TrackingInfo:
		return self.tracking_info_provider.tracking_info()


	def get_station_user(
		self,
		station: StationInfo,
	)-> Optional[AccountInfo]:
		minScope = (not self.security_scopes or\
			 UserRoleDef.STATION_VIEW.value in self.security_scopes
		)
		user = self.optional_user()
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
	

	def get_scoped_user(self) -> AccountInfo:
		user = self.current_user()
		if user.isadmin:
			return user
		for scope in self.security_scopes:
			if not any(r for r in user.roles if r.name == scope):
				raise WrongPermissionsError()
		return user
	
	def impersonate(self, user: AccountInfo) -> "Impersonation":
		return Impersonation(self, user)
	
	
class Impersonation:

	def __init__(
		self,
		userProvider: "CurrentUserProvider",
		user: AccountInfo,
	) -> None:
		self.prev_user = userProvider.optional_user()
		self.user_provider = userProvider
		self.impersonated = user

	def __enter__(
		self,
	):
		self.user_provider.__user__ = self.impersonated

	def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any):
		self.user_provider.__user__ = self.prev_user