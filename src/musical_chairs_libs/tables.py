from typing import cast, Optional
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
	Column("creationTimestamp", Float[float], nullable=False),
	Column("viewSecurityLevel", Integer, nullable=True),
)

u = users.c #pyright: ignore [reportUnknownMemberType]
u_pk = cast(Column[Integer],u.pk) #pyright: ignore [reportUnknownMemberType]
u_username = cast(Column[String],u.username) #pyright: ignore [reportUnknownMemberType]
u_displayName = cast(Column[Optional[String]],u.displayName) #pyright: ignore [reportUnknownMemberType]
u_hashedPW = cast(Column[LargeBinary],u.hashedPW) #pyright: ignore [reportUnknownMemberType]
u_email = cast(Column[Optional[String]],u.email) #pyright: ignore [reportUnknownMemberType]
u_dirRoot = cast(Column[Optional[String]],u.dirRoot) #pyright: ignore [reportUnknownMemberType]
u_disabled = cast(Column[Optional[Integer]],u.isDisabled) #pyright: ignore [reportUnknownMemberType]
u_creationTimestamp = cast(Column[Float[float]],u.creationTimestamp) #pyright: ignore [reportUnknownMemberType]

Index("idx_uniqueUsername", u_username, unique=True)
Index("idx_uniqueEmail", u_email, unique=True)
Index("idx_dirRoot", u_dirRoot, unique=True)

artists = Table("Artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"),\
		nullable=False),
	Column("lastModifiedTimestamp", Float[float], nullable=False),
	Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False),
)

ar = artists.c #pyright: ignore [reportUnknownMemberType]
ar_pk = cast(Column[Integer],ar.pk) #pyright: ignore [reportUnknownMemberType]
ar_name = cast(Column[String],ar.name) #pyright: ignore [reportUnknownMemberType]
ar_ownerFk = cast(Column[Integer],ar.ownerFk) #pyright: ignore [reportUnknownMemberType]

Index("idx_uniqueArtistsName", ar_name, ar_ownerFk, unique=True)


albums = Table("Albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("albumArtistFk", Integer, ForeignKey("Artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=False),
	Column("lastModifiedTimestamp", Float[float], nullable=False),
	Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False)
)

ab = albums.c #pyright: ignore [reportUnknownMemberType]
ab_pk = cast(Column[Integer],ab.pk) #pyright: ignore [reportUnknownMemberType]
ab_name = cast(Column[Optional[String]],ab.name) #pyright: ignore [reportUnknownMemberType]
ab_year = cast(Column[Optional[Integer]], ab.year) #pyright: ignore [reportUnknownMemberType]
ab_albumArtistFk = cast(Column[Optional[Integer]], ab.albumArtistFk) #pyright: ignore [reportUnknownMemberType]
ab_ownerFk = cast(Column[Integer], ab.ownerFk) #pyright: ignore [reportUnknownMemberType]

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
	Column("bitrate", Float[float], nullable=True),
	Column("comment", String, nullable=True),
	Column("lyrics", String, nullable=True),
	Column("duration", Float[float], nullable=True),
	Column("sampleRate", Float[float], nullable=True),
	Column("isDirectoryPlaceholder", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float[float], nullable=True)
)

sg = songs.c #pyright: ignore [reportUnknownMemberType]
sg_pk = cast(Column[Integer],sg.pk) #pyright: ignore [reportUnknownMemberType]
sg_name = cast(Column[Optional[String]],sg.name) #pyright: ignore [reportUnknownMemberType]
sg_path = cast(Column[String],sg.path) #pyright: ignore [reportUnknownMemberType]
sg_albumFk = cast(Column[Optional[Integer]], sg.albumFk) #pyright: ignore [reportUnknownMemberType]
sg_track = cast(Column[Optional[Integer]], sg.track) #pyright: ignore [reportUnknownMemberType]
sg_disc = cast(Column[Optional[Integer]], sg.disc) #pyright: ignore [reportUnknownMemberType]
sg_genre = cast(Column[Optional[String]], sg.genre) #pyright: ignore [reportUnknownMemberType]
sg_explicit = cast(Column[Optional[Integer]], sg.explicit) #pyright: ignore [reportUnknownMemberType]
sg_bitrate = cast(Column[Optional[Float[float]]], sg.bitrate) #pyright: ignore [reportUnknownMemberType]
sg_comment = cast(Column[Optional[String]], sg.comment) #pyright: ignore [reportUnknownMemberType]
sg_lyrics = cast(Column[Optional[String]], sg.lyrics) #pyright: ignore [reportUnknownMemberType]
sg_duration = cast(Column[Optional[Float[float]]], sg.duration) #pyright: ignore [reportUnknownMemberType]
sg_sampleRate = cast(Column[Optional[Float[float]]], sg.sampleRate) #pyright: ignore [reportUnknownMemberType]

Index("idx_uniqueSongPath", sg_path, unique=True)


song_artist = Table("SongsArtists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("artistFk", Integer, ForeignKey("Artists.pk"), nullable=False),
	Column("isPrimaryArtist", Integer, nullable=True),
	Column("comment", String, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float[float], nullable=True)
)


sgar = song_artist.c #pyright: ignore [reportUnknownMemberType]
sgar_pk = cast(Column[Integer] ,sgar.pk) #pyright: ignore [reportUnknownMemberType]
sgar_songFk = cast(Column[Integer] ,sgar.songFk) #pyright: ignore [reportUnknownMemberType]
sgar_artistFk = cast(Column[Integer] ,sgar.artistFk) #pyright: ignore [reportUnknownMemberType]
sgar_isPrimaryArtist = cast(Column[Optional[Integer]],sgar.isPrimaryArtist) #pyright: ignore [reportUnknownMemberType]

Index("idx_songsArtists", sgar_songFk, sgar_artistFk, unique=True)

song_covers = Table("SongCovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("coverSongFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float[float], nullable=True)
)
_sc_songFk = cast(Column[Integer],song_covers.c.songFk) #pyright: ignore [reportUnknownMemberType]
_sc_coverSongFk = cast(Column[Integer],song_covers.c.coverSongFk) #pyright: ignore [reportUnknownMemberType]
Index("idx_songCovers", _sc_songFk, _sc_coverSongFk, unique=True)

stations = Table("Stations", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("displayName", String, nullable=True),
	Column("procId", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float[float], nullable=True),
  Column("ownerFk", Integer, ForeignKey("Users.pk"), nullable=False),
  Column("requestSecurityLevel", Integer, nullable=True),
  Column("viewSecurityLevel", Integer, nullable=True),
)

st = stations.c #pyright: ignore [reportUnknownMemberType]
st_pk = cast(Column[Integer],st.pk) #pyright: ignore [reportUnknownMemberType]
st_name = cast(Column[String],st.name) #pyright: ignore [reportUnknownMemberType]
st_displayName = cast(Column[String],st.displayName) #pyright: ignore [reportUnknownMemberType]
st_procId = cast(Column[Integer],st.procId) #pyright: ignore [reportUnknownMemberType]
st_ownerFk = cast(Column[Integer],st.ownerFk) #pyright: ignore [reportUnknownMemberType]
st_requestSecurityLevel = cast(Column[Integer],st.requestSecurityLevel) #pyright: ignore [reportUnknownMemberType]
st_viewSecurityLevel = cast(Column[Integer],st.viewSecurityLevel) #pyright: ignore [reportUnknownMemberType]
Index("idx_uniqueStationName", st_name, st_ownerFk, unique=True)

stations_songs = Table("StationsSongs", metadata,
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float[float], nullable=True)
)
stsg = stations_songs.c #pyright: ignore [reportUnknownMemberType]


stsg_songFk = cast(Column[Integer], stations_songs.c.songFk) #pyright: ignore [reportUnknownMemberType]
stsg_stationFk= cast(Column[Integer], stations_songs.c.stationFk) #pyright: ignore [reportUnknownMemberType]
Index("idx_stationsSongs", stsg_songFk, stsg_stationFk, unique=True)

userRoles = Table("UserRoles", metadata,
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float[float], nullable=False)
)
ur_userFk = cast(Column[Integer], userRoles.c.userFk) #pyright: ignore [reportUnknownMemberType]
ur_role = cast(Column[String], userRoles.c.role) #pyright: ignore [reportUnknownMemberType]
ur_span = cast(Column[Float[float]], userRoles.c.span) #pyright: ignore [reportUnknownMemberType]
ur_count = cast(Column[Float[float]], userRoles.c.count) #pyright: ignore [reportUnknownMemberType]
ur_priority = cast(Column[Integer], userRoles.c.priority) #pyright: ignore [reportUnknownMemberType]
Index("idx_userRoles", ur_userFk, ur_role, unique=True)

user_action_history = Table("UserActionHistory", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=True),
	Column("action", String, nullable=False),
	Column("timestamp", Float[float], nullable=True),
	Column("queuedTimestamp", Float[float], nullable=False),
	Column("requestedTimestamp", Float[float], nullable=True)
)

uah = user_action_history.c
uah_pk = cast(Column[Integer], uah.pk)
uah_userFk = cast(Column[Optional[Integer]],uah.userFk)
uah_action = cast(Column[String], uah.action)
uah_timestamp = cast(Column[Optional[Float[float]]],uah.timestamp)
uah_queuedTimestamp = cast(Column[Float[float]], uah.queuedTimestamp)
uah_requestedTimestamp = cast(Column[Float[float]], uah.requestedTimestamp)

station_queue = Table("StationQueue", metadata,
  Column("userActionHistoryFk",
		Integer,
		ForeignKey("UserActionHistory.pk"),
		nullable=False
	),
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=True)
)

q = station_queue.c #pyright: ignore [reportUnknownMemberType]
q_userActionHistoryFk = cast(Column[Integer], q.userActionHistoryFk) #pyright: ignore [reportUnknownMemberType]
q_songFk = cast(Column[Integer], q.songFk) #pyright: ignore [reportUnknownMemberType]
q_stationFk = cast(Column[Integer], q.stationFk) #pyright: ignore [reportUnknownMemberType]



station_user_permissions = Table("StationUserPermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float[float], nullable=False)
)

stup = station_user_permissions.c
stup_stationFk = cast(Column[Integer], stup.stationFk)
stup_pk = cast(Column[Integer], stup.pk)
stup_userFk = cast(Column[Integer], stup.userFk)
stup_role = cast(Column[String], stup.role)
stup_span = cast(Column[Float[float]], stup.span)
stup_count = cast(Column[Float[float]], stup.count)
stup_priority = cast(Column[Integer], stup.priority)


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
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float[float], nullable=False)
)

pup = path_user_permissions.c #pyright: ignore [reportUnknownMemberType]
pup_userFk = cast(Column[Integer], pup.userFk) #pyright: ignore [reportUnknownMemberType]
pup_path = cast(Column[String], pup.path) #pyright: ignore [reportUnknownMemberType]
pup_role = cast(Column[String], pup.role) #pyright: ignore [reportUnknownMemberType]
pup_priority = cast(Column[Integer], pup.priority) #pyright: ignore [reportUnknownMemberType]
pup_span = cast(Column[Float[float]], pup.span) #pyright: ignore [reportUnknownMemberType]
pup_count = cast(Column[Float[float]], pup.count) #pyright: ignore [reportUnknownMemberType]

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
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Float[float], nullable=False)
)
fup = friend_user_permissions.c #pyright: ignore [reportUnknownMemberType]
fup_friendFk = cast(Column[Integer], fup.friendFk) #pyright: ignore [reportUnknownMemberType]
fup_pk = cast(Column[Integer], fup.pk) #pyright: ignore [reportUnknownMemberType]
fup_userFk = cast(Column[Integer], fup.userFk) #pyright: ignore [reportUnknownMemberType]
fup_role = cast(Column[String], fup.role) #pyright: ignore [reportUnknownMemberType]
fup_span = cast(Column[Float[float]], fup.span) #pyright: ignore [reportUnknownMemberType]
fup_count = cast(Column[Float[float]], fup.count) #pyright: ignore [reportUnknownMemberType]
fup_priority = cast(Column[Integer], fup.priority) #pyright: ignore [reportUnknownMemberType]

Index(
	"idx_friendPermissions",
	fup_friendFk,
	fup_userFk,
	fup_role,
	unique=True
)



