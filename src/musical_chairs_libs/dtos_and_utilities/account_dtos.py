from typing import (
	List,
	cast
)
from pydantic import (
	BaseModel as MCBaseClass,
	field_validator,
	field_serializer,
	SerializationInfo,
	SerializeAsAny,
	Field
)
from .constants.constants import public_token_prefix
from .user_role_def import UserRoleDef, UserRoleSphere
from .validation_functions import min_length_validator_factory
from .simple_functions import (
	get_duplicates,
	validate_email,
	normalize_opening_slash,
	normalize_closing_slash
)
from .generic_dtos import FrozenIdItem, FrozenBaseClass, RuledEntity, IdItem
from .action_rule_dtos import (
	ActionRule,
)



class AccountInfoUpdate(FrozenBaseClass):
	username: str
	email: str
	displayname: str |None=""


class AccountInfoBase(FrozenBaseClass):
	username: str
	displayname: str | None=""


class AccountInfo(AccountInfoBase, FrozenIdItem):
	...


class User(AccountInfoBase, FrozenIdItem):
	publictoken: str


class RoledUserMixin(AccountInfoBase):
	roles: List[ActionRule]=cast(
		List[ActionRule],Field(default_factory=list)
	)
	dirroot: str | None=None

	@property
	def preferredName(self) -> str:
		return self.displayname or self.username

	@property
	def dirrootOrDefault(self) -> str:
		return normalize_opening_slash(normalize_closing_slash(
			self.dirroot or self.username
		))

	@property
	def isadmin(self) -> bool:
		return any(
			UserRoleDef.ADMIN.conforms(r.name) \
				for r in self.roles
		)


	def has_site_roles(self, *roles: UserRoleDef) -> bool:
		if self.isadmin:
			return True
		for role in roles:
			if all(r.name != role.value or (r.name == role.value and r.blocked) \
				for r in \
					(r2 for r2 in self.roles if r2.sphere == UserRoleSphere.Site.value)
			):
				return False
		return True


	@field_serializer(
		"roles",
		return_type=SerializeAsAny[List[ActionRule]]
	)
	def serialize_roles(
		self,
		value: List[ActionRule],
		_info: SerializationInfo
	):
		return value


	def to_user(self) -> User:
		return User(
			**self.model_dump(
				exclude={"hiddentoken"}
			)
		)


class RoledUser(RoledUserMixin, FrozenIdItem):
	publictoken: str
	dirroot: str | None = None



class EmailableUser(RoledUserMixin, FrozenIdItem):
	publictoken: str
	dirroot: str | None = None
	email: str

	def to_role_user(self) -> RoledUser:
		return RoledUser(
			**self.model_dump(
				exclude={"hiddentoken", "email"}
			)
		)
	


class InternalUser(RoledUserMixin, FrozenIdItem):
	publictoken: str
	dirroot: str | None = None
	email: str
	hiddentoken: str

	def to_roled_user(self) -> RoledUser:
		return RoledUser(
			**self.model_dump(
				exclude={"hiddentoken", "email"}
			)
		)

	def to_emailable_user(self) -> EmailableUser:
		return EmailableUser(
			**self.model_dump(exclude={"hiddentoken"})
		)



class AuthenticatedAccount(RoledUser):
	'''
	This AccountInfo is only returned after successful authentication.
	'''
	id: int
	access_token: str=""
	token_type: str=""
	lifetime: float=0
	login_timestamp: float=0


class AccountCreationInfo(RoledUserMixin):
	'''
	This AccountInfo is only to the server to create an account.
	Password is clear text here because it hasn't been hashed yet.
	No id property because no id has been assigned yet.
	This class also has validation on several of its properties.
	'''
	password: str=""
	email: str


	@field_validator("username")
	def check_username(cls, v: str) -> str:
		if not v:
			raise ValueError("Username is empty")
		if v.startswith(public_token_prefix):
			raise ValueError(f"Username cannot start with '{public_token_prefix}'")
		vSet = set(v[::])
		if any({"/"} & vSet):
			raise ValueError(f"Illegal characters in username: {{{"/"} & vSet}}")
		return v

	@field_validator("email")
	def check_email(cls, v: str) -> str:
		valid = validate_email(v)
		if not valid or not valid.email:
			raise ValueError("Email is null")
		return valid.email #pyright: ignore [reportGeneralTypeIssues]

	_pass_len = field_validator( #pyright: ignore [reportUnknownVariableType]
		"password"
	)(min_length_validator_factory(6, "Password"))


	@field_validator("roles")
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


class PasswordInfo(FrozenBaseClass):
	oldpassword: str
	newpassword: str


OwnerType = User


class OwnedEntity(MCBaseClass):
	owner: OwnerType=Field(frozen=False)


class RuledOwnedEntity(IdItem, OwnedEntity, RuledEntity):
	...