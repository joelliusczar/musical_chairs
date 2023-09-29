from uuid import UUID
from typing import cast, Optional
from sqlalchemy import (
	Table,
	MetaData,
	Column,
	Float,
	Double,
	Boolean,
	LargeBinary,
	Integer,
	String,
	ForeignKey,
	Index,
	Uuid,
	Text
)
from sqlalchemy.sql.schema import Column



metadata = MetaData()


users = Table("Users", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("username", String(50), nullable=False),
	Column("displayName", String(50), nullable=True),
	Column("hashedPW", LargeBinary, nullable=True),
	Column("email", String(254), nullable=True),
	Column("dirRoot", String(200), nullable=True),
	Column("isDisabled", Boolean, nullable=True),
	Column("creationTimestamp", Double[float](), nullable=False),
	Column("viewSecurityLevel", Integer, nullable=True),
)

u = users.c
u_pk = cast(Column[Uuid[UUID]],u.pk)
u_username = cast(Column[String],u.username)
u_displayName = cast(Column[Optional[String]],u.displayName)
u_hashedPW = cast(Column[LargeBinary],u.hashedPW)
u_email = cast(Column[Optional[String]],u.email)
u_dirRoot = cast(Column[Optional[String]],u.dirRoot)
u_disabled = cast(Column[Optional[Integer]],u.isDisabled)
u_creationTimestamp = cast(Column[Double[float]],u.creationTimestamp)

Index("idx_uniqueUsername", u_username, unique=True)
Index("idx_uniqueEmail", u_email, unique=True)
Index("idx_dirRoot", u_dirRoot, unique=True)

artists = Table("Artists", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("name", String(200), nullable=False),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"),\
		nullable=False),
	Column("lastModifiedTimestamp", Double[float], nullable=False),
	Column("ownerFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
)

ar = artists.c
ar_pk = cast(Column[Uuid[UUID]],ar.pk)
ar_name = cast(Column[String],ar.name)
ar_ownerFk = cast(Column[Uuid[UUID]],ar.ownerFk)

Index("idx_uniqueArtistsName", ar_name, ar_ownerFk, unique=True)


albums = Table("Albums", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("name", String(200), nullable=False),
	Column("albumArtistFk", Uuid[UUID], ForeignKey("Artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=False),
	Column("lastModifiedTimestamp", Double[float], nullable=False),
	Column("ownerFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False)
)

ab = albums.c
ab_pk = cast(Column[Uuid[UUID]],ab.pk)
ab_name = cast(Column[Optional[String]],ab.name)
ab_year = cast(Column[Optional[Integer]], ab.year)
ab_albumArtistFk = cast(Column[Optional[Uuid[UUID]]], ab.albumArtistFk)
ab_ownerFk = cast(Column[Uuid[UUID]], ab.ownerFk)

Index(
	"idx_uniqueAlbumNameForArtist",
	ab_name,
	ab_albumArtistFk,
	ab_ownerFk,
	unique=True
)

songs = Table("Songs", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("path", String(2000), nullable=False),
	Column("name", String(200), nullable=True),
	Column("albumFk", Uuid[UUID], ForeignKey("Albums.pk"), nullable=True),
	Column("track", Integer, nullable=True),
	Column("disc", Integer, nullable=True),
	Column("genre", String(50), nullable=True),
	Column("explicit", Boolean, nullable=True),
	Column("bitrate", Double[float], nullable=True),
	Column("comment", String(2000), nullable=True),
	Column("lyrics", Text, nullable=True),
	Column("duration", Float[float], nullable=True),
	Column("sampleRate", Float[float], nullable=True),
	Column("isDirectoryPlaceholder", Boolean, nullable=True),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Double[float], nullable=True)
)

sg = songs.c
sg_pk = cast(Column[Uuid[UUID]],sg.pk)
sg_name = cast(Column[Optional[String]],sg.name)
sg_path = cast(Column[String],sg.path)
sg_albumFk = cast(Column[Optional[Uuid[UUID]]], sg.albumFk)
sg_track = cast(Column[Optional[Integer]], sg.track)
sg_disc = cast(Column[Optional[Integer]], sg.disc)
sg_genre = cast(Column[Optional[String]], sg.genre)
sg_explicit = cast(Column[Optional[Integer]], sg.explicit)
sg_bitrate = cast(Column[Optional[Float[float]]], sg.bitrate)
sg_comment = cast(Column[Optional[String]], sg.comment)
sg_lyrics = cast(Column[Optional[String]], sg.lyrics)
sg_duration = cast(Column[Optional[Float[float]]], sg.duration)
sg_sampleRate = cast(Column[Optional[Float[float]]], sg.sampleRate)

Index("idx_uniqueSongPath", sg_path, unique=True)


song_artist = Table("SongsArtists", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("songFk", Uuid[UUID], ForeignKey("Songs.pk"), nullable=False),
	Column("artistFk", Uuid[UUID], ForeignKey("Artists.pk"), nullable=False),
	Column("isPrimaryArtist", Boolean, nullable=True),
	Column("comment", String(2000), nullable=True),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Double[float], nullable=True)
)


sgar = song_artist.c
sgar_pk = cast(Column[Uuid[UUID]] ,sgar.pk)
sgar_songFk = cast(Column[Uuid[UUID]] ,sgar.songFk)
sgar_artistFk = cast(Column[Uuid[UUID]] ,sgar.artistFk)
sgar_isPrimaryArtist = cast(Column[Optional[Boolean]],sgar.isPrimaryArtist)

Index("idx_songsArtists", sgar_songFk, sgar_artistFk, unique=True)

song_covers = Table("SongCovers", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("songFk", Uuid[UUID], ForeignKey("Songs.pk"), nullable=False),
	Column("coverSongFk", Uuid[UUID], ForeignKey("Songs.pk"), nullable=False),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Double[float], nullable=True)
)
_sc_songFk = cast(Column[Uuid[UUID]],song_covers.c.songFk)
_sc_coverSongFk = cast(Column[Uuid[UUID]],song_covers.c.coverSongFk)
Index("idx_songCovers", _sc_songFk, _sc_coverSongFk, unique=True)

stations = Table("Stations", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("name", String(100), nullable=False),
	Column("displayName", String(500), nullable=True),
	Column("procId", Integer, nullable=True),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Double[float], nullable=True),
  Column("ownerFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
  Column("requestSecurityLevel", Integer, nullable=True),
  Column("viewSecurityLevel", Integer, nullable=True),
)

st = stations.c
st_pk = cast(Column[Uuid[UUID]],st.pk)
st_name = cast(Column[String],st.name)
st_displayName = cast(Column[String],st.displayName)
st_procId = cast(Column[Integer],st.procId)
st_ownerFk = cast(Column[Uuid[UUID]],st.ownerFk)
st_requestSecurityLevel = cast(Column[Integer],st.requestSecurityLevel)
st_viewSecurityLevel = cast(Column[Integer],st.viewSecurityLevel)
Index("idx_uniqueStationName", st_name, st_ownerFk, unique=True)

stations_songs = Table("StationsSongs", metadata,
	Column("songFk", Uuid[UUID], ForeignKey("Songs.pk"), nullable=False),
	Column("stationFk", Uuid[UUID], ForeignKey("Stations.pk"), nullable=False),
	Column("lastModifiedByUserFk", Uuid[UUID], ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Double[float], nullable=True)
)
stsg = stations_songs.c


stsg_songFk = cast(Column[Uuid[UUID]], stations_songs.c.songFk)
stsg_stationFk= cast(Column[Uuid[UUID]], stations_songs.c.stationFk)
Index("idx_stationsSongs", stsg_songFk, stsg_stationFk, unique=True)

userRoles = Table("UserRoles", metadata,
	Column("userFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Double[float], nullable=False)
)
ur_userFk = cast(Column[Uuid[UUID]], userRoles.c.userFk)
ur_role = cast(Column[String], userRoles.c.role)
ur_span = cast(Column[Float[float]], userRoles.c.span)
ur_count = cast(Column[Float[float]], userRoles.c.count)
ur_priority = cast(Column[Integer], userRoles.c.priority)
Index("idx_userRoles", ur_userFk, ur_role, unique=True)

user_action_history = Table("UserActionHistory", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("userFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=True),
	Column("action", String(50), nullable=False),
	Column("timestamp", Double[float], nullable=True),
	Column("queuedTimestamp", Double[float], nullable=False),
	Column("requestedTimestamp", Double[float], nullable=True)
)

uah = user_action_history.c
uah_pk = cast(Column[Uuid[UUID]], uah.pk)
uah_userFk = cast(Column[Optional[Uuid[UUID]]],uah.userFk)
uah_action = cast(Column[String], uah.action)
uah_timestamp = cast(Column[Optional[Double[float]]],uah.timestamp)
uah_queuedTimestamp = cast(Column[Double[float]], uah.queuedTimestamp)
uah_requestedTimestamp = cast(Column[Double[float]], uah.requestedTimestamp)

station_queue = Table("StationQueue", metadata,
  Column("userActionHistoryFk",
		Uuid[UUID],
		ForeignKey("UserActionHistory.pk"),
		nullable=False
	),
	Column("stationFk", Uuid[UUID], ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Uuid[UUID], ForeignKey("Songs.pk"), nullable=True)
)

q = station_queue.c
q_userActionHistoryFk = cast(Column[Uuid[UUID]], q.userActionHistoryFk)
q_songFk = cast(Column[Uuid[UUID]], q.songFk)
q_stationFk = cast(Column[Uuid[UUID]], q.stationFk)

Index("idx_stationQueueStations", q_stationFk)


station_user_permissions = Table("StationUserPermissions", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("stationFk", Uuid[UUID], ForeignKey("Stations.pk"), nullable=False),
	Column("userFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Double[float], nullable=False)
)

stup = station_user_permissions.c
stup_stationFk = cast(Column[Uuid[UUID]], stup.stationFk)
stup_pk = cast(Column[Uuid[UUID]], stup.pk)
stup_userFk = cast(Column[Uuid[UUID]], stup.userFk)
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
	Column("pk", Uuid[UUID], primary_key=True),
	Column("userFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
	Column("path", String(2000), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Double[float], nullable=False)
)

pup = path_user_permissions.c
pup_userFk = cast(Column[Uuid[UUID]], pup.userFk)
pup_path = cast(Column[String], pup.path)
pup_role = cast(Column[String], pup.role)
pup_priority = cast(Column[Integer], pup.priority)
pup_span = cast(Column[Float[float]], pup.span)
pup_count = cast(Column[Float[float]], pup.count)

Index(
	"idx_pathPermissions",
	pup_userFk,
	pup_path,
	pup_role,
	unique=True
)

friend_user_permissions = Table("FriendUserPermissions", metadata,
	Column("pk", Uuid[UUID], primary_key=True),
	Column("friendFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
	Column("userFk", Uuid[UUID], ForeignKey("Users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationTimestamp", Double[float], nullable=False)
)
fup = friend_user_permissions.c
fup_friendFk = cast(Column[Uuid[UUID]], fup.friendFk)
fup_pk = cast(Column[Uuid[UUID]], fup.pk)
fup_userFk = cast(Column[Uuid[UUID]], fup.userFk)
fup_role = cast(Column[String], fup.role)
fup_span = cast(Column[Float[float]], fup.span)
fup_count = cast(Column[Float[float]], fup.count)
fup_priority = cast(Column[Integer], fup.priority)

Index(
	"idx_friendPermissions",
	fup_friendFk,
	fup_userFk,
	fup_role,
	unique=True
)



