from enum import Enum
from typing import Optional


class UserRoleDomain(Enum):
	Site = "site"
	User = "user"
	Station = "station"
	Path = "path"
	Playlist = "playlist"
	Album = "album"
	Artist = "artist"

	def conforms(self, candidate: str) -> bool:
		return candidate.startswith(self.value)
	
class AlbumActions(Enum):
	ALBUM_CREATE = f"{UserRoleDomain.Album.value}:create"
	ALBUM_EDIT = f"{UserRoleDomain.Album.value}:edit"
	
class ArtistActions(Enum):
	ARTIST_CREATE = f"{UserRoleDomain.Artist.value}:create"
	ARTIST_EDIT = f"{UserRoleDomain.Artist.value}:edit"

class StationActions(Enum):
	STATION_CREATE = f"{UserRoleDomain.Station.value}:create"
	STATION_COPY = f"{UserRoleDomain.Station.value}:copy"
	STATION_EDIT = f"{UserRoleDomain.Station.value}:edit"
	STATION_DELETE = f"{UserRoleDomain.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleDomain.Station.value}:request"
	STATION_ENABLE = f"{UserRoleDomain.Station.value}:enable"
	STATION_DISABLE = f"{UserRoleDomain.Station.value}:disable"
	STATION_SKIP = f"{UserRoleDomain.Station.value}:skip"
	STATION_PLAYNEXT = f"{UserRoleDomain.Station.value}:playnext"
	STATION_ASSIGN = f"{UserRoleDomain.Station.value}:assign"
	STATION_USER_ASSIGN = f"{UserRoleDomain.Station.value}:userassign"
	STATION_USER_REMOVE = f"{UserRoleDomain.Station.value}:userremove"
	
class PathActions(Enum):
	PATH_EDIT = f"{UserRoleDomain.Path.value}:edit"
	PATH_DELETE = f"{UserRoleDomain.Path.value}:delete"
	PATH_USER_ASSIGN = f"{UserRoleDomain.Path.value}:userassign"
	PATH_DOWNLOAD = f"{UserRoleDomain.Path.value}:download"
	PATH_UPLOAD = f"{UserRoleDomain.Path.value}:upload"
	PATH_MOVE = f"{UserRoleDomain.Path.value}:move"

class PlaylistActions(Enum):
	PLAYLIST_CREATE = f"{UserRoleDomain.Playlist.value}:create"
	PLAYLIST_EDIT = f"{UserRoleDomain.Playlist.value}:edit"
	PLAYLIST_DELETE = f"{UserRoleDomain.Playlist.value}:delete"
	PLAYLIST_ASSIGN = f"{UserRoleDomain.Playlist.value}:assign"
	PLAYLIST_USER_ASSIGN = f"{UserRoleDomain.Playlist.value}:userassign"
	PLAYLIST_USER_LIST = f"{UserRoleDomain.Playlist.value}:userlist"

class UserActions(Enum):
	CHANGE_PASS = f"{UserRoleDomain.User.value}:change-password"
	LOGIN = f"{UserRoleDomain.User.value}:login"
	ACCOUNT_CREATE = f"{UserRoleDomain.User.value}:account-create"
	ACCOUNT_UPDATE = f"{UserRoleDomain.User.value}:account-update"
	ADD_SITE_RULE = f"{UserRoleDomain.User.value}:add-site-rule"
	REMOVE_SITE_RULE = f"{UserRoleDomain.User.value}:remove-site-rule"

class DbUsers(Enum):
	OWNER_USER = "mc_owner"
	API_USER = "api_user"
	RADIO_USER = "radio_user"
	JANITOR_USER = "janitor_user"

	def format_user(self, host:str="localhost") -> str:
		return f"'{self.value}'@'{host}'"

	def __call__(self, host:Optional[str]=None) -> str:
		if host:
			return self.format_user(host)
		return self.value
	
class JobTypes(Enum):
	SONG_DELETE = "song-delete"

class JobStatusTypes(Enum):
	STARTED = "started"
	COMPLETED = "completed"
	FAILED = "failed"

#these types are for the station itself
class StationTypes(Enum):
	SONGS_ONLY = 0
	ALBUMS_ONLY = 1 #deprecated
	PLAYLISTS_ONLY = 2 #deprecated
	ALBUMS_AND_PLAYLISTS = 3

#these types are for the songs and help differentiate between an album id
#and a playlist id
class StationRequestTypes(Enum):
	SONG = 0
	ALBUM = 1
	PLAYLIST =2 

	def title(self):
		return self.name.title()

	def lower(self):
		return self.name.lower()