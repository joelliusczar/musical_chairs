CREATE TABLE IF NOT EXISTS [Folders] (
    [FolderPK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_folderName ON [Folders] ([Name]);

CREATE TABLE IF NOT EXISTS [Songs] (
    [SongPK] INTEGER PRIMARY KEY ASC,
    [Path] TEXT NULL,
    [FolderFK] INTEGER,
    FOREIGN KEY([FolderFK]) REFERENCES [Folders]([FolderPK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_path ON [Songs] ([Path]);

CREATE TABLE IF NOT EXISTS [Tags] (
    [TagPK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE TABLE IF NOT EXISTS [SongsTags] (
    [SongFK] INTEGER,
    [TagFK] INTEGER,
    [Skip] INTEGER,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([SongPK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([TagPK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_songsTags ON [SongsTags]([SongFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [Stations] (
    [StationPK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL,
    [ProcId] INTEGER NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stations ON [Stations] ([Name]);

CREATE TABLE IF NOT EXISTS [StationsTags] (
    [StationFK] INTEGER,
    [TagFK] INTEGER,
    FOREIGN KEY([StationFK]) REFERENCES [Station]([StationPK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([TagPK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stationsTags ON [StationsTags]([StationFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [StationHistory] (
    [StationFK] INTEGER,
    [SongFK] INTEGER,
    [LastPlayedTimestamp] REAL,
    [LastQueuedTimestamp] REAL,
    [LastRequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([SongPK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([StationPK])
);

CREATE TABLE IF NOT EXISTS [StationQueue] (
    [StationFK] INTEGER,
    [SongFK] INTEGER,
    [AddedTimestamp] REAL,
    [RequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([SongPK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([StationPK])
);
