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
	Text,
)
from sqlalchemy.sql.schema import Column



metadata = MetaData()


users = Table("users", metadata,
	Column("pk", Integer, primary_key=True),
	Column("username", String(50), nullable=False),
	Column("displayname", String(50), nullable=True),
	Column("hashedpw", LargeBinary, nullable=True),
	Column("email", String(254), nullable=True),
	Column("dirroot", String(200), nullable=True),
	Column("isdisabled", Boolean, nullable=True),
	Column("creationtimestamp", Double[float](), nullable=False),
	Column("viewsecuritylevel", Integer, nullable=True),
)

u = users.c
u_pk = cast(Column[Integer],u.pk)
u_username = cast(Column[String],u.username)
u_displayName = cast(Column[Optional[String]],u.displayname)
u_hashedPW = cast(Column[LargeBinary],u.hashedpw)
u_email = cast(Column[Optional[String]],u.email)
u_dirRoot = cast(Column[Optional[String]],u.dirroot)
u_disabled = cast(Column[Optional[Integer]],u.isdisabled)
u_creationTimestamp = cast(Column[Double[float]],u.creationtimestamp)

Index("idx_uniqueusername", u_username, unique=True)
Index("idx_uniqueemail", u_email, unique=True)
Index("idx_dirroot", u_dirRoot, unique=True)

artists = Table("artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String(300), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"),\
		nullable=False),
	Column("lastmodifiedtimestamp", Double[float], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
)

ar = artists.c
ar_pk = cast(Column[Integer],ar.pk)
ar_name = cast(Column[String],ar.name)
ar_ownerFk = cast(Column[Integer],ar.ownerfk)

Index("idx_uniqueartistsname", ar_name, ar_ownerFk, unique=True)


albums = Table("albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String(200), nullable=False),
	Column("albumartistfk", Integer, ForeignKey("artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=False),
	Column("lastmodifiedtimestamp", Double[float], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False)
)

ab = albums.c
ab_pk = cast(Column[Integer],ab.pk)
ab_name = cast(Column[Optional[String]],ab.name)
ab_year = cast(Column[Optional[Integer]], ab.year)
ab_albumArtistFk = cast(Column[Optional[Integer]], ab.albumartistfk)
ab_ownerFk = cast(Column[Integer], ab.ownerfk)

Index(
	"idx_uniquealbumnameforartist",
	ab_name,
	ab_albumArtistFk,
	ab_ownerFk,
	unique=True
)

songs = Table("songs", metadata,
	Column("pk", Integer, primary_key=True),
	Column("path", String(2000), nullable=False),
	Column("name", String(200), nullable=True),
	Column("albumfk", Integer, ForeignKey("albums.pk"), nullable=True),
	Column("track", String(20), nullable=True),
	Column("disc", Integer, nullable=True),
	Column("genre", String(50), nullable=True),
	Column("explicit", Boolean, nullable=True),
	Column("bitrate", Double[float], nullable=True),
	Column("comment", String(2000), nullable=True),
	Column("lyrics", Text, nullable=True),
	Column("duration", Float[float], nullable=True),
	Column("samplerate", Float[float], nullable=True),
	Column("isdirectoryplaceholder", Boolean, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True),
	Column("internalpath", String(255), nullable=False),
	Column("hash", LargeBinary, nullable=True),
)

sg = songs.c
sg_pk = cast(Column[Integer],sg.pk)
sg_name = cast(Column[Optional[String]],sg.name)
sg_path = cast(Column[String],sg.path)
sg_internalpath = cast(Column[String],sg.internalpath)
sg_albumFk = cast(Column[Optional[Integer]], sg.albumfk)
sg_track = cast(Column[Optional[Integer]], sg.track)
sg_disc = cast(Column[Optional[Integer]], sg.disc)
sg_genre = cast(Column[Optional[String]], sg.genre)
sg_explicit = cast(Column[Optional[Integer]], sg.explicit)
sg_bitrate = cast(Column[Optional[Float[float]]], sg.bitrate)
sg_comment = cast(Column[Optional[String]], sg.comment)
sg_lyrics = cast(Column[Optional[String]], sg.lyrics)
sg_duration = cast(Column[Optional[Float[float]]], sg.duration)
sg_sampleRate = cast(Column[Optional[Float[float]]], sg.samplerate)
sg_isdirplacholhder = cast(Column[Boolean], sg.isdirectoryplaceholder)

Index("idx_uniquesongpath", sg_path, unique=True)


song_artist = Table("songsartists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("artistfk", Integer, ForeignKey("artists.pk"), nullable=False),
	Column("isprimaryartist", Boolean, nullable=True),
	Column("comment", String(2000), nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True)
)


sgar = song_artist.c
sgar_pk = cast(Column[Integer] ,sgar.pk)
sgar_songFk = cast(Column[Integer] ,sgar.songfk)
sgar_artistFk = cast(Column[Integer] ,sgar.artistfk)
sgar_isPrimaryArtist = cast(Column[Optional[Boolean]],sgar.isprimaryartist)

Index("idx_songsartists", sgar_songFk, sgar_artistFk, unique=True)

song_covers = Table("songcovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("coversongfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True)
)
_sc_songFk = cast(Column[Integer],song_covers.c.songfk)
_sc_coverSongFk = cast(Column[Integer],song_covers.c.coversongfk)
Index("idx_songcovers", _sc_songFk, _sc_coverSongFk, unique=True)

stations = Table("stations", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String(100), nullable=False),
	Column("displayname", String(500), nullable=True),
	Column("procid", Integer, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True),
  Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
  Column("requestsecuritylevel", Integer, nullable=True),
  Column("viewsecuritylevel", Integer, nullable=True),

)

st = stations.c
st_pk = cast(Column[Integer],st.pk)
st_name = cast(Column[String],st.name)
st_displayName = cast(Column[String],st.displayname)
st_procId = cast(Column[Integer],st.procid)
st_ownerFk = cast(Column[Integer],st.ownerfk)
st_requestSecurityLevel = cast(Column[Integer],st.requestsecuritylevel)
st_viewSecurityLevel = cast(Column[Integer],st.viewsecuritylevel)
Index("idx_uniquestationname", st_name, st_ownerFk, unique=True)

stations_songs = Table("stationssongs", metadata,
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True)
)
stsg = stations_songs.c


stsg_songFk = cast(Column[Integer], stations_songs.c.songfk)
stsg_stationFk = cast(Column[Integer], stations_songs.c.stationfk)
stsg_lastmodifiedtimestamp = cast(
	Column[Double[float]], stations_songs.c.lastmodifiedtimestamp
)
Index("idx_stationssongs", stsg_songFk, stsg_stationFk, unique=True)

userRoles = Table("userroles", metadata,
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationtimestamp", Double[float], nullable=False)
)
ur_userFk = cast(Column[Integer], userRoles.c.userfk)
ur_role = cast(Column[String], userRoles.c.role)
ur_span = cast(Column[Float[float]], userRoles.c.span)
ur_count = cast(Column[Float[float]], userRoles.c.count)
ur_priority = cast(Column[Integer], userRoles.c.priority)
Index("idx_userroles", ur_userFk, ur_role, unique=True)

user_action_history = Table("useractionhistory", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=True),
	Column("action", String(50), nullable=False),
	Column("timestamp", Double[float], nullable=True),
	Column("queuedtimestamp", Double[float], nullable=False)
)

uah = user_action_history.c
uah_pk = cast(Column[Integer], uah.pk)
uah_userFk = cast(Column[Optional[Integer]],uah.userfk)
uah_action = cast(Column[String], uah.action)
uah_timestamp = cast(Column[Optional[Double[float]]],uah.timestamp)
uah_queuedTimestamp = cast(Column[Double[float]], uah.queuedtimestamp)

station_queue = Table("stationqueue", metadata,
  Column("useractionhistoryfk",
		Integer,
		ForeignKey("useractionhistory.pk"),
		nullable=False
	),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=True)
)

q = station_queue.c
q_userActionHistoryFk = cast(Column[Integer], q.useractionhistoryfk)
q_songFk = cast(Column[Integer], q.songfk)
q_stationFk = cast(Column[Integer], q.stationfk)

Index("idx_stationqueuestations", q_stationFk)


station_user_permissions = Table("stationuserpermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationtimestamp", Double[float], nullable=False)
)

stup = station_user_permissions.c
stup_stationFk = cast(Column[Integer], stup.stationfk)
stup_pk = cast(Column[Integer], stup.pk)
stup_userFk = cast(Column[Integer], stup.userfk)
stup_role = cast(Column[String], stup.role)
stup_span = cast(Column[Float[float]], stup.span)
stup_count = cast(Column[Float[float]], stup.count)
stup_priority = cast(Column[Integer], stup.priority)


Index(
	"idx_stationpermissions",
	stup_stationFk,
	stup_userFk,
	stup_role,
	unique=True
)

path_user_permissions = Table("pathuserpermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("path", Text, nullable=False),
	Column("role", String(50), nullable=False),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationtimestamp", Double[float], nullable=False),
)

pup = path_user_permissions.c
pup_userFk = cast(Column[Integer], pup.userfk)
pup_path = cast(Column[String], pup.path)
pup_role = cast(Column[String], pup.role)
pup_priority = cast(Column[Integer], pup.priority)
pup_span = cast(Column[Float[float]], pup.span)
pup_count = cast(Column[Float[float]], pup.count)

#moving these to their own script
# Index(
# 	"idx_pathuserpermissions_userfk",
# 	pup_userFk
# )

# Index(
# 	"idx_pathpermissions",
# 	pup_userFk,
# 	pup_path,
# 	pup_role,
# 	unique=True
# )

friend_user_permissions = Table("frienduserpermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("friendfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationtimestamp", Double[float], nullable=False)
)
fup = friend_user_permissions.c
fup_friendFk = cast(Column[Integer], fup.friendfk)
fup_pk = cast(Column[Integer], fup.pk)
fup_userFk = cast(Column[Integer], fup.userfk)
fup_role = cast(Column[String], fup.role)
fup_span = cast(Column[Float[float]], fup.span)
fup_count = cast(Column[Float[float]], fup.count)
fup_priority = cast(Column[Integer], fup.priority)

Index(
	"idx_friendpermissions",
	fup_friendFk,
	fup_userFk,
	fup_role,
	unique=True
)

last_played = Table('lastplayed', metadata,
	Column('pk', Integer, primary_key=True, autoincrement=True),
	Column('stationfk', Integer, ForeignKey('stations.pk'), nullable=False),
	Column('songfk', Integer, ForeignKey('songs.pk'), nullable=False),
	Column('timestamp', Double[float], nullable=False)
)

lp = last_played.c
lp_stationFk = cast(Column[Integer], lp.stationfk)
lp_songFk = cast(Column[Integer], lp.songfk)
lp_timestamp = cast(Column[Double[float]], lp.timestamp)

Index(
	"idx_lastplayed",
	lp_stationFk,
	lp_songFk,
	unique=True
)




