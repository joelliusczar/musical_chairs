from typing import (
	Any,
	List,
	Optional,
	Iterator,
	Union,
	Collection,
	cast
)
from pydantic import (
	field_validator,
	field_serializer,
	SerializationInfo,
	SerializeAsAny,
	Field
)
from .user_role_def import UserRoleDef, RulePriorityLevel, UserRoleDomain
from .validation_functions import min_length_validator_factory
from .simple_functions import (
	asdict,
	get_duplicates,
	validate_email,
	normalize_opening_slash,
	normalize_closing_slash
)
from .generic_dtos import FrozenIdItem, FrozenBaseClass
from .action_rule_dtos import (
	ActionRule,
)
from .absorbent_trie import ChainedAbsorbentTrie

#STATION_CREATE, STATION_FLIP, STATION_REQUEST, STATION_SKIP
	# left out of here on purpose
	# for STATION_FLIP, STATION_REQUEST, STATION_SKIP, we should have
	#explicit rules with defined limts
station_owner_rules = [
	UserRoleDef.STATION_ASSIGN,
	UserRoleDef.STATION_DELETE,
	UserRoleDef.STATION_EDIT,
	UserRoleDef.STATION_VIEW,
	UserRoleDef.STATION_USER_ASSIGN,
	UserRoleDef.STATION_USER_LIST
]

def get_station_owner_rules(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	for rule in station_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				domain=UserRoleDomain.Station.value
			)

path_owner_rules = [
	UserRoleDef.PATH_DELETE,
	UserRoleDef.PATH_DOWNLOAD,
	UserRoleDef.PATH_EDIT,
	UserRoleDef.PATH_LIST,
	UserRoleDef.PATH_VIEW,
	UserRoleDef.PATH_MOVE,
	UserRoleDef.PATH_USER_LIST,
	UserRoleDef.PATH_USER_ASSIGN,
	UserRoleDef.PATH_UPLOAD,
]

def get_path_owner_roles(
	ownerDir: Optional[str],
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
		if not ownerDir:
			return
		for rule in path_owner_rules:
			if not scopes or rule.value in scopes:
				if rule == UserRoleDef.PATH_DOWNLOAD:
					yield ActionRule(
						name=rule.value,
						priority=RulePriorityLevel.USER.value,
						domain=UserRoleDomain.Path.value,
						path=ownerDir,
						span=60,
						count=12
					)
					continue
				yield ActionRule(
						name=rule.value,
						priority=RulePriorityLevel.OWNER.value,
						domain=UserRoleDomain.Path.value,
						path=ownerDir,
					)

#create left out on purpose
playlist_owner_rules = [
	UserRoleDef.PLAYLIST_VIEW,
	UserRoleDef.PLAYLIST_EDIT,
	UserRoleDef.PLAYLIST_DELETE,
	UserRoleDef.PLAYLIST_ASSIGN,
	UserRoleDef.PLAYLIST_USER_ASSIGN,
	UserRoleDef.PLAYLIST_USER_LIST,
]

def get_playlist_owner_roles(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	for rule in playlist_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				domain=UserRoleDomain.Playlist.value
			)

album_owner_rules = [
	UserRoleDef.ALBUM_EDIT,
]

def get_album_owner_roles(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	for rule in album_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				domain=UserRoleDomain.Album.value
			)

artist_owner_rules = [
	UserRoleDef.ARTIST_EDIT,
]

def get_artist_owner_roles(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	for rule in artist_owner_rules:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.OWNER.value,
				domain=UserRoleDomain.Artist.value
			)

starting_user_roles = [
	UserRoleDef.PLAYLIST_CREATE,
	UserRoleDef.STATION_CREATE,
	UserRoleDef.ARTIST_CREATE,
	UserRoleDef.ALBUM_CREATE,
]

def get_starting_site_roles(
	scopes: Optional[Collection[str]]=None
) -> Iterator[ActionRule]:
	for rule in starting_user_roles:
		if not scopes or rule.value in scopes:
			yield ActionRule(
				name=rule.value,
				priority=RulePriorityLevel.USER.value,
				span=60,
				count=1
			)

class AccountInfoBase(FrozenBaseClass):
	username: str
	email: str
	displayname: Optional[str]=""

class AccountInfoSecurity(AccountInfoBase):
	roles: List[Union[ActionRule, ActionRule]]=cast(
		List[Union[ActionRule, ActionRule]],Field(default_factory=list)
	)
	dirroot: Optional[str]=None

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

	def get_permitted_paths_tree(
		self
	) -> ChainedAbsorbentTrie[ActionRule]:
		pathTree = ChainedAbsorbentTrie[ActionRule](
			(normalize_opening_slash(r.path), r) for r in
			self.roles if r.domain == UserRoleDomain.Path.value \
				and r.path is not None
		)
		pathTree.add("/", (
			ActionRule(**asdict(r, exclude={"path"}), path = "/") 
			for r in self.roles \
			if r.path is None and (UserRoleDomain.Path.conforms(r.name) \
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
		if self.isadmin:
			return True
		for role in roles:
			if all(r.name != role.value or (r.name == role.value and r.blocked) \
				for r in self.roles
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


class AccountInfo(AccountInfoSecurity, FrozenIdItem):
	...


class AuthenticatedAccount(AccountInfoSecurity):
	'''
	This AccountInfo is only returned after successful authentication.
	'''
	id: int
	access_token: str=""
	token_type: str=""
	lifetime: float=0
	login_timestamp: float=0


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

class PasswordInfo(FrozenBaseClass):
	oldpassword: str
	newpassword: str

class UserHistoryActionItem(FrozenBaseClass):
	userid: int
	action: str
	timestamp: float

class StationHistoryActionItem(UserHistoryActionItem):
	stationid: int


class OwnerInfo(FrozenIdItem):
	username: Optional[str]=None
	displayname: Optional[str]=None

OwnerType = Union[OwnerInfo, AccountInfo]