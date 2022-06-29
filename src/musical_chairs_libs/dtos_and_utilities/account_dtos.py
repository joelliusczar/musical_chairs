from typing import\
	List
from pydantic import BaseModel, validator
from .user_role_def import UserRoleDef
from .validation_functions import min_length_validator_factory
from .simple_functions import get_duplicates, validate_email

class AccountInfoBase(BaseModel):
	username: str
	displayName: str=""
	email: str
	roles: List[str]=[]

	@property
	def preferredName(self) -> str:
		return self.displayName or self.username

	@property
	def isAdmin(self) -> bool:
		return UserRoleDef.ADMIN.value in \
			(UserRoleDef.extract_role_segments(r)[0] for r in self.roles)

class AccountInfo(AccountInfoBase):
	id: int

class AuthenticatedAccount(AccountInfoBase):
	'''
	This AccountInfo is only returned after successful authentication.
	'''
	access_token: str
	token_type: str
	lifetime: int

class AccountCreationInfo(AccountInfoBase):
	'''
	This AccountInfo is only to the server to create an account.
	Password is clear text here because it hasn't been hashed yet.
	No id property because no id has been assigned yet.
	This class also has validation on several of its properties.
	'''
	password: str

	@validator("email")
	def check_email(cls, v: str) -> str:
		valid = validate_email(v) #pyright: ignore reportUnknownMemberType
		return valid.email #pyright: ignore reportUnknownMemberType

	_pass_len = validator(
		"password",
		allow_reuse=True
	)(min_length_validator_factory(6, "Password"))


	@validator("roles")
	def are_all_roles_allowed(cls, v: List[str]) -> List[str]:
		roleSet = UserRoleDef.as_set()
		duplicate = next(get_duplicates(
			UserRoleDef.extract_role_segments(r)[0] for r in v
		), None)
		if duplicate:
			raise ValueError(
				f"{duplicate[0]} has been added {duplicate[1]} times "
				"but it is only legal to add it once."
			)
		for role in v:
			extracted = UserRoleDef.extract_role_segments(role)[0]
			if extracted not in roleSet:
				raise ValueError(f"{role} is an illegal role")
		return v

class RoleInfo(BaseModel):
	userPk: int
	role: str
	creationTimestamp: float