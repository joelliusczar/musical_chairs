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
from .user_role_def import UserRoleDef
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates, validate_email
from .generic_dtos import IdItem
from .action_rule_dtos import (ActionRule, PathsActionRule)
from .absorbent_trie import AbsorbentTrie


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
		return any(r.conforms(UserRoleDef.ADMIN.value) for r in self.roles)

	def get_permitted_paths(
		self,
		scopes: Union[str, Iterable[str]]
	) -> Iterator[str]:
		scopeSet = set([scopes] if type(scopes) == str else scopes)
		pathsGen = (p for pl in \
			(r for r in self.roles \
				if isinstance(r, PathsActionRule) and r.name in scopeSet
			) for p in pl.paths
		)
		pathTree = AbsorbentTrie[Any](pathsGen)
		yield from (p for p in pathTree.shortest_paths())




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
class StationUserInfo(AccountInfo):
	stationId: Optional[int]=None


@dataclass(frozen=True)
class UserHistoryActionItem:
	userId: int
	action: str
	timestamp: float