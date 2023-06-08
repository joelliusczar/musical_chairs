from typing import Any, cast
from sqlalchemy import (
	Table,
	MetaData,
	Column,
	Float,
	LargeBinary,
	Integer,
	String,
	ForeignKey,
	Index
)
from sqlalchemy.sql import ColumnCollection as TblCols
from sqlalchemy.sql.schema import Column



metadata = MetaData()

users = Table("Users", metadata,
	Column("pk", Integer, primary_key=True),
	Column("username", String, nullable=False),
	Column("displayName", String, nullable=True),
	Column("hashedPW", LargeBinary, nullable=True),
	Column("email", String, nullable=True),
	Column("dirRoot", String, nullable=True),
	Column("isDisabled", Integer, nullable=True),
	Column("creationTimestamp", Float, nullable=False)
)

u = cast(TblCols,users.c) #pyright: ignore [reportUnknownMemberType]
u_pk = cast(Column,u.pk) #pyright: ignore [reportUnknownMemberType]
u_username = cast(Column,u.username) #pyright: ignore [reportUnknownMemberType]
u_displayName = cast(Column,u.displayName) #pyright: ignore [reportUnknownMemberType]
u_hashedPW = cast(Column,u.hashedPW) #pyright: ignore [reportUnknownMemberType]
u_email = cast(Column,u.email) #pyright: ignore [reportUnknownMemberType]
u_dirRoot = cast(Column,u.dirRoot) #pyright: ignore [reportUnknownMemberType]
u_disabled = cast(Column,u.isDisabled) #pyright: ignore [reportUnknownMemberType]
u_creationTimestamp = cast(Column,u.creationTimestamp) #pyright: ignore [reportUnknownMemberType]

Index("idx_uniqueUsername", u_username, unique=True)
Index("idx_uniqueEmail", u_email, unique=True)
Index("idx_dirRoot", u_dirRoot, unique=True)

artists = Table("Artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"),\
		nullable=False),
	Column("lastModifiedTimestamp", Float, nullable=False),
	Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False),
)

ar = cast(TblCols, artists.c) #pyright: ignore [reportUnknownMemberType]
ar_pk = cast(Column,ar.pk) #pyright: ignore [reportUnknownMemberType]
ar_name = cast(Column,ar.name) #pyright: ignore [reportUnknownMemberType]
ar_ownerFk = cast(Column,ar.ownerFk) #pyright: ignore [reportUnknownMemberType]

Index("idx_uniqueArtistsName", ar_name, ar_ownerFk, unique=True)


albums = Table("Albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("albumArtistFk", Integer, ForeignKey("Artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=False),
	Column("lastModifiedTimestamp", Float, nullable=False),
	Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False)
)

ab = cast(TblCols, albums.c) #pyright: ignore [reportUnknownMemberType]
ab_pk = cast(Column,ab.pk) #pyright: ignore [reportUnknownMemberType]
ab_name = cast(Column,ab.name) #pyright: ignore [reportUnknownMemberType]
ab_year = cast(Column,ab.year) #pyright: ignore [reportUnknownMemberType]
ab_albumArtistFk = cast(Column,ab.albumArtistFk) #pyright: ignore [reportUnknownMemberType]
ab_ownerFk = cast(Column,ab.ownerFk) #pyright: ignore [reportUnknownMemberType]

Index(
	"idx_uniqueAlbumNameForArtist",
	ab_name,
	ab_albumArtistFk,
	ab_ownerFk,
	unique=True
)

songs = Table("Songs", metadata,
	Column("pk", Integer, primary_key=True),
	Column("path", String, nullable=False),
	Column("name", String, nullable=True),
	Column("albumFk", Integer, ForeignKey("Albums.pk"), nullable=True),
	Column("track", Integer, nullable=True),
	Column("disc", Integer, nullable=True),
	Column("genre", String, nullable=True),
	Column("explicit", Integer, nullable=True),
	Column("bitrate", Float, nullable=True),
	Column("comment", String, nullable=True),
	Column("lyrics", String, nullable=True),
	Column("duration", Float, nullable=True),
	Column("sampleRate", Float, nullable=True),
	Column("isDirectoryPlaceholder", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_sg_path: Any = songs.c.path #pyright: ignore [reportUnknownMemberType]
Index("idx_uniqueSongPath", _sg_path, unique=True)

song_artist = Table("SongsArtists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", ForeignKey("Songs.pk"), nullable=False),
	Column("artistFk", ForeignKey("Artists.pk"), nullable=False),
	Column("isPrimaryArtist", Integer, nullable=True),
	Column("comment", String, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_sa_songFk: Any = song_artist.c.songFk #pyright: ignore [reportUnknownMemberType]
_sa_artistFk: Any = song_artist.c.artistFk #pyright: ignore [reportUnknownMemberType]

Index("idx_songsArtists", _sa_songFk, _sa_artistFk, unique=True)

song_covers = Table("SongCovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", ForeignKey("Songs.pk"), nullable=False),
	Column("coverSongFk", ForeignKey("Songs.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_sc_songFk = cast(Column,song_covers.c.songFk) #pyright: ignore [reportUnknownMemberType]
_sc_coverSongFk = cast(Column,song_covers.c.coverSongFk) #pyright: ignore [reportUnknownMemberType]
Index("idx_songCovers", _sc_songFk, _sc_coverSongFk, unique=True)

stations = Table("Stations", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("displayName", String, nullable=True),
	Column("procId", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True),
  Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False),
  Column("requestSecurityLevel", Integer, nullable=True),
  Column("viewSecurityLevel", Integer, nullable=True),
)

st = cast(TblCols, stations.c) #pyright: ignore [reportUnknownMemberType]
st_pk = cast(Column,st.pk) #pyright: ignore [reportUnknownMemberType]
st_name = cast(Column,st.name) #pyright: ignore [reportUnknownMemberType]
st_displayName = cast(Column,st.displayName) #pyright: ignore [reportUnknownMemberType]
st_procId = cast(Column,st.procId) #pyright: ignore [reportUnknownMemberType]
st_ownerFk = cast(Column,st.ownerFk) #pyright: ignore [reportUnknownMemberType]
st_requestSecurityLevel = cast(Column,st.requestSecurityLevel) #pyright: ignore [reportUnknownMemberType]
st_viewSecurityLevel = cast(Column,st.viewSecurityLevel) #pyright: ignore [reportUnknownMemberType]
Index("idx_uniqueStationName", st_name, st_ownerFk, unique=True)

stations_songs = Table("StationsSongs", metadata,
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
stsg_songFk = cast(Column, stations_songs.c.songFk) #pyright: ignore [reportUnknownMemberType]
stsg_stationFk= cast(Column, stations_songs.c.stationFk) #pyright: ignore [reportUnknownMemberType]
Index("idx_stationsSongs", stsg_songFk, stsg_stationFk, unique=True)

station_queue = Table("StationQueue", metadata,
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("playedTimestamp", Float),
	Column("queuedTimestamp", Float),
	Column("requestedTimestamp", Float),
	Column("requestedByUserFk", Integer, ForeignKey("Users.pk"), nullable=True)
)

q = cast(TblCols, station_queue.c) #pyright: ignore [reportUnknownMemberType]
q_songFk = cast(Column,q.songFk) #pyright: ignore [reportUnknownMemberType]
q_stationFk = cast(Column,q.stationFk) #pyright: ignore [reportUnknownMemberType]
q_queuedTimestamp: Column = q.queuedTimestamp #pyright: ignore [reportUnknownMemberType
q_playedTimestamp: Column = q.playedTimestamp #pyright: ignore [reportUnknownMemberType
q_requestedTimestamp: Column = q.requestedTimestamp #pyright: ignore [reportUnknownMemberType
q_requestedByUserFk: Column = q.requestedByUserFk #pyright: ignore [reportUnknownMemberType

userRoles = Table("UserRoles", metadata,
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("span", Float, nullable=False),
	Column("count", Float, nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float, nullable=False)
)
ur_userFk = cast(Column, userRoles.c.userFk) #pyright: ignore [reportUnknownMemberType]
ur_role = cast(Column, userRoles.c.role) #pyright: ignore [reportUnknownMemberType]
ur_span = cast(Column, userRoles.c.span) #pyright: ignore [reportUnknownMemberType]
ur_count = cast(Column, userRoles.c.count) #pyright: ignore [reportUnknownMemberType]
ur_priority = cast(Column, userRoles.c.priority) #pyright: ignore [reportUnknownMemberType]
Index("idx_userRoles", ur_userFk, ur_role, unique=True)

user_action_history = Table("UserActionHistory", metadata,
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("action", String),
	Column("timestamp", Float, nullable=False)
)

uah = cast(TblCols, user_action_history.c) #pyright: ignore [reportUnknownMemberType]
uah_userFk = cast(Column,uah.userFk) #pyright: ignore [reportUnknownMemberType]
uah_action = cast(Column,uah.action) #pyright: ignore [reportUnknownMemberType]
uah_timestamp = cast(Column,uah.timestamp) #pyright: ignore [reportUnknownMemberType]


station_user_permissions = Table("StationUserPermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=True),
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("span", Float, nullable=False),
	Column("count", Float, nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float, nullable=False)
)
stup = cast(TblCols, station_user_permissions.c) #pyright: ignore [reportUnknownMemberType]
stup_stationFk = cast(Column, stup.stationFk) #pyright: ignore [reportUnknownMemberType]
stup_pk = cast(Column, stup.pk) #pyright: ignore [reportUnknownMemberType]
stup_userFk = cast(Column, stup.userFk) #pyright: ignore [reportUnknownMemberType]
stup_role = cast(Column, stup.role) #pyright: ignore [reportUnknownMemberType]
stup_span = cast(Column, stup.span) #pyright: ignore [reportUnknownMemberType]
stup_count = cast(Column, stup.count) #pyright: ignore [reportUnknownMemberType]
stup_priority = cast(Column, stup.priority) #pyright: ignore [reportUnknownMemberType]


Index(
	"idx_stationPermissions",
	stup_stationFk,
	stup_userFk,
	stup_role,
	unique=True
)

path_user_permissions = Table("PathUserPermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("path", String, nullable=False),
	Column("role", String),
	Column("span", Float, nullable=False),
	Column("count", Float, nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float, nullable=False)
)

pup = cast(TblCols, path_user_permissions.c) #pyright: ignore [reportUnknownMemberType]
pup_userFk: Column = cast(Column,pup.userFk) #pyright: ignore [reportUnknownMemberType]
pup_path: Column = cast(Column,pup.path) #pyright: ignore [reportUnknownMemberType]
pup_role: Column = cast(Column,pup.role) #pyright: ignore [reportUnknownMemberType]
pup_priority: Column = cast(Column,pup.priority) #pyright: ignore [reportUnknownMemberType]
pup_span: Column = cast(Column,pup.span) #pyright: ignore [reportUnknownMemberType]
pup_count: Column = cast(Column,pup.count) #pyright: ignore [reportUnknownMemberType]

Index(
	"idx_pathPermissions",
	pup_userFk,
	pup_path,
	pup_role,
	unique=True
)

friend_user_permissions = Table("FriendUserPermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("friendFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("span", Float, nullable=False),
	Column("count", Float, nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float, nullable=False)
)
fup = cast(TblCols, friend_user_permissions.c) #pyright: ignore [reportUnknownMemberType]
fup_friendFk = cast(Column, fup.friendFk) #pyright: ignore [reportUnknownMemberType]
fup_pk = cast(Column, fup.pk) #pyright: ignore [reportUnknownMemberType]
fup_userFk = cast(Column, fup.userFk) #pyright: ignore [reportUnknownMemberType]
fup_role = cast(Column, fup.role) #pyright: ignore [reportUnknownMemberType]
fup_span = cast(Column, fup.span) #pyright: ignore [reportUnknownMemberType]
fup_count = cast(Column, fup.count) #pyright: ignore [reportUnknownMemberType]
fup_priority = cast(Column, fup.priority) #pyright: ignore [reportUnknownMemberType]

Index(
	"idx_friendPermissions",
	fup_friendFk,
	fup_userFk,
	fup_role,
	unique=True
)

sg = cast(TblCols,songs.c) #pyright: ignore [reportUnknownMemberType]
sg_pk = cast(Column,sg.pk) #pyright: ignore [reportUnknownMemberType]
sg_name = cast(Column,sg.name) #pyright: ignore [reportUnknownMemberType]
sg_path = cast(Column,sg.path) #pyright: ignore [reportUnknownMemberType]
sg_albumFk = cast(Column,sg.albumFk) #pyright: ignore [reportUnknownMemberType]
sg_track = cast(Column,sg.track) #pyright: ignore [reportUnknownMemberType]
sg_disc = cast(Column,sg.disc) #pyright: ignore [reportUnknownMemberType]
sg_genre = cast(Column,sg.genre) #pyright: ignore [reportUnknownMemberType]
sg_explicit = cast(Column,sg.explicit) #pyright: ignore [reportUnknownMemberType]
sg_bitrate = cast(Column,sg.bitrate) #pyright: ignore [reportUnknownMemberType]
sg_comment = cast(Column,sg.comment) #pyright: ignore [reportUnknownMemberType]
sg_lyrics = cast(Column,sg.lyrics) #pyright: ignore [reportUnknownMemberType]
sg_duration = cast(Column,sg.duration) #pyright: ignore [reportUnknownMemberType]
sg_sampleRate = cast(Column,sg.sampleRate) #pyright: ignore [reportUnknownMemberType]

sgar = cast(TblCols, song_artist.c) #pyright: ignore [reportUnknownMemberType]
sgar_pk = cast(Column,sgar.pk) #pyright: ignore [reportUnknownMemberType]
sgar_songFk = cast(Column,sgar.songFk) #pyright: ignore [reportUnknownMemberType]
sgar_artistFk = cast(Column,sgar.artistFk) #pyright: ignore [reportUnknownMemberType]
sgar_isPrimaryArtist = cast(Column,sgar.isPrimaryArtist) #pyright: ignore [reportUnknownMemberType]


stsg = cast(TblCols, stations_songs.c) #pyright: ignore [reportUnknownMemberType]
stsg_songFk = cast(Column,stsg.songFk) #pyright: ignore [reportUnknownMemberType]
stsg_stationFk = cast(Column,stsg.stationFk) #pyright: ignore [reportUnknownMemberType]



