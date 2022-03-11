SELECT "security_def_1.sql";

CREATE TABLE IF NOT EXISTS [Users] (
	[PK] INTEGER PRIMARY KEY ASC,
	[UserName] TEXT NOT NULL,
	[HashedPW] BLOB,
	[Salt] BLOB,
	[Email] TEXT NULL,
	[IsActive] INTEGER
);