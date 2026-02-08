from enum import Enum
from typing import Optional

hidden_token_alphabet = \
	"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz-.~"
public_token_alphabet = "0123456789_abcdefghijklmnopqrstuvwxyz"

public_token_prefix = "u-"

class UserRoleSphere(Enum):
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
	ALBUM_CREATE = f"{UserRoleSphere.Album.value}:create"
	ALBUM_EDIT = f"{UserRoleSphere.Album.value}:edit"
	
class ArtistActions(Enum):
	ARTIST_CREATE = f"{UserRoleSphere.Artist.value}:create"
	ARTIST_EDIT = f"{UserRoleSphere.Artist.value}:edit"

class StationActions(Enum):
	STATION_CREATE = f"{UserRoleSphere.Station.value}:create"
	STATION_COPY = f"{UserRoleSphere.Station.value}:copy"
	STATION_EDIT = f"{UserRoleSphere.Station.value}:edit"
	STATION_DELETE = f"{UserRoleSphere.Station.value}:delete"
	STATION_REQUEST = f"{UserRoleSphere.Station.value}:request"
	STATION_ENABLE = f"{UserRoleSphere.Station.value}:enable"
	STATION_DISABLE = f"{UserRoleSphere.Station.value}:disable"
	STATION_SKIP = f"{UserRoleSphere.Station.value}:skip"
	STATION_PLAYNEXT = f"{UserRoleSphere.Station.value}:playnext"
	STATION_ASSIGN = f"{UserRoleSphere.Station.value}:assign"
	STATION_USER_ASSIGN = f"{UserRoleSphere.Station.value}:userassign"
	STATION_USER_REMOVE = f"{UserRoleSphere.Station.value}:userremove"

class StationsSongsActions(Enum):
	SKIP = "Skipped"
	PLAYED = "Played"
	
class PathActions(Enum):
	PATH_EDIT = f"{UserRoleSphere.Path.value}:edit"
	PATH_DELETE = f"{UserRoleSphere.Path.value}:delete"
	PATH_USER_ASSIGN = f"{UserRoleSphere.Path.value}:userassign"
	PATH_DOWNLOAD = f"{UserRoleSphere.Path.value}:download"
	PATH_UPLOAD = f"{UserRoleSphere.Path.value}:upload"
	PATH_MOVE = f"{UserRoleSphere.Path.value}:move"

class PlaylistActions(Enum):
	PLAYLIST_CREATE = f"{UserRoleSphere.Playlist.value}:create"
	PLAYLIST_EDIT = f"{UserRoleSphere.Playlist.value}:edit"
	PLAYLIST_DELETE = f"{UserRoleSphere.Playlist.value}:delete"
	PLAYLIST_ASSIGN = f"{UserRoleSphere.Playlist.value}:assign"
	PLAYLIST_USER_ASSIGN = f"{UserRoleSphere.Playlist.value}:userassign"
	PLAYLIST_USER_LIST = f"{UserRoleSphere.Playlist.value}:userlist"

class UserActions(Enum):
	CHANGE_PASS = f"{UserRoleSphere.User.value}:change-password"
	LOGIN = f"{UserRoleSphere.User.value}:login"
	ACCOUNT_CREATE = f"{UserRoleSphere.User.value}:account-create"
	ACCOUNT_UPDATE = f"{UserRoleSphere.User.value}:account-update"
	ADD_SITE_RULE = f"{UserRoleSphere.User.value}:add-site-rule"
	REMOVE_SITE_RULE = f"{UserRoleSphere.User.value}:remove-site-rule"

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