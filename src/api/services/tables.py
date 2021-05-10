from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey

metadata = MetaData()

folders = Table("Folders", metadata, 
  Column("pk"),
  Column("name"),
)

songs = Table("Songs", metadata, 
  Column("pk"),
  Column("path"),
  Column("folderFK"),
  Column("title"),
  Column("artist"),
  Column("albumArtist"),
  Column("album"),
  Column("trackNum"),
  Column("discNum"),
  Column("genre"),
  Column("songCoverFK"),
)

tags = Table("Tags", metadata, 
  Column("pk"),
  Column("name"),
)

songs_tags = Table("SongsTags", metadata, 
  Column("songFK"),
  Column("tagFK"),
  Column("skip"),
)

stations = Table("Stations", metadata, 
  Column("pk"),
  Column("name"),
  Column("displayName"),
  Column("procId"),
)

stations_tags = Table("StationsTags", metadata, 
  Column("stationFK"),
  Column("tagFK"),
)

stations_history = Table("StationHistory", metadata, 
  Column("stationFK"),
  Column("songFK"),
  Column("lastPlayedTimestamp"),
  Column("lastQueuedTimestamp"),
  Column("lastRequestedTimestamp"),
)

station_queue = Table("StationQueue", metadata,
    Column("stationFK"),
    Column("songFK"),
    Column("addedTimestamp"),
    Column("requestedTimestamp"),
)