from typing import Any, cast, Optional
from sqlalchemy import (
	Table,
	MetaData,
	Column,
	Integer,
	Text,
	ForeignKey,
	Index,
	BLOB,
	REAL
)
from sqlalchemy.sql.schema import Column
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateTable, CreateIndex


metadata = MetaData()

def get_ddl_scripts(conn: Connection) -> str:
	
	result = ""
	for table in metadata.sorted_tables:
		result += str(CreateTable(table).compile(conn)).rstrip() + ";\n"
		for index in sorted(table.indexes or [], key=lambda i: i.name or ""):
			result += (str(CreateIndex(index).compile(conn)) + ";\n")

	return result

users = Table("users", metadata,
	Column("pk", Integer, primary_key=True),
	# Column("publicid", Text, nullable=False),
	Column("username", Text, nullable=False),
	Column("flatusername", Text, nullable=False),
	Column("displayname", Text, nullable=True),
	Column("hashedpw", BLOB, nullable=True),
	Column("email", Text, nullable=True),
	Column("dirroot", Text, nullable=True),
	Column("isdisabled", Integer, nullable=True),
	Column("creationtimestamp", REAL[Any], nullable=False),
	Column("viewsecuritylevel", Integer, nullable=True),
)



u = users.c
u_pk = cast(Column[Integer],u.pk)
# u_publicid = cast(Column[Text],u.publicid)
u_username = cast(Column[Text],u.username)
u_flatusername = cast(Column[Text],u.flatusername)
u_displayName = cast(Column[Optional[Text]],u.displayname)
u_hashedPW = cast(Column[BLOB],u.hashedpw)
u_email = cast(Column[Optional[Text]],u.email)
u_dirRoot = cast(Column[Optional[Text]],u.dirroot)
u_disabled = cast(Column[Optional[Integer]],u.isdisabled)
u_creationTimestamp = cast(Column[REAL[Any]],u.creationtimestamp)

Index("idx_uniqueusername", u_flatusername, unique=True)
Index("idx_uniqueemail", u_email, unique=True)
Index("idx_dirroot", u_dirRoot, unique=True)

artists = Table("artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", Text, nullable=False),
	Column("flatname", Text, nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"),\
		nullable=False),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
)

ar = artists.c
ar_pk = cast(Column[Integer],ar.pk)
ar_name = cast(Column[Text],ar.name)
ar_flatname = cast(Column[Text],ar.flatname)
ar_ownerFk = cast(Column[Integer],ar.ownerfk)

Index("idx_uniqueartistsname", ar_name, ar_ownerFk, unique=True)


albums = Table("albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", Text, nullable=False),
	Column("flatname", Text, nullable=False),
	Column("albumartistfk", Integer, ForeignKey("artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=False),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("versionnote", Text, nullable=True),
)

ab = albums.c
ab_pk = cast(Column[Integer],ab.pk)
ab_name = cast(Column[Optional[Text]],ab.name)
ab_flatname = cast(Column[Optional[Text]],ab.flatname)
ab_year = cast(Column[Optional[Integer]], ab.year)
ab_albumArtistFk = cast(Column[Optional[Integer]], ab.albumartistfk)
ab_ownerFk = cast(Column[Integer], ab.ownerfk)
ab_versionnote = cast(Column[Text], ab.versionnote)

Index(
	"idx_uniquealbumnameforartist2",
	ab_name,
	ab_albumArtistFk,
	ab_ownerFk,
	ab_versionnote,
	unique=True
)


playlists = Table('playlists', metadata,
	Column('pk', Integer, primary_key=True, autoincrement=True),
	Column("name", Text, nullable=False),
	Column("displayname", Text, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=False),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=False),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("viewsecuritylevel", Integer, nullable=True),
)

pl = playlists.c
pl_pk = cast(Column[Integer],pl.pk)
pl_name = cast(Column[Optional[Text]],pl.name)
pl_displayname = cast(Column[Optional[Text]],pl.displayname)
pl_lastmodifiedtimestamp = lastmodifiedtimestamp = cast(
	Column[REAL[Any]], pl.lastmodifiedtimestamp
)
pl_ownerFk = cast(Column[Integer], pl.ownerfk)
pl_viewSecurityLevel = cast(Column[Integer],pl.viewsecuritylevel)



songs = Table("songs", metadata,
	Column("pk", Integer, primary_key=True),
	Column("treepath", Text, nullable=False),
	Column("name", Text, nullable=True),
	Column("albumfk", Integer, ForeignKey("albums.pk"), nullable=True),
	Column("track", Text, nullable=True),
	Column("tracknum", REAL[Any], nullable=False, default=0),
	Column("discnum", Integer, nullable=True),
	Column("genre", Text, nullable=True),
	Column("explicit", Integer, nullable=True),
	Column("bitrate", REAL[Any], nullable=True),
	Column("notes", Text, nullable=True),
	Column("lyrics", Text, nullable=True),
	Column("duration", REAL[Any], nullable=True),
	Column("samplerate", REAL[Any], nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column("internalpath", Text, nullable=False),
	Column("filehash", BLOB, nullable=True),
	Column("deletedtimestamp", REAL[Any], nullable=True),
	Column("deletedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
)

sg = songs.c
sg_pk = cast(Column[Integer],sg.pk)
sg_name = cast(Column[Optional[Text]],sg.name)
sg_path = cast(Column[Text],sg.treepath)
sg_internalpath = cast(Column[Text],sg.internalpath)
sg_albumFk = cast(Column[Optional[Integer]], sg.albumfk)
sg_track = cast(Column[Optional[Text]], sg.track)
sg_trackNum = cast(Column[REAL[Any]], sg.tracknum)
sg_disc = cast(Column[Optional[Integer]], sg.discnum)
sg_genre = cast(Column[Optional[Text]], sg.genre)
sg_explicit = cast(Column[Optional[Integer]], sg.explicit)
sg_bitrate = cast(Column[Optional[REAL[Any]]], sg.bitrate)
sg_notes = cast(Column[Optional[Text]], sg.notes)
sg_lyrics = cast(Column[Optional[Text]], sg.lyrics)
sg_duration = cast(Column[Optional[REAL[Any]]], sg.duration)
sg_sampleRate = cast(Column[Optional[REAL[Any]]], sg.samplerate)
sg_deletedTimstamp = cast(Column[Integer], sg.deletedtimestamp)

Index("idx_uniquesongpath", sg_path, unique=True)


song_artist = Table("songsartists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("artistfk", Integer, ForeignKey("artists.pk"), nullable=False),
	Column("isprimaryartist", Integer, nullable=True),
	Column("notes", Text, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True)
)

sgar = song_artist.c
sgar_pk = cast(Column[Integer] ,sgar.pk)
sgar_songFk = cast(Column[Integer] ,sgar.songfk)
sgar_artistFk = cast(Column[Integer] ,sgar.artistfk)
sgar_isPrimaryArtist = cast(Column[Optional[Integer]],sgar.isprimaryartist)

Index("idx_songsartists", sgar_songFk, sgar_artistFk, unique=True)

playlists_songs = Table("playlistssongs", metadata,
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("playlistfk", Integer, ForeignKey("playlists.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column(
		"lexorder",
		BLOB,
		nullable=False,
		default=""
	),
)

plsg = playlists_songs.c
plsg_songFk = cast(Column[Integer] ,plsg.songfk)
plsg_playlistFk = cast(Column[Integer] ,plsg.playlistfk)
plsg_lexorder = cast(Column[BLOB], plsg.lexorder)
plsg_lastmodifiedtimestamp = cast(
	Column[REAL[Any]], plsg.lastmodifiedtimestamp
)


song_covers = Table("songcovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("coversongfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True)
)
_sc_songFk = cast(Column[Integer],song_covers.c.songfk)
_sc_coverSongFk = cast(Column[Integer],song_covers.c.coversongfk)
Index("idx_songcovers", _sc_songFk, _sc_coverSongFk, unique=True)


stations = Table("stations", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", Text, nullable=False),
	Column("displayname", Text, nullable=True),
	Column("procid", Integer, nullable=True),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column("ownerfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("requestsecuritylevel", Integer, nullable=True),
	Column("viewsecuritylevel", Integer, nullable=True),
	Column("typeid", Integer, nullable=False, default=0),
	Column("bitratekps", Integer, nullable=True),
	Column("playnum", Integer, nullable=False, default=1)
)

st = stations.c
st_pk = cast(Column[Integer],st.pk)
st_name = cast(Column[Text],st.name)
st_displayName = cast(Column[Text],st.displayname)
st_procId = cast(Column[Integer],st.procid)
st_ownerFk = cast(Column[Integer],st.ownerfk)
st_requestSecurityLevel = cast(Column[Integer],st.requestsecuritylevel)
st_viewSecurityLevel = cast(Column[Integer],st.viewsecuritylevel)
st_typeid = cast(Column[Integer],st.typeid)
st_bitrate = cast(Column[Optional[Integer]], st.bitratekps)
st_playnum = cast(Column[Integer],st.playnum)
Index("idx_uniquestationname", st_name, st_ownerFk, unique=True)


stations_songs = Table("stationssongs", metadata,
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
	Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column("lastplayednum", Integer, nullable=False, default=0)
)
stsg = stations_songs.c

stsg_songFk = cast(Column[Integer], stations_songs.c.songfk)
stsg_stationFk = cast(Column[Integer], stations_songs.c.stationfk)
stsg_lastmodifiedtimestamp = cast(
	Column[REAL[Any]], stations_songs.c.lastmodifiedtimestamp
)
stsg_lastplayednum = cast(Column[Integer], stsg.lastplayednum)
Index("idx_stationssongs", stsg_songFk, stsg_stationFk, unique=True)


stations_albums = Table("stationsalbums",metadata,
	Column("albumfk", Integer, ForeignKey("albums.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
		Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column("lastplayednum", Integer, nullable=False, default=0)
)
stab = stations_albums.c

stab_albumFk = cast(Column[Integer], stab.albumfk)
stab_stationFk = cast(Column[Integer], stab.stationfk)
stab_lastmodifiedtimestamp = cast(
	Column[REAL[Any]],
	stab.lastmodifiedtimestamp
)
stab_lastplayednum = cast(Column[Integer], stab.lastplayednum)
Index("idx_stationsalbums", stab_albumFk, stab_stationFk, unique=True)


stations_playlists = Table("stationsplaylists",metadata,
	Column("playlistfk", Integer, ForeignKey("playlists.pk"), nullable=False),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
		Column("lastmodifiedbyuserfk", Integer, ForeignKey("users.pk"), \
		nullable=True),
	Column("lastmodifiedtimestamp", REAL[Any], nullable=True),
	Column("lastplayednum", Integer, nullable=False, default=0)
)
stpl = stations_playlists.c

stpl_playlistFk = cast(Column[Integer], stpl.playlistfk)
stpl_stationFk = cast(Column[Integer], stpl.stationfk)
stpl_lastmodifiedtimestamp = cast(
	Column[REAL[Any]],
	stpl.lastmodifiedtimestamp
)
stpl_lastplayednum = cast(Column[Integer], stpl.lastplayednum)
Index("idx_stationsplaylists", stpl_playlistFk, stpl_stationFk, unique=True)


userRoles = Table("userroles", metadata,
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=False),
	Column("role", Text),
	Column("span", REAL[Any], nullable=False),
	Column("quota", REAL[Any], nullable=False),
	Column("priority", Integer),
	Column("sphere", Text, nullable=False),
	Column("keypath", Text, nullable=True),
	Column("creationtimestamp", REAL[Any], nullable=False)
)
ur_userFk = cast(Column[Integer], userRoles.c.userfk)
ur_role = cast(Column[Text], userRoles.c.role)
ur_span = cast(Column[REAL[Any]], userRoles.c.span)
ur_quota = cast(Column[REAL[Any]], userRoles.c.quota)
ur_priority = cast(Column[Integer], userRoles.c.priority)
ur_sphere = cast(Column[Text], userRoles.c.sphere)
ur_keypath = cast(Column[Text], userRoles.c.keypath)
Index("idx_userroles", ur_userFk, ur_sphere, ur_role, ur_keypath, unique=True)


user_agents = Table("visitors",metadata,
	Column("pk", Integer, primary_key=True),
	Column("useragenttxt", Text, nullable=False),
	Column("hashua", BLOB, nullable=False),
	Column("lengthua", Integer, nullable=False),
	Column("ipv4address", Text, nullable=True),
	Column("ipv6address", Text, nullable=True),
)

uag_pk = cast(Column[Integer], user_agents.c.pk)
uag_content = cast(Column[Text], user_agents.c.useragenttxt)
uag_hash = cast(Column[BLOB], user_agents.c.hashua)
uag_length = cast(Column[Integer], user_agents.c.lengthua)
uag_ipv4Address = cast(Column[Text], user_agents.c.ipv4address)
uag_ipv6Address = cast(Column[Text], user_agents.c.ipv6address)

Index(
	"idx_vistor",
	uag_ipv6Address,
	uag_ipv4Address,
	uag_hash,
	uag_length
)


station_queue = Table("stationlogs", metadata,
	Column("pk", Integer, primary_key=True),
	Column("stationfk", Integer, ForeignKey("stations.pk"), nullable=False),
	Column("songfk", Integer, ForeignKey("songs.pk"), nullable=True),
	Column("itemtype", Text, nullable=False, default="song"),
	Column("action", Text, nullable=True),
	Column("parentkey", Integer, nullable=True),
	Column("queuedtimestamp", REAL[Any], nullable=False),
	Column("playedtimestamp", REAL[Any], nullable=True),
	Column("userfk", Integer, ForeignKey("users.pk"), nullable=True),
)

q = station_queue.c
q_pk = cast(Column[Integer], q.pk)
q_songFk = cast(Column[Integer], q.songfk)
q_stationFk = cast(Column[Integer], q.stationfk)
q_itemType = cast(Column[Text], q.itemtype)
q_action = cast(Column[Text], q.action)
q_parentKey = cast(Column[Integer], q.parentkey)
q_timestamp = cast(Column[Optional[REAL[Any]]],q.playedtimestamp)
q_queuedTimestamp = cast(Column[REAL[Any]], q.queuedtimestamp)

Index("idx_stationlogsstations", q_stationFk)


last_played = Table('lastplayed', metadata,
	Column("pk", Integer, primary_key=True, autoincrement=True),
	Column("stationfk", Integer, ForeignKey('stations.pk'), nullable=False),
	Column("songfk", Integer, ForeignKey('songs.pk'), nullable=False),
	Column("playedtimestamp", REAL[Any], nullable=False),
	Column("itemtype", Text, nullable=False, default="song"),
	Column("parentkey", Integer, nullable=True)
)

lp = last_played.c
lp_stationFk = cast(Column[Integer], lp.stationfk)
lp_songFk = cast(Column[Integer], lp.songfk)
lp_timestamp = cast(Column[REAL[Any]], lp.playedtimestamp)
lp_itemType = cast(Column[Text], lp.itemtype)
lp_parentKey = cast(Column[Integer], lp.parentkey)

Index(
	"idx_lastplayed2",
	lp_stationFk,
	lp_songFk,
	lp_itemType,
	lp_parentKey,
	unique=True
)


jobs = Table('jobs', metadata,
	Column('pk', Integer, primary_key=True, autoincrement=True),
	Column("jobtype", Text, nullable=False),
	Column("status", Text, nullable=True),
	Column("instructions", Text, nullable=True),
	Column("queuedtimestamp", REAL[Any], nullable=False),
	Column('completedtimestamp', REAL[Any], nullable=True)
)

j = jobs.c
j_pk = cast(Column[Integer], j.pk)
j_type = cast(Column[Text], j.jobtype)
j_status = cast(Column[Text], j.status)
j_instructions = cast(Column[Text], j.instructions)
j_queuedtimestamp = cast(Column[REAL[Any]], j.queuedtimestamp)
j_completedtimestamp = cast(Column[REAL[Any]], j.completedtimestamp)

