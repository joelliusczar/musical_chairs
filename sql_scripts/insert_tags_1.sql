
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('vg');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('thinking');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('steampunk');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('dark');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('sad');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('movies');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('soundtrack');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('pop');
INSERT OR IGNORE INTO [Tags] ([Name]) VALUES('trippy');

INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('all', 'All'); 
INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('vg', 'Video Game Soundtracks'); 
INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('thinking', 'Thinking'); 
INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('trip', 'Tripping'); 
INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('pop', 'Pop'); 
INSERT OR IGNORE INTO [Stations] ([Name], [DisplayName]) 
VALUES('movies', 'Movie Soundtracks');

SELECT [PK] FROM [Stations] WHERE Name = 'all';


INSERT OR IGNORE INTO [StationsTags]
SELECT ST.[PK], T.[PK]
FROM [Stations] ST, [Tags] T
WHERE ST.[Name] = 'all';

INSERT OR IGNORE INTO [StationsTags]
SELECT ST.[PK], T.[PK]
FROM [Stations] ST, [Tags] T
WHERE ST.[Name] = 'vg' AND T.[Name] = 'vg';

INSERT OR IGNORE INTO [StationsTags]
SELECT ST.[PK], T.[PK]
FROM [Stations] ST, [Tags] T
WHERE ST.[Name] = 'movies' AND T.[Name] = 'movies';

INSERT OR IGNORE INTO [StationsTags]
SELECT ST.[PK], T.[PK]
FROM [Stations] ST, [Tags] T
WHERE ST.[Name] = 'pop' AND T.[Name] = 'pop';