from typing import (
	Any,
	List,
	Optional,
	Iterator,
	Union,
	Collection
)
from pydantic import validator #pyright: ignore [reportUnknownVariableType]
from pydantic.dataclasses import dataclass as pydanticDataclass
from dataclasses import dataclass, field
from .user_role_def import UserRoleDef, RulePriorityLevel, UserRoleDomain
from .validation_functions import min_length_validator_factory
from .simple_functions import (
	get_duplicates,
	validate_email,
	normalize_opening_slash
)
from .generic_dtos import IdItem
from .action_rule_dtos import (
	ActionRule,
	PathsActionRule,
	StationActionRule,
)
from .absorbent_trie import ChainedAbsorbentTrie


def get_station_owner_rules(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	#STATION_CREATE, STATION_FLIP, STATION_REQUEST, STATION_SKIP
	# left out of here on purpose
	# for STATION_FLIP, STATION_REQUEST, STATION_SKIP, we should have
	#explicit rules with defined limts
	if not scopes or UserRoleDef.STATION_ASSIGN.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_ASSIGN.value,
			priority=RulePriorityLevel.OWNER.value,
		)
	if not scopes or UserRoleDef.STATION_DELETE.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_DELETE.value,
			priority=RulePriorityLevel.OWNER.value,
		)
	if not scopes or UserRoleDef.STATION_EDIT.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_EDIT.value,
			priority=RulePriorityLevel.OWNER.value,
		)
	if not scopes or UserRoleDef.STATION_VIEW.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_VIEW.value,
			priority=RulePriorityLevel.OWNER.value,
		)
	if not scopes or UserRoleDef.STATION_USER_ASSIGN.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_USER_ASSIGN.value,
			priority=RulePriorityLevel.OWNER.value,
		)
	if not scopes or UserRoleDef.STATION_USER_LIST.value in scopes:
		yield StationActionRule(
			UserRoleDef.STATION_USER_LIST.value,
			priority=RulePriorityLevel.OWNER.value,
		)

def get_path_owner_roles(
	ownerDir: Optional[str],
	scopes: Optional[Collection[str]]=None
) -> Iterator[PathsActionRule]:
		if not ownerDir:
			return
		if not scopes or UserRoleDef.PATH_LIST.value in scopes:
			yield PathsActionRule(
				UserRoleDef.PATH_LIST.value,
				priority=RulePriorityLevel.OWNER.value,
				path=ownerDir,
			)
		if not scopes or UserRoleDef.PATH_VIEW.value in scopes:
			yield PathsActionRule(
				UserRoleDef.PATH_VIEW.value,
				priority=RulePriorityLevel.OWNER.value,
				path=ownerDir,
			)
		if not scopes or UserRoleDef.PATH_EDIT.value in scopes:
			yield PathsActionRule(
				UserRoleDef.PATH_EDIT.value,
				priority=RulePriorityLevel.OWNER.value,
				path=ownerDir,
			)
		if not scopes or UserRoleDef.PATH_USER_LIST.value in scopes:
			yield PathsActionRule(
				UserRoleDef.PATH_USER_LIST.value,
				priority=RulePriorityLevel.OWNER.value,
				path=ownerDir,
			)
		if not scopes or UserRoleDef.PATH_USER_ASSIGN.value in scopes:
			yield PathsActionRule(
				UserRoleDef.PATH_USER_ASSIGN.value,
				priority=RulePriorityLevel.OWNER.value,
				path=ownerDir,
			)


@dataclass(frozen=True)
class AccountInfoBase:
	username: str
	email: str
	displayname: Optional[str]=""

@dataclass(frozen=True)
class AccountInfoSecurity(AccountInfoBase):
	roles: List[Union[ActionRule, PathsActionRule]]=field(default_factory=list)
	dirroot: Optional[str]=None

	@property
	def preferredName(self) -> str:
		return self.displayname or self.username

	@property
	def isadmin(self) -> bool:
		return any(
			UserRoleDef.ADMIN.conforms(r.name) \
				for r in self.roles
		)

	def get_permitted_paths_tree(
		self
	) -> ChainedAbsorbentTrie[PathsActionRule]:
		pathTree = ChainedAbsorbentTrie[PathsActionRule](
			(normalize_opening_slash(r.path), r) for r in
			self.roles if isinstance(r, PathsActionRule) \
				and not r.path is None
		)
		pathTree.add("", (r.to_path_rule("") for r in self.roles \
			if type(r) == ActionRule \
				and (UserRoleDomain.Path.conforms(r.name) \
						or r.name == UserRoleDef.ADMIN.value
				)
		), shouldEmptyUpdateTree=False)
		return pathTree

	def get_permitted_paths(
		self
	) -> Iterator[str]:
		pathTree = self.get_permitted_paths_tree()
		yield from (p for p in pathTree.shortest_paths())

	def has_roles(self, *roles: UserRoleDef) -> bool:
		for role in roles:
			if all(r.name != role.value or (r.name == role.value and r.blocked) \
				for r in self.roles
			):
				return False
		return True

@dataclass(frozen=True)
class AccountInfo(AccountInfoSecurity, IdItem):
	...


@dataclass(frozen=True)
class AuthenticatedAccount(AccountInfoSecurity):
	'''
	This AccountInfo is only returned after successful authentication.
	'''
	access_token: str=""
	token_type: str=""
	lifetime: float=0

@pydanticDataclass(frozen=True)
class AccountCreationInfo(AccountInfoSecurity):
	'''
	This AccountInfo is only to the server to create an account.
	Password is clear text here because it hasn't been hashed yet.
	No id property because no id has been assigned yet.
	This class also has validation on several of its properties.
	'''
	password: str=""

	def scrubed_dict(self) -> dict[str, Any]:
		return {
			"username": self.username,
			"email": self.email,
			"displayname": self.displayname,
			"roles": self.roles
		}

	@validator("email")
	def check_email(cls, v: str) -> str:
		valid = validate_email(v) #pyright: ignore [reportUnknownMemberType]
		return valid.email #pyright: ignore [reportGeneralTypeIssues]

	_pass_len = validator( #pyright: ignore [reportUnknownVariableType]
		"password",
		allow_reuse=True
	)(min_length_validator_factory(6, "Password"))


	@validator("roles")
	def are_all_roles_allowed(cls, v: List[str]) -> List[str]:
		roleSet = UserRoleDef.as_set()
		duplicate = next(get_duplicates(
			UserRoleDef.role_dict(r)["name"] for r in v
		), None)
		if duplicate:
			raise ValueError(
				f"{duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		for role in v:
			extracted = UserRoleDef.role_dict(role)["name"]
			if extracted not in roleSet:
				raise ValueError(f"{role} is an illegal role")
		return v

	# @validator("username")
	# def username_valid_chars(cls, v: str) -> str:
	# 	if re.match(r"\d", v):
	# 		raise ValueError("username cannot start with a number")
	# 	if re.match(guidRegx, v):
	# 		msg = "Hey asshole! Stop trying to make your username a guid!"
	# 		raise ValueError(msg)
	# 	if re.search(r"[ \u0000-\u001f\u007f]", v):
	# 		raise ValueError("username contains illegal characters")

	# 	return SavedNameString.format_name_for_save(v)

	# @validator("displayname")
	# def displayName_valid_chars(cls, v: str) -> str:

	# 	if re.match(guidRegx, v):
	# 		msg = "Hey asshole! Stop trying to make your username a guid!"
	# 		raise ValueError(msg)
	# 	cleaned = re.sub(r"[\n\t]+| +"," ", v)
	# 	if re.search(r"[\u0000-\u001f\u007f]", cleaned):
	# 		raise ValueError("username contains illegal characters")

	# 	return SavedNameString.format_name_for_save(cleaned)

@dataclass(frozen=True)
class PasswordInfo:
	oldpassword: str
	newpassword: str

@dataclass(frozen=True)
class UserHistoryActionItem:
	userid: int
	action: str
	timestamp: float

@dataclass(frozen=True)
class StationHistoryActionItem(UserHistoryActionItem):
	stationid: int


@dataclass(frozen=True)
class OwnerInfo(IdItem):
	username: Optional[str]=None
	displayname: Optional[str]=None

OwnerType = Union[OwnerInfo, AccountInfo]