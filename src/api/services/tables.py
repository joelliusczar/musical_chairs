from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey

metadata = MetaData()

folders = Table("Folders", metadata, 
  Column("folderPK"),
  Column("name"),
)

songs = Table("Songs", metadata, 
  Column("songPK"),
  Column("path"),
  Column("folderFK"),
)

tags = Table("Tags", metadata, 
  Column("tagPK"),
  Column("name"),
)

songs_tags = Table("SongsTags", metadata, 
  Column("songFK"),
  Column("tagFK"),
  Column("skip"),
)

stations = Table("Stations", metadata, 
  Column("stationPK"),
  Column("name"),
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