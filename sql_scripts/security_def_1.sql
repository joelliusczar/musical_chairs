CREATE TABLE IF NOT EXISTS [Users] (
    [PK] INTEGER PRIMARY KEY ASC,
    [UserName] TEXT NULL,
    [HashedPW] TEXT,
    [Salt] TEXT
);