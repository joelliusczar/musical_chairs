from enum import Enum
from typing import (
	Union,
	Set,
	Tuple,
	Optional
)
from .type_aliases import (
	s2sDict,
	simpleDict
)
from .simple_functions import role_dict
from .constants import UserRoleSphere


class RulePriorityLevel(Enum):
	NONE = 0
	PUBLIC = 0
	ANY_USER = 9
	USER = 10
	#rule_user is for a site wide privilage that requires some sort of explicit grant
	RULED_USER = 19
	SITE = 20
	FRIEND_USER = 29 # not used
	FRIEND_STATION = 30
	INVITED_USER = 39
	# STATION_PATH should be able to overpower INVITED_USER
	STATION_PATH = 40
	OWENER_USER = 49
	OWNER = 50
	#only admins should be able to see these items
	LOCKED = 59
	SUPER = 60


class UserRoleDef(Enum):
	ADMIN = "admin"
	USER_USER_ASSIGN = f"{UserRoleSphere.User.value}:userassign"
	USER_USER_LIST = f"{UserRoleSphere.User.value}:userlist"
	SITE_PLACEHOLDER = f"{UserRoleSphere.Site.value}:placeholder"
	USER_EDIT = f"{UserRoleSphere.Site.value}:useredit"
	ALBUM_CREATE = f"{UserRoleSphere.Album.value}:create"
	ALBUM_EDIT = f"{UserRoleSphere.Album.value}:edit"
	ALBUM_VIEW_ALL = f"{UserRoleSphere.Album.value}:view_all"
	ARTIST_CREATE = f"{UserRoleSphere.Artist.value}:create"
	ARTIST_EDIT = f"{UserRoleSphere.Artist.value}:edit"
	ARTIST_VIEW_ALL = f"{UserRoleSphere.Artist.value}:view_all"
	STATION_VIEW = f"{UserRoleSphere.Station.value}:view"
	STATION_CREATE = f"{UserRoleSphere.Station.value}:create"
	STATION_EDIT = f"{UserRoleSphere.Station.value}:edit"
	STATION_DELETE = f"{UserRoleSphere.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleSphere.Station.value}:request"
	STATION_FLIP = f"{UserRoleSphere.Station.value}:flip"
	STATION_SKIP = f"{UserRoleSphere.Station.value}:skip"
	STATION_ASSIGN = f"{UserRoleSphere.Station.value}:assign"
	STATION_USER_ASSIGN = f"{UserRoleSphere.Station.value}:userassign"
	STATION_USER_LIST = f"{UserRoleSphere.Station.value}:userlist"
	USER_LIST = f"{UserRoleSphere.User.value}:list"
	USER_IMPERSONATE = f"{UserRoleSphere.User.value}:impersonate"
	PATH_LIST = f"{UserRoleSphere.Path.value}:list"
	PATH_EDIT = f"{UserRoleSphere.Path.value}:edit"
	PATH_DELETE = f"{UserRoleSphere.Path.value}:delete"
	PATH_VIEW = f"{UserRoleSphere.Path.value}:view"
	PATH_USER_ASSIGN = f"{UserRoleSphere.Path.value}:userassign"
	PATH_USER_LIST = f"{UserRoleSphere.Path.value}:userlist"
	PATH_DOWNLOAD = f"{UserRoleSphere.Path.value}:download"
	PATH_UPLOAD = f"{UserRoleSphere.Path.value}:upload"
	PATH_MOVE = f"{UserRoleSphere.Path.value}:move"
	PLAYLIST_VIEW = f"{UserRoleSphere.Playlist.value}:view"
	PLAYLIST_CREATE = f"{UserRoleSphere.Playlist.value}:create"
	PLAYLIST_EDIT = f"{UserRoleSphere.Playlist.value}:edit"
	PLAYLIST_DELETE = f"{UserRoleSphere.Playlist.value}:delete"
	PLAYLIST_ASSIGN = f"{UserRoleSphere.Playlist.value}:assign"
	PLAYLIST_USER_ASSIGN = f"{UserRoleSphere.Playlist.value}:userassign"
	PLAYLIST_USER_LIST = f"{UserRoleSphere.Playlist.value}:userlist"

	def __call__(self, **kwargs: Union[str, int]) -> str:
		return self.modded_value(**kwargs)

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)

	@property
	def nameValue(self):
		return self.value

	@staticmethod
	def as_set(sphere: Optional[str]=None) -> Set[str]:
		return {r.value for r in UserRoleDef \
			if not sphere or r.value.startswith(sphere)}

	@staticmethod
	def role_dict(role: str) -> s2sDict:
		return role_dict(role)

	@staticmethod
	def role_str(roleDict: simpleDict) -> str:
		return ";".join(sorted(f"{k}={v}" for k,v in roleDict.items() if v != ""))

	@staticmethod
	def extract_role_segments(role: str) -> Tuple[str, int]:
		roleDict = UserRoleDef.role_dict(role)
		if "name" in roleDict:
			nameValue = roleDict["name"]
			mod = int(roleDict["mod"]) if "mod" in roleDict else -1
			return (nameValue, mod)
		return ("", 0)

	def modded_value(
		self,
		**kwargs: Optional[Union[str, int]]
	) -> str:
		if "name" in kwargs and kwargs["name"] != self.value:
			raise RuntimeError("Name should not be provided.")
		kwargs["name"] = self.value
		return UserRoleDef.role_str(kwargs)