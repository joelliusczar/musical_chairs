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

class UserRoleDomain(Enum):
	Site = "site"
	Station = "station"
	Path = "path"
	Playlist = "playlist"
	Album = "album"
	Artist = "artist"

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)


class UserRoleDef(Enum):
	ADMIN = "admin"
	SITE_USER_ASSIGN = f"{UserRoleDomain.Site.value}:userassign"
	SITE_USER_LIST = f"{UserRoleDomain.Site.value}:userlist"
	SITE_PLACEHOLDER = f"{UserRoleDomain.Site.value}:placeholder"
	USER_EDIT = f"{UserRoleDomain.Site.value}:useredit"
	SONG_EDIT = "song:edit"
	SONG_DOWNLOAD = "song:download"
	SONG_TREE_LIST = "songtree:list"
	ALBUM_EDIT = f"{UserRoleDomain.Album.value}:edit"
	ALBUM_VIEW = f"{UserRoleDomain.Album.value}:view"
	ALBUM_VIEW_ALL = f"{UserRoleDomain.Album.value}:view_all"
	ARTIST_EDIT = f"{UserRoleDomain.Artist.value}:edit"
	ARTIST_VIEW = f"{UserRoleDomain.Artist.value}:view"
	ARTIST_VIEW_ALL = f"{UserRoleDomain.Artist.value}:view_all"
	STATION_VIEW = f"{UserRoleDomain.Station.value}:view"
	STATION_CREATE = f"{UserRoleDomain.Station.value}:create"
	STATION_COPY = f"{UserRoleDomain.Station.value}:copy"
	STATION_EDIT = f"{UserRoleDomain.Station.value}:edit"
	STATION_DELETE = f"{UserRoleDomain.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleDomain.Station.value}:request"
	STATION_FLIP = f"{UserRoleDomain.Station.value}:flip"
	STATION_SKIP = f"{UserRoleDomain.Station.value}:skip"
	STATION_ASSIGN = f"{UserRoleDomain.Station.value}:assign"
	STATION_USER_ASSIGN = f"{UserRoleDomain.Station.value}:userassign"
	STATION_USER_LIST = f"{UserRoleDomain.Station.value}:userlist"
	USER_LIST = "user:list"
	USER_IMPERSONATE = "user:impersonate"
	PATH_LIST = f"{UserRoleDomain.Path.value}:list"
	PATH_EDIT = f"{UserRoleDomain.Path.value}:edit"
	PATH_DELETE = f"{UserRoleDomain.Path.value}:delete"
	PATH_VIEW = f"{UserRoleDomain.Path.value}:view"
	PATH_USER_ASSIGN = f"{UserRoleDomain.Path.value}:userassign"
	PATH_USER_LIST = f"{UserRoleDomain.Path.value}:userlist"
	PATH_DOWNLOAD = f"{UserRoleDomain.Path.value}:download"
	PATH_UPLOAD = f"{UserRoleDomain.Path.value}:upload"
	PATH_MOVE = f"{UserRoleDomain.Path.value}:move"
	PLAYLIST_VIEW = f"{UserRoleDomain.Playlist.value}:view"
	PLAYLIST_CREATE = f"{UserRoleDomain.Playlist.value}:create"
	PLAYLIST_EDIT = f"{UserRoleDomain.Playlist.value}:edit"
	PLAYLIST_DELETE = f"{UserRoleDomain.Playlist.value}:delete"
	PLAYLIST_ASSIGN = f"{UserRoleDomain.Playlist.value}:assign"
	PLAYLIST_USER_ASSIGN = f"{UserRoleDomain.Playlist.value}:userassign"
	PLAYLIST_USER_LIST = f"{UserRoleDomain.Playlist.value}:userlist"

	def __call__(self, **kwargs: Union[str, int]) -> str:
		return self.modded_value(**kwargs)

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)

	@property
	def nameValue(self):
		return self.value

	@staticmethod
	def as_set(domain: Optional[str]=None) -> Set[str]:
		return {r.value for r in UserRoleDef \
			if not domain or r.value.startswith(domain)}

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