from sqlalchemy import Table, \
	MetaData, \
	Column, \
	Float, \
	LargeBinary, \
	Integer, \
	String, \
	ForeignKey, \
	UniqueConstraint

metadata = MetaData()

artists = Table("Artists", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, unique=True),
)

albums = Table("Albums", metadata,
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=True, unique=True),
	Column("albumArtistFk", Integer, ForeignKey("Artists.pk"), nullable=True ),
	Column("year", Integer),
)

songs = Table("Songs", metadata, 
	Column("pk", Integer, primary_key=True),
	Column("path", String, nullable=True, unique=True),
	Column("name", String),
	Column("albumFk", Integer, ForeignKey("Albums.pk"), nullable=True),
	Column("track", Integer, nullable=True),
	Column("disc", Integer, nullable=True),
	Column("genre", String, nullable=True),
	Column('explicit', Integer, nullable=True),
	Column("bitrate", Float, nullable=True),
	Column("comment", String, nullable=True),
)

song_artist = Table("SongsArtists", metadata,
	Column("songFk", ForeignKey("Songs.pk"), nullable=False),
	Column("artistFk", ForeignKey("Artists.pk"), nullable=False),
	Column("isPrimaryArtist", Integer, nullable=True),
)

songCovers = Table("SongCovers", metadata,
	Column("pk", Integer, primary_key=True),
	Column("songFk", ForeignKey("Songs.pk"), nullable=False),
	Column("coverSongFk", ForeignKey("Songs.pk"), nullable=False),
	UniqueConstraint("songFk", "coverSongFk")
)

tags = Table("Tags", metadata, 
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=True, unique=True),
)

songs_tags = Table("SongsTags", metadata, 
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("tagFk", Integer, ForeignKey("Tags.pk"), nullable=False),
	Column("skip", Integer, nullable=True),
	UniqueConstraint("songFk", "tagFk")
)

stations = Table("Stations", metadata, 
	Column("pk", Integer, primary_key=True),
	Column("name", String, nullable=False, unique=True),
	Column("displayName", String, nullable=True),
	Column("procId", Integer, nullable=True),
)

stations_tags = Table("StationsTags", metadata, 
	Column("stationFk", Integer, nullable=False),
	Column("tagFk", Integer, nullable=False),
	UniqueConstraint("stationFk", "tagFk")
)

stations_history = Table("StationHistory", metadata, 
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("playedTimestamp", Float),
	Column("queuedTimestamp", Float),
	Column("requestedTimestamp", Float),
)

station_queue = Table("StationQueue", metadata,
	Column("stationFk", Integer, ForeignKey("Stations.pk"), nullable=False),
	Column("songFk", Integer, ForeignKey("Songs.pk"), nullable=False),
	Column("queuedTimestamp", Float),
	Column("requestedTimestamp", Float),
)

users = Table("Users", metadata,
	Column("pk", Integer, primary_key=True),
	Column("userName", String),
	Column("hashedPW", LargeBinary),
	Column("salt", LargeBinary),
	Column("email", String),
	Column("isActive", Integer),
)

