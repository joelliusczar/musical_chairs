CREATE TABLE IF NOT EXISTS [Folders] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_folderName ON [Folders] ([Name]);


CREATE TABLE IF NOT EXISTS [Songs] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Path] TEXT NULL,
    [FolderFK] INTEGER,
    [Title] TEXT,
    [Artist] TEXT,
    [AlbumArtist] TEXT,
    [Album] TEXT,
    [TrackNum] INTEGER NULL,
    [DiscNum] INTEGER NULL,
    [Genre] TEXT,
    [SongCoverFK] INTEGER NULL,
    FOREIGN KEY([FolderFK]) REFERENCES [Folders]([PK])
);

CREATE TABLE IF NOT EXISTS [SongCovers] (
    [PK] INTEGER PRIMARY KEY ASC,
    [SongFK] INTEGER,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
);

--don't want to insert duplicate songs
CREATE UNIQUE INDEX IF NOT EXISTS idx_path ON [Songs] ([Path]);

CREATE TABLE IF NOT EXISTS [Tags] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE TABLE IF NOT EXISTS [SongsTags] (
    [SongFK] INTEGER,
    [TagFK] INTEGER,
    [Skip] INTEGER,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_songsTags ON [SongsTags]([SongFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [Stations] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL,
    [DisplayName] TEXT NULL,
    [ProcId] INTEGER NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stations ON [Stations] ([Name]);

CREATE TABLE IF NOT EXISTS [StationsTags] (
    [StationFK] INTEGER,
    [TagFK] INTEGER,
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stationsTags ON [StationsTags]([StationFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [StationHistory] (
    [StationFK] INTEGER,
    [SongFK] INTEGER,
    [LastPlayedTimestamp] REAL,
    [LastQueuedTimestamp] REAL,
    [LastRequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK])
);

CREATE TABLE IF NOT EXISTS [StationQueue] (
    [StationFK] INTEGER,
    [SongFK] INTEGER,
    [AddedTimestamp] REAL,
    [RequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK])
);
