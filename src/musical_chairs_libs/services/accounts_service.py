#pyright: reportMissingTypeStubs=false
from typing import (
	Iterable,
	Iterator,
	Optional,
	Tuple,
)
from musical_chairs_libs.dtos_and_utilities import (
	AccountInfo,
	AccountCreationInfo,
	AccountInfoBase,
	PasswordInfo,
	ActionRule,
)

from .account_access_service import AccountAccessService
from .account_management_service import AccountManagementService
from .account_token_creator import AccountTokenCreator



class AccountsService:

	def __init__(
		self,
		accountAccessService: AccountAccessService,
		accountManagementService: AccountManagementService,
		accountTokenCreator: AccountTokenCreator,
	) -> None:
		self.account_access_service = accountAccessService
		self.account_management_service = accountManagementService
		self.account_token_creator = accountTokenCreator


	def get_account_for_login(
		self,
		username: str
	) -> Tuple[Optional[AccountInfo], Optional[bytes]]:
		return self.account_access_service.get_account_for_login(username)

	def authenticate_user(self,
		username: str,
		guess: bytes
	) -> Optional[AccountInfo]:
		return self.account_access_service.authenticate_user(username, guess)

	def create_account(self, accountInfo: AccountCreationInfo) -> AccountInfo:
		return self.account_management_service.create_account(accountInfo)


	def remove_roles_for_user(
		self,
		userId: int,
		roles: Iterable[str]
	) -> int:
		return self.account_management_service.remove_roles_for_user(userId, roles)


	def save_roles(
		self,
		userId: Optional[int],
		roles: Iterable[ActionRule]
	) -> Iterable[ActionRule]:
		return self.account_management_service.save_roles(userId, roles)


	def create_access_token(
		self,
		user: AccountInfo,
	) -> str:
		return self.account_token_creator.create_access_token(user)

	def has_expired(self, timestamp: float) -> bool:
		return self.account_access_service.has_expired(timestamp)

	def get_user_from_token(
		self,
		token: str
	) -> Tuple[Optional[AccountInfo], float]:
		return self.get_user_from_token(token)


	def is_username_used(
		self,
		username: str,
		loggedInUser: Optional[AccountInfo]=None
	) -> bool:
		return self.account_management_service.is_username_used(username)

	def is_email_used(
		self,
		email: str,
		loggedInUser: Optional[AccountInfo]=None
	) -> bool:
		return self.account_management_service.is_email_used(email)

	def get_accounts_count(self) -> int:
		return self.account_management_service.get_accounts_count()

	def get_account_list(
		self,
		searchTerm: Optional[str]=None,
		page: int = 0,
		pageSize: Optional[int]=None
	) -> Iterator[AccountInfo]:
		return self.account_management_service.get_account_list(
			searchTerm,
			page,
			pageSize
		)


	def get_account_for_edit(
		self,
		key: int | str
	) -> AccountInfo | None:
		return self.account_management_service.get_account_for_edit(key)

	def update_account_general_changes(
		self,
		updatedInfo: AccountInfoBase,
	) -> AccountInfo:
		return self.account_management_service.update_account_general_changes(
			updatedInfo
		)

	def update_password(
		self,
		passwordInfo: PasswordInfo,
	) -> bool:
		return self.account_management_service.update_password(passwordInfo)

	def get_site_rule_users(
		self,
		userId: Optional[int]=None,
		owner: Optional[AccountInfo]=None
	) -> Iterator[AccountInfo]:
		return self.account_management_service.get_site_rule_users(userId, owner)

	def add_user_rule(
		self,
		addedUserId: int,
		rule: ActionRule,
	) -> ActionRule:
		return self.account_management_service.add_user_rule(addedUserId, rule)



	def remove_user_site_rule(
		self,
		userId: int,
		ruleName: Optional[str],
	):
		return self.account_management_service.remove_user_site_rule(
			userId,
			ruleName
		)