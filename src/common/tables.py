from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey

metadata = MetaData()

folders = Table("Folders", metadata, 
  Column("pk"),
  Column("name"),
)

songs = Table("Songs", metadata, 
  Column("pk"),
  Column("path"),
  Column("folderFk"),
  Column("title"),
  Column("artist"),
  Column("albumArtist"),
  Column("album"),
  Column("trackNum"),
  Column("discNum"),
  Column("genre"),
  Column("songCoverFk"),
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