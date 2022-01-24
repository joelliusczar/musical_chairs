SELECT "data_def_1.sql";


CREATE TABLE IF NOT EXISTS [Artists] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_artist ON [Artists] ([Name]);

CREATE TABLE IF NOT EXISTS [Albums] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL,
    [AlbumArtistFK] INTEGER NULL,
    [Year] INTEGER,
    FOREIGN KEY([AlbumArtistFK]) REFERENCES [Artists]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_albums ON [Albums] ([Name]);

CREATE TABLE IF NOT EXISTS [Songs] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Path] TEXT NULL,
    [Title] TEXT,
    [AlbumFK] INTEGER NULL,
    [Track] INTEGER NULL,
    [Disc] INTEGER NULL,
    [Genre] TEXT,
    [Explicit] INTEGER,
    [Bitrate] REAL,
    [Comment] TEXT,
    FOREIGN KEY([AlbumFK]) REFERENCES [Albums]([PK])
);

CREATE TABLE IF NOT EXISTS [SongsArtists] (
    [SongFK] INTEGER NOT NULL,
    [ArtistFK] INTEGER NOT NULL,
    [IsPrimaryArtist] INTEGER NULL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([ArtistFK]) REFERENCES [Artists]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_songsArtists ON [SongsArtists]([SongFK], [ArtistFK]);

CREATE TABLE IF NOT EXISTS [SongCovers] (
    [PK] INTEGER PRIMARY KEY ASC,
    [SongFK] INTEGER NOT NULL,
    [CoverSongFK] INTEGER NOT NULL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([CoverSongFK]) REFERENCES [Songs]([PK]) 
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cover ON [SongCovers] ([SongFK], [CoverSongFK]);

--don't want to insert duplicate songs
CREATE UNIQUE INDEX IF NOT EXISTS idx_path ON [Songs] ([Path]);

CREATE TABLE IF NOT EXISTS [Tags] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_tags ON [Tags] ([Name]);

CREATE TABLE IF NOT EXISTS [SongsTags] (
    [SongFK] INTEGER NOT NULL,
    [TagFK] INTEGER NOT NULL,
    [Skip] INTEGER NULL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_songsTags ON [SongsTags]([SongFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [Stations] (
    [PK] INTEGER PRIMARY KEY ASC,
    [Name] TEXT NOT NULL,
    [DisplayName] TEXT NULL,
    [ProcId] INTEGER NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stations ON [Stations] ([Name]);

CREATE TABLE IF NOT EXISTS [StationsTags] (
    [StationFK] INTEGER NOT NULL,
    [TagFK] INTEGER NOT NULL,
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK]),
    FOREIGN KEY([TagFK]) REFERENCES [Tags]([PK])
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stationsTags ON [StationsTags]([StationFK], [TagFK]);

CREATE TABLE IF NOT EXISTS [StationHistory] (
    [StationFK] INTEGER NOT NULL,
    [SongFK] INTEGER NOT NULL,
    [LastPlayedTimestamp] REAL,
    [LastQueuedTimestamp] REAL,
    [LastRequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK])
);

CREATE TABLE IF NOT EXISTS [StationQueue] (
    [StationFK] INTEGER NOT NULL,
    [SongFK] INTEGER NOT NULL,
    [AddedTimestamp] REAL,
    [RequestedTimestamp] REAL,
    FOREIGN KEY([SongFK]) REFERENCES [Songs]([PK]),
    FOREIGN KEY([StationFK]) REFERENCES [Station]([PK])
);
