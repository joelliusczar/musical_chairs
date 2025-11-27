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
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateTable, CreateIndex


metadata = MetaData()

def get_ddl_scripts(conn: Connection) -> str:
	
	result = ""
	for table in metadata.sorted_tables:
		result += str(CreateTable(table).compile(conn))
		for index in sorted(table.indexes or [], key=lambda i: i.name or ""):
			result += (str(CreateIndex(index).compile(conn)) + "\n")

	return result

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
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("versionnote", String(200), nullable=True),
)

ab = albums.c
ab_pk = cast(Column[Integer],ab.pk)
ab_name = cast(Column[Optional[String]],ab.name)
ab_year = cast(Column[Optional[Integer]], ab.year)
ab_albumArtistFk = cast(Column[Optional[Integer]], ab.albumartistfk)
ab_ownerFk = cast(Column[Integer], ab.ownerfk)
ab_versionnote = cast(Column[String], ab.versionnote)

Index(
	"idx_uniquealbumnameforartist",
	ab_name,
	ab_albumArtistFk,
	ab_ownerFk,
	unique=True
)

playlists = Table('playlists', metadata,
	Column('pk', Integer, primary_key=True, autoincrement=True),
	Column("name", String(100), nullable=False),
	Column("description", String(1000), nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=False),
	Column("lastmodifiedtimestamp", Double[float], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("viewsecuritylevel", Integer, nullable=True),
)

pl = playlists.c
pl_pk = cast(Column[Integer],pl.pk)
pl_name = cast(Column[Optional[String]],pl.name)
pl_description = cast(Column[Optional[String]],pl.description)
pl_ownerFk = cast(Column[Integer], pl.ownerfk)
pl_viewSecurityLevel = cast(Column[Integer],pl.viewsecuritylevel)



songs = Table("songs", metadata,
	Column("pk", Integer, primary_key=True),
	Column("path", String(2000), nullable=False),
	Column("name", String(200), nullable=True),
	Column("albumfk", Integer, ForeignKey("albums.pk"), nullable=True),
	Column("track", String(20), nullable=True),
	Column("tracknum", Float[float], nullable=False, default=0),
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
	Column("hash", BINARY(64), nullable=True),
	Column("deletedtimestamp", Double[float], nullable=True),
	Column("deletedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
)

sg = songs.c
sg_pk = cast(Column[Integer],sg.pk)
sg_name = cast(Column[Optional[String]],sg.name)
sg_path = cast(Column[String],sg.path)
sg_internalpath = cast(Column[String],sg.internalpath)
sg_albumFk = cast(Column[Optional[Integer]], sg.albumfk)
sg_track = cast(Column[Optional[String]], sg.track)
sg_trackNum = cast(Column[Float[float]], sg.tracknum)
sg_disc = cast(Column[Optional[Integer]], sg.disc)
sg_genre = cast(Column[Optional[String]], sg.genre)
sg_explicit = cast(Column[Optional[Integer]], sg.explicit)
sg_bitrate = cast(Column[Optional[Float[float]]], sg.bitrate)
sg_comment = cast(Column[Optional[String]], sg.comment)
sg_lyrics = cast(Column[Optional[String]], sg.lyrics)
sg_duration = cast(Column[Optional[Float[float]]], sg.duration)
sg_sampleRate = cast(Column[Optional[Float[float]]], sg.samplerate)
sg_isdirplacholhder = cast(Column[Boolean], sg.isdirectoryplaceholder)
sg_deletedTimstamp = cast(Column[Boolean], sg.deletedtimestamp)

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

playlists_songs = Table("playlistssongs", metadata,
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("playlistfk", Integer, ForeignKey("playlists.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True),
	Column("order", Float[float], nullable=False, default=0),
)

plsg = playlists_songs.c
plsg_songFk = cast(Column[Integer] ,plsg.songfk)
plsg_playlistFk = cast(Column[Integer] ,plsg.playlistfk)
plsg_order = cast(Column[Float[float]], plsg.order)


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
	Column("typeid", Integer, nullable=False, default=0),
	Column("bitratekps", Integer, nullable=True),
)

st = stations.c
st_pk = cast(Column[Integer],st.pk)
st_name = cast(Column[String],st.name)
st_displayName = cast(Column[String],st.displayname)
st_procId = cast(Column[Integer],st.procid)
st_ownerFk = cast(Column[Integer],st.ownerfk)
st_requestSecurityLevel = cast(Column[Integer],st.requestsecuritylevel)
st_viewSecurityLevel = cast(Column[Integer],st.viewsecuritylevel)
st_typeid = cast(Column[Integer],st.typeid)
st_bitrate = cast(Column[Optional[Integer]], st.bitratekps)
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

stations_albums = Table("stationsalbums",metadata,
	Column("albumfk", Integer, ForeignKey("albums.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
		Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True)
)
stab = stations_albums.c

stab_albumFk = cast(Column[Integer], stab.albumfk)
stab_stationFk = cast(Column[Integer], stab.stationfk)
stab_lastmodifiedtimestamp = cast(
	Column[Double[float]],
	stab.lastmodifiedtimestamp
)
Index("idx_stationsalbums", stab_albumFk, stab_stationFk, unique=True)

stations_playlists = Table("stationsplaylists",metadata,
	Column("playlistfk", Integer, ForeignKey("playlists.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
		Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", Double[float], nullable=True)
)
stpl = stations_playlists.c

stpl_playlistFk = cast(Column[Integer], stpl.playlistfk)
stpl_stationFk = cast(Column[Integer], stpl.stationfk)
stpl_lastmodifiedtimestamp = cast(
	Column[Double[float]],
	stpl.lastmodifiedtimestamp
)
Index("idx_stationsplaylists", stpl_playlistFk, stpl_stationFk, unique=True)


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

user_agents = Table("useragents",metadata,
	Column("pk", Integer, primary_key=True),
	Column("content", Text, nullable=False),
	Column("hash", BINARY(16), nullable=False),
	Column("length", Integer, nullable=False),
)

uag_pk = cast(Column[Integer], user_agents.c.pk)
uag_content = cast(Column[String], user_agents.c.content)
uag_hash = cast(Column[BINARY], user_agents.c.hash)
uag_length = cast(Column[Integer], user_agents.c.length)

Index("idx_useragenthash", uag_hash)

user_action_history = Table("useractionhistory", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=True),
	Column("action", String(50), nullable=False),
	Column("timestamp", Double[float], nullable=True),
	Column("queuedtimestamp", Double[float], nullable=False),
	Column("ipv4address", String(24), nullable=True),
	Column("ipv6address", String(50), nullable=True),
	Column("useragentsfk", Integer, ForeignKey("useragents.pk"), nullable=True),
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

playlist_user_permissions = Table("playlistuserpermissions", metadata,
	Column("pk", Integer, primary_key=True),
	Column("playlistfk", Integer, ForeignKey("playlists.pk"), nullable=False),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("role", String(50)),
	Column("span", Float[float], nullable=False),
	Column("count", Float[float], nullable=False),
	Column("priority", Integer),
	Column("creationtimestamp", Double[float], nullable=False)
)

plup = playlist_user_permissions.c
plup_playlistFk = cast(Column[Integer], plup.playlistfk)
plup_pk = cast(Column[Integer], plup.pk)
plup_userFk = cast(Column[Integer], plup.userfk)
plup_role = cast(Column[String], plup.role)
plup_span = cast(Column[Float[float]], plup.span)
plup_count = cast(Column[Float[float]], plup.count)
plup_priority = cast(Column[Integer], plup.priority)

Index(
	"idx_playlistpermissions",
	plup_playlistFk,
	plup_userFk,
	plup_role,
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

jobs = Table('jobs', metadata,
	Column('pk', Integer, primary_key=True, autoincrement=True),
	Column("jobtype", String(50), nullable=False),
	Column("status", String(50), nullable=True),
	Column("instructions", String(2000), nullable=True),
	Column("queuedtimestamp", Double[float], nullable=False),
	Column('completedtimestamp', Double[float], nullable=True)
)

j = jobs.c
j_pk = cast(Column[Integer], j.pk)
j_type = cast(Column[String], j.jobtype)
j_status = cast(Column[String], j.status)
j_instructions = cast(Column[String], j.instructions)
j_queuedtimestamp = cast(Column[Double[float]], j.queuedtimestamp)
j_completedtimestamp = cast(Column[Double[float]], j.completedtimestamp)

