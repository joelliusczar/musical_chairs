INSERT INTO [Artists] SELECT * FROM [ArtistsOld];
INSERT INTO [Tags] SELECT * FROM [TagsOld];
INSERT INTO [Stations] SELECT * FROM [StationsOld];
INSERT INTO [StationsTags] SELECT * FROM [StationsTagsOld];
INSERT INTO [Albums] SELECT * FROM [AlbumsOld];
INSERT INTO [Songs] SELECT * FROM [SongsOld];
INSERT INTO [SongsArtists] SELECT * FROM [SongsArtistsOld];
INSERT INTO [SongCovers] SELECT * FROM [SongCoversOld];
INSERT INTO [SongsTags] SELECT * FROM [SongsTagsOld];
INSERT INTO [StationHistory] SELECT * FROM [StationHistoryOld];
INSERT INTO [StationQueue] SELECT * FROM [StationQueueOld];
INSERT INTO [Users] SELECT * FROM [UsersOld];
INSERT INTO [UserRoles] SELECT * FROM [UserRolesOld];

DROP TABLE [ArtistsOld];
DROP TABLE [TagsOld];
DROP TABLE [StationsOld];
DROP TABLE [StationsTagsOld];
DROP TABLE [AlbumsOld];
DROP TABLE [SongsOld];
DROP TABLE [SongsArtistsOld];
DROP TABLE [SongCoversOld];
DROP TABLE [SongsTagsOld];
DROP TABLE [StationHistoryOld];
DROP TABLE [StationQueueOld];
DROP TABLE [UsersOld];
DROP TABLE [UserRolesOld];



