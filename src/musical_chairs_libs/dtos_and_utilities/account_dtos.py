from typing import (
	Any,
	List,
	Optional,
	Iterator,
	Union,
	Iterable
)
from pydantic import validator #pyright: ignore [reportUnknownVariableType]
from pydantic.dataclasses import dataclass as pydanticDataclass
from dataclasses import dataclass, field
from .user_role_def import UserRoleDef, UserRoleDomain, RulePriorityLevel
from .validation_functions import min_length_validator_factory
from .simple_functions import (
	get_duplicates,
	validate_email,
	normalize_opening_slash
)
from .generic_dtos import IdItem
from .action_rule_dtos import (ActionRule, PathsActionRule)
from .absorbent_trie import AbsorbentTrie
from itertools import chain

def get_station_owner_rules() -> Iterator[ActionRule]:
	#STATION_CREATE, STATION_FLIP, STATION_REQUEST, STATION_SKIP
	# left out of here on purpose
	# for STATION_FLIP, STATION_REQUEST, STATION_SKIP, we should have
	#explicit rules with defined limts
	yield ActionRule(
		UserRoleDef.STATION_ASSIGN.value,
		priority=RulePriorityLevel.OWNER.value,
		domain=UserRoleDomain.Station
	)
	yield ActionRule(
		UserRoleDef.STATION_DELETE.value,
		priority=RulePriorityLevel.OWNER.value,
		domain=UserRoleDomain.Station
	)
	yield ActionRule(
		UserRoleDef.STATION_EDIT.value,
		priority=RulePriorityLevel.OWNER.value,
		domain=UserRoleDomain.Station
	)

def get_path_owner_roles(ownerDir: Optional[str]) -> Iterator[PathsActionRule]:
		if not ownerDir:
			return
		yield PathsActionRule(
			UserRoleDef.PATH_LIST.value,
			priority=RulePriorityLevel.OWNER.value,
			path=ownerDir,
			domain=UserRoleDomain.Path
		)
		yield PathsActionRule(
			UserRoleDef.PATH_VIEW.value,
			priority=RulePriorityLevel.OWNER.value,
			path=ownerDir,
			domain=UserRoleDomain.Path
		)
		yield PathsActionRule(
			UserRoleDef.PATH_EDIT.value,
			priority=RulePriorityLevel.OWNER.value,
			path=ownerDir,
			domain=UserRoleDomain.Path
		)
		yield PathsActionRule(
			UserRoleDef.PATH_DOWNLOAD.value,
			priority=RulePriorityLevel.OWNER.value,
			path=ownerDir,
			domain=UserRoleDomain.Path
		)

@dataclass(frozen=True)
class AccountInfoBase:
	username: str
	email: str
	displayName: Optional[str]=""

@dataclass(frozen=True)
class AccountInfoSecurity(AccountInfoBase):
	roles: List[Union[ActionRule, PathsActionRule]]=field(default_factory=list)
	dirRoot: Optional[str]=None

	@property
	def preferredName(self) -> str:
		return self.displayName or self.username

	@property
	def isAdmin(self) -> bool:
		return any(
			UserRoleDef.ADMIN.conforms(r.name) and r.domain == UserRoleDomain.Site \
				for r in self.roles
		)

	def get_permitted_paths_tree(
		self,
		scopes: Union[str, Iterable[str]]
	) -> AbsorbentTrie[Any]:
		scopeSet = set([scopes] if type(scopes) == str else scopes)
		pathsGen = (normalize_opening_slash(r.path) for r in chain(
				self.roles,
				get_path_owner_roles(normalize_opening_slash(self.dirRoot))
			) if isinstance(r, PathsActionRule) and r.name in scopeSet \
					and not r.path is None
			)
		pathTree = AbsorbentTrie[Any](p for p in pathsGen if not p is None)
		return pathTree

	def get_permitted_paths(
		self,
		scopes: Union[str, Iterable[str]]
	) -> Iterator[str]:
		pathTree = self.get_permitted_paths_tree(scopes)
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
			"displayName": self.displayName,
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


@dataclass(frozen=True)
class PasswordInfo:
	oldPassword: str
	newPassword: str

@dataclass(frozen=True)
class UserHistoryActionItem:
	userId: int
	action: str
	timestamp: float