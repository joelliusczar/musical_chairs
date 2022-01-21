from sqlalchemy import Table, MetaData, Column, Integer, REAL

metadata = MetaData()

artists = Table("Artists", metadata,
  Column("pk"),
  Column("name"),
)

albums = Table("Albums", metadata,
  Column("pk"),
  Column("name"),
  Column("albumArtistFk"),
  Column("year"),
)

songs = Table("Songs", metadata, 
  Column("pk"),
  Column("path"),
  Column("title"),
  Column("albumFk"),
  Column("track"),
  Column("disc"),
  Column("genre"),
  Column("songCoverFk"),
  Column("bitrate"),
  Column("comment"),
)

song_artist = Table("SongArtists", metadata,
  Column("songFk"),
  Column("artistFk"),
  Column("isPrimaryArtist"),
)

tags = Table("Tags", metadata, 
  Column("pk"),
  Column("name"),
)

songs_tags = Table("SongsTags", metadata, 
  Column("songFk"),
  Column("tagFk"),
  Column("skip"),
)

stations = Table("Stations", metadata, 
  Column("pk"),
  Column("name"),
  Column("displayName"),
  Column("procId"),
)

stations_tags = Table("StationsTags", metadata, 
  Column("stationFk"),
  Column("tagFk"),
)

stations_history = Table("StationHistory", metadata, 
  Column("stationFk"),
  Column("songFk"),
  Column("lastPlayedTimestamp"),
  Column("lastQueuedTimestamp"),
  Column("lastRequestedTimestamp"),
)

station_queue = Table("StationQueue", metadata,
    Column("stationFk"),
    Column("songFk"),
    Column("addedTimestamp"),
    Column("requestedTimestamp"),
)

# temp table definition
last_history_tmp = Table('LastHistory', metadata,
  Column("songFk", Integer),
  Column("lastQueued", REAL),
  prefixes=["TEMP"]
)