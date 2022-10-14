from typing import Any
from sqlalchemy import Table,\
	MetaData,\
	Column,\
	Float,\
	LargeBinary,\
	Integer,\
	String,\
	ForeignKey,\
	Index
from sqlalchemy.sql import ColumnCollection as TblCols
from sqlalchemy.sql.schema import Column



metadata = MetaData()

users = Table("Users", metadata,
	Column("pk", Integer, primary_key=True),
	Column("username", String, nullable=False),
	Column("displayName", String, nullable=True),
	Column("hashedPW", LargeBinary, nullable=True),
	Column("email", String, nullable=True),
	Column("isDisabled", Integer, nullable=True),
	Column("creationTimestamp", Float, nullable=False)
)
_u_username: Any = users.c.username #pyright: ignore reportUnknownMemberType
Index("idx_uniqueUsername", _u_username, unique=True)
_u_email: Any = users.c.email #pyright: ignore reportUnknownMemberType
Index("idx_uniqueEmail", _u_email, unique=True)

artists = Table("Artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)

_ar_name: Any = artists.c.name #pyright: ignore reportUnknownMemberType
Index("idx_uniqueArtistsName", _ar_name, unique=True)


albums = Table("Albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("albumArtistFk", Integer, ForeignKey("Artists.pk"), nullable=True),
	Column("year", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_ab_name: Any = albums.c.name #pyright: ignore reportUnknownMemberType
_ab_albumArtistFk: Any = albums.c.albumArtistFk #pyright: ignore reportUnknownMemberType
Index("idx_uniqueAlbumNameForArtist", _ab_name, _ab_albumArtistFk, unique=True)

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
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_sg_path: Any = songs.c.path #pyright: ignore reportUnknownMemberType
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
_sa_songFk: Any = song_artist.c.songFk #pyright: ignore reportUnknownMemberType
_sa_artistFk: Any = song_artist.c.artistFk #pyright: ignore reportUnknownMemberType

Index("idx_songsArtists", _sa_songFk, _sa_artistFk, unique=True)

song_covers = Table("SongCovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", ForeignKey("Songs.pk"), nullable=False),
	Column("coverSongFk", ForeignKey("Songs.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_sc_songFk: Any = song_covers.c.songFk #pyright: ignore reportUnknownMemberType
_sc_coverSongFk: Any = song_covers.c.coverSongFk #pyright: ignore reportUnknownMemberType
Index("idx_songCovers", _sc_songFk, _sc_coverSongFk, unique=True)

tags = Table("Tags", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_tg_name: Any = tags.c.name #pyright: ignore reportUnknownMemberType
Index("idx_uniqueTagName", _tg_name, unique=True)

songs_tags = Table("SongsTags", metadata,
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("tagFk", Integer, ForeignKey("Tags.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
sgtg_songFk: Any = songs_tags.c.songFk #pyright: ignore reportUnknownMemberType
sgtg_tagFk: Any = songs_tags.c.tagFk #pyright: ignore reportUnknownMemberType
Index("idx_songsTags", sgtg_songFk, sgtg_tagFk, unique=True)

stations = Table("Stations", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False),
	Column("displayName", String, nullable=True),
	Column("procId", Integer, nullable=True),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)
_st_name: Any = stations.c.name #pyright: ignore reportUnknownMemberType
Index("idx_uniqueStationName", _st_name, unique=True)

stations_tags = Table("StationsTags", metadata,
	Column("stationFk", Integer, nullable=False),
	Column("tagFk", Integer, nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)

_sttg_stationFk: Any = stations_tags.c.stationFk #pyright: ignore reportUnknownMemberType
_sttg_tagFk: Any = stations_tags.c.tagFk #pyright: ignore reportUnknownMemberType
Index("idx_stationsTags", _sttg_stationFk, _sttg_tagFk, unique=True)

banned_songs_stations =  Table("BannedSongsStations", metadata,
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("lastModifiedByUserFk", Integer, ForeignKey("Users.pk"), \
		nullable=True),
	Column("lastModifiedTimestamp", Float, nullable=True)
)

_bsgst_stationFk: Any = banned_songs_stations.c.stationFk #pyright: ignore reportUnknownMemberType
_bsgst_songFk: Any = banned_songs_stations.c.songFk #pyright: ignore reportUnknownMemberType
Index("idx_bannedSongStation", _bsgst_stationFk, _bsgst_songFk, unique=True)

stations_history = Table("StationHistory", metadata,
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("playedTimestamp", Float),
	Column("queuedTimestamp", Float),
	Column("requestedTimestamp", Float),
	Column("requestedByUserFk", Integer, ForeignKey("Users.pk"), nullable=True)
)

station_queue = Table("StationQueue", metadata,
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("queuedTimestamp", Float),
	Column("requestedTimestamp", Float),
	Column("requestedByUserFk", Integer, ForeignKey("Users.pk"), nullable=True)
)



userRoles = Table("UserRoles", metadata,
	Column("userFk", Integer, ForeignKey("Users.pk"), nullable=False),
	Column("role", String),
	Column("creationTimestamp", Float, nullable=False)
)
_ur_userFk: Any = userRoles.c.userFk #pyright: ignore reportUnknownMemberType
_ur_role: Any = userRoles.c.role #pyright: ignore reportUnknownMemberType
Index("idx_userRoles", _ur_userFk, _ur_role, unique=True)


sg: TblCols = songs.c #pyright: ignore [reportUnknownMemberType]
sg_pk: Column = sg.pk #pyright: ignore [reportUnknownMemberType]
sg_name: Column = sg.name #pyright: ignore [reportUnknownMemberType]
sg_path: Column = sg.path #pyright: ignore [reportUnknownMemberType]
sg_albumFk: Column = sg.albumFk #pyright: ignore [reportUnknownMemberType]
sg_track: Column = sg.track #pyright: ignore [reportUnknownMemberType]
sg_disc: Column = sg.disc #pyright: ignore [reportUnknownMemberType]
sg_genre: Column = sg.genre #pyright: ignore [reportUnknownMemberType]
sg_explicit: Column = sg.explicit #pyright: ignore [reportUnknownMemberType]
sg_bitrate: Column = sg.bitrate #pyright: ignore [reportUnknownMemberType]
sg_comment: Column = sg.comment #pyright: ignore [reportUnknownMemberType]
sg_lyrics: Column = sg.lyrics #pyright: ignore [reportUnknownMemberType]
sg_duration: Column = sg.duration #pyright: ignore [reportUnknownMemberType]
sg_sampleRate: Column = sg.sampleRate #pyright: ignore [reportUnknownMemberType]

ab: TblCols = albums.c #pyright: ignore [reportUnknownMemberType]
ab_pk: Column = ab.pk #pyright: ignore [reportUnknownMemberType]
ab_name: Column = ab.name #pyright: ignore [reportUnknownMemberType]
ab_year: Column = ab.year #pyright: ignore [reportUnknownMemberType]
ab_albumArtistFk: Column = ab.albumArtistFk #pyright: ignore [reportUnknownMemberType]

ar: TblCols = artists.c #pyright: ignore [reportUnknownMemberType]
ar_pk: Column = ar.pk #pyright: ignore [reportUnknownMemberType]
ar_name: Column = ar.name #pyright: ignore [reportUnknownMemberType]

tg: TblCols = tags.c #pyright: ignore [reportUnknownMemberType]
tg_pk: Column = tg.pk #pyright: ignore [reportUnknownMemberType]
tg_name: Column = tg.name #pyright: ignore [reportUnknownMemberType]


st: TblCols = stations.c #pyright: ignore [reportUnknownMemberType]
st_pk: Column = st.pk #pyright: ignore [reportUnknownMemberType]
st_name: Column = st.name #pyright: ignore [reportUnknownMemberType]

sgar: TblCols = song_artist.c #pyright: ignore [reportUnknownMemberType]
sgar_pk: Column = sgar.pk #pyright: ignore [reportUnknownMemberType]
sgar_songFk: Column = sgar.songFk #pyright: ignore [reportUnknownMemberType]
sgar_artistFk: Column = sgar.artistFk #pyright: ignore [reportUnknownMemberType]
sgar_isPrimaryArtist: Column = sgar.isPrimaryArtist #pyright: ignore [reportUnknownMemberType]

sgtg: TblCols = songs_tags.c #pyright: ignore [reportUnknownMemberType]
sgtg_tagFk: Column = sgtg.tagFk #pyright: ignore [reportUnknownMemberType]
sgtg_songFk: Column = sgtg.songFk #pyright: ignore [reportUnknownMemberType]

sttg: TblCols = stations_tags.c #pyright: ignore [reportUnknownMemberType]
sttg_tagFk: Column = sttg.tagFk #pyright: ignore [reportUnknownMemberType]
sttg_stationFk: Column = sttg.stationFk #pyright: ignore [reportUnknownMemberType]

q: TblCols = station_queue.c #pyright: ignore [reportUnknownMemberType]
q_songFk: Column = q.songFk #pyright: ignore [reportUnknownMemberType]
q_stationFk: Column = q.stationFk #pyright: ignore [reportUnknownMemberType]
q_queuedTimestamp: Column = q.queuedTimestamp #pyright: ignore [reportUnknownMemberType]
