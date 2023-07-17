CREATE TABLE "Users" (
	pk INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	"displayName" VARCHAR, 
	"hashedPW" BLOB, 
	email VARCHAR, 
	"dirRoot" VARCHAR, 
	"isDisabled" INTEGER, 
	"creationTimestamp" FLOAT NOT NULL, 
	"viewSecurityLevel" INTEGER, 
	PRIMARY KEY (pk)
);
CREATE TABLE "Artists" (
	pk INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	"lastModifiedByUserFk" INTEGER NOT NULL, 
	"lastModifiedTimestamp" FLOAT NOT NULL, 
	"ownerFk" INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk), 
	FOREIGN KEY("ownerFk") REFERENCES "Users" (pk)
);
CREATE TABLE "Stations" (
	pk INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	"displayName" VARCHAR, 
	"procId" INTEGER, 
	"lastModifiedByUserFk" INTEGER, 
	"lastModifiedTimestamp" FLOAT, 
	"ownerFk" INTEGER NOT NULL, 
	"requestSecurityLevel" INTEGER, 
	"viewSecurityLevel" INTEGER, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk), 
	FOREIGN KEY("ownerFk") REFERENCES "Users" (pk)
);
CREATE TABLE "UserRoles" (
	"userFk" INTEGER NOT NULL, 
	role VARCHAR, 
	span FLOAT NOT NULL, 
	count FLOAT NOT NULL, 
	priority INTEGER, 
	"creationTimestamp" FLOAT NOT NULL, 
	FOREIGN KEY("userFk") REFERENCES "Users" (pk)
);
CREATE TABLE "UserActionHistory" (
	pk INTEGER NOT NULL, 
	"userFk" INTEGER, 
	action VARCHAR NOT NULL, 
	timestamp FLOAT, 
	"queuedTimestamp" FLOAT NOT NULL, 
	"requestedTimestamp" FLOAT, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("userFk") REFERENCES "Users" (pk)
);
CREATE TABLE "PathUserPermissions" (
	pk INTEGER NOT NULL, 
	"userFk" INTEGER NOT NULL, 
	path VARCHAR NOT NULL, 
	role VARCHAR, 
	span FLOAT NOT NULL, 
	count FLOAT NOT NULL, 
	priority INTEGER, 
	"creationTimestamp" FLOAT NOT NULL, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("userFk") REFERENCES "Users" (pk)
);
CREATE TABLE "FriendUserPermissions" (
	pk INTEGER NOT NULL, 
	"friendFk" INTEGER NOT NULL, 
	"userFk" INTEGER NOT NULL, 
	role VARCHAR, 
	span FLOAT NOT NULL, 
	count FLOAT NOT NULL, 
	priority INTEGER, 
	"creationTimestamp" FLOAT NOT NULL, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("friendFk") REFERENCES "Users" (pk), 
	FOREIGN KEY("userFk") REFERENCES "Users" (pk)
);
CREATE TABLE "Albums" (
	pk INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	"albumArtistFk" INTEGER, 
	year INTEGER, 
	"lastModifiedByUserFk" INTEGER NOT NULL, 
	"lastModifiedTimestamp" FLOAT NOT NULL, 
	"ownerFk" INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("albumArtistFk") REFERENCES "Artists" (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk), 
	FOREIGN KEY("ownerFk") REFERENCES "Users" (pk)
);
CREATE TABLE "StationUserPermissions" (
	pk INTEGER NOT NULL, 
	"stationFk" INTEGER NOT NULL, 
	"userFk" INTEGER NOT NULL, 
	role VARCHAR, 
	span FLOAT NOT NULL, 
	count FLOAT NOT NULL, 
	priority INTEGER, 
	"creationTimestamp" FLOAT NOT NULL, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("stationFk") REFERENCES "Stations" (pk), 
	FOREIGN KEY("userFk") REFERENCES "Users" (pk)
);
CREATE TABLE "Songs" (
	pk INTEGER NOT NULL, 
	path VARCHAR NOT NULL, 
	name VARCHAR, 
	"albumFk" INTEGER, 
	track INTEGER, 
	disc INTEGER, 
	genre VARCHAR, 
	explicit INTEGER, 
	bitrate FLOAT, 
	comment VARCHAR, 
	lyrics VARCHAR, 
	duration FLOAT, 
	"sampleRate" FLOAT, 
	"isDirectoryPlaceholder" INTEGER, 
	"lastModifiedByUserFk" INTEGER, 
	"lastModifiedTimestamp" FLOAT, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("albumFk") REFERENCES "Albums" (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk)
);
CREATE TABLE "SongsArtists" (
	pk INTEGER NOT NULL, 
	"songFk" INTEGER NOT NULL, 
	"artistFk" INTEGER NOT NULL, 
	"isPrimaryArtist" INTEGER, 
	comment VARCHAR, 
	"lastModifiedByUserFk" INTEGER, 
	"lastModifiedTimestamp" FLOAT, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("songFk") REFERENCES "Songs" (pk), 
	FOREIGN KEY("artistFk") REFERENCES "Artists" (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk)
);
CREATE TABLE "SongCovers" (
	pk INTEGER NOT NULL, 
	"songFk" INTEGER NOT NULL, 
	"coverSongFk" INTEGER NOT NULL, 
	"lastModifiedByUserFk" INTEGER, 
	"lastModifiedTimestamp" FLOAT, 
	PRIMARY KEY (pk), 
	FOREIGN KEY("songFk") REFERENCES "Songs" (pk), 
	FOREIGN KEY("coverSongFk") REFERENCES "Songs" (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk)
);
CREATE TABLE "StationsSongs" (
	"songFk" INTEGER NOT NULL, 
	"stationFk" INTEGER NOT NULL, 
	"lastModifiedByUserFk" INTEGER, 
	"lastModifiedTimestamp" FLOAT, 
	FOREIGN KEY("songFk") REFERENCES "Songs" (pk), 
	FOREIGN KEY("stationFk") REFERENCES "Stations" (pk), 
	FOREIGN KEY("lastModifiedByUserFk") REFERENCES "Users" (pk)
);
CREATE TABLE "StationQueue" (
	"userActionHistoryFk" INTEGER NOT NULL, 
	"stationFk" INTEGER NOT NULL, 
	"songFk" INTEGER, 
	FOREIGN KEY("userActionHistoryFk") REFERENCES "UserActionHistory" (pk), 
	FOREIGN KEY("stationFk") REFERENCES "Stations" (pk), 
	FOREIGN KEY("songFk") REFERENCES "Songs" (pk)
);

CREATE UNIQUE INDEX "idx_uniqueUsername" ON "Users" (username);
CREATE UNIQUE INDEX "idx_uniqueEmail" ON "Users" (email);
CREATE UNIQUE INDEX "idx_dirRoot" ON "Users" ("dirRoot");
CREATE UNIQUE INDEX "idx_uniqueArtistsName" ON "Artists" (name, "ownerFk");
CREATE UNIQUE INDEX "idx_uniqueStationName" ON "Stations" (name, "ownerFk");
CREATE UNIQUE INDEX "idx_userRoles" ON "UserRoles" ("userFk", role);
CREATE UNIQUE INDEX "idx_pathPermissions" ON "PathUserPermissions" ("userFk", path, role);
CREATE UNIQUE INDEX "idx_friendPermissions" ON "FriendUserPermissions" ("friendFk", "userFk", role);
CREATE UNIQUE INDEX "idx_uniqueAlbumNameForArtist" ON "Albums" (name, "albumArtistFk", "ownerFk");
CREATE UNIQUE INDEX "idx_stationPermissions" ON "StationUserPermissions" ("stationFk", "userFk", role);
CREATE UNIQUE INDEX "idx_uniqueSongPath" ON "Songs" (path);
CREATE UNIQUE INDEX "idx_songsArtists" ON "SongsArtists" ("songFk", "artistFk");
CREATE UNIQUE INDEX "idx_songCovers" ON "SongCovers" ("songFk", "coverSongFk");
CREATE UNIQUE INDEX "idx_stationsSongs" ON "StationsSongs" ("songFk", "stationFk");

BEGIN;
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (1, 'alpha_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (2, 'bravo_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (3, 'charlie_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (4, 'delta_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (5, 'echo_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (6, 'foxtrot_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (7, 'golf_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (8, 'hotel_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (9, 'india_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (10, 'juliet_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (11, 'kilo_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (12, 'lima_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (13, 'november_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (14, 'oscar_artist', 11, 0.0, 11);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (15, 'papa_artist', 11, 0.0, 14);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (16, 'romeo_artist', 11, 0.0, 9);
INSERT INTO "Artists" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (17, 'sierra_artist', 11, 0.0, 8);
COMMIT;
BEGIN;
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (1, 'broo_album', 7, 2001, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (2, 'moo_album', 7, 2003, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (8, 'shoo_album', 6, 2003, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (9, 'who_2_album', 6, 2001, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (10, 'who_1_album', 5, 2001, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (11, 'boo_album', 4, 2001, 11, 0.0, 11);
COMMIT;
BEGIN;
INSERT INTO "Albums" (pk, name, year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (4, 'soo_album', 2004, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (7, 'koo_album', 2010, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, year, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (13, 'koo_album', 2010, 11, 0.0, 11);
COMMIT;
BEGIN;
INSERT INTO "Albums" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (5, 'doo_album', 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (6, 'roo_album', 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (12, 'garoo_album', 11, 0.0, 11);
COMMIT;
BEGIN;
INSERT INTO "Albums" (pk, name, "albumArtistFk", "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (3, 'juliet_album', 7, 11, 0.0, 11);
INSERT INTO "Albums" (pk, name, "albumArtistFk", "lastModifiedByUserFk", "lastModifiedTimestamp", "ownerFk") VALUES (14, 'grunt_album', 7, 11, 0.0, 10);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, explicit, bitrate, comment) VALUES (1, 'foo/goo/boo/sierra', 'sierra_song', 11, 1, 1, 'pop', 0, 144.0, 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, explicit, bitrate, comment) VALUES (2, 'foo/goo/boo/tango', 'tango_song', 11, 2, 1, 'pop', 0, 144.0, 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, explicit, bitrate, comment) VALUES (3, 'foo/goo/boo/uniform', 'uniform_song', 11, 3, 1, 'pop', 1, 144.0, 'Kazoos make good parrallel parkers');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, bitrate, comment) VALUES (4, 'foo/goo/boo/victor', 'victor_song', 11, 4, 1, 'pop', 144.0, 'Kazoos make bad swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, bitrate, comment) VALUES (5, 'foo/goo/boo/victor_2', 'victor_song', 11, 5, 1, 'pop', 144.0, 'Kazoos make good hood rats');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (6, 'foo/goo/who_1/whiskey', 'whiskey_song', 10, 1, 1, 'pop', 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (7, 'foo/goo/who_1/xray', 'xray_song', 10, 2, 1, 'pop', 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (8, 'foo/goo/who_1/yankee', 'yankee_song', 10, 3, 1, 'pop', 'guitars make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (9, 'foo/goo/who_1/zulu', 'zulu_song', 10, 4, 1, 'pop', 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (10, 'foo/goo/who_1/alpha', 'alpha_song', 10, 5, 1, 'pop', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (11, 'foo/goo/who_2/bravo', 'bravo_song', 9, 1, 2, 'pop', 'hamburgers make flat swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (12, 'foo/goo/who_2/charlie', 'charlie_song', 9, 2, 2, 'pop', 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (13, 'foo/goo/who_2/delta', 'delta_song', 9, 3, 2, 'pop', 'Kazoos make good swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (59, 'foo/goo/looga/alpha', 'looga_alpha_song', 14, 5, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (62, 'tossedSlash/guess/gold/jar', 'jar_song', 14, 5, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (63, 'tossedSlash/guess/gold/bar', 'bar_song', 14, 6, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (64, 'tossedSlash/guess/gold/run', 'run_song', 14, 7, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (65, 'tossedSlash/band/bun', 'bun_song', 14, 8, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (66, 'tossedSlash/band/hun', 'hun_song', 14, 8, 1, 'bam', 'hotdogs make good lava swimmers');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre, comment) VALUES (67, 'tossedSlash/guess/silver/run', 'run_song', 14, 7, 1, 'bam', 'hotdogs make good lava swimmers');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre) VALUES (14, 'foo/goo/who_2/foxtrot', 'foxtrot_song', 9, 4, 2, 'pop');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre) VALUES (15, 'foo/goo/who_2/golf', 'golf_song', 9, 5, 2, 'pop');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre) VALUES (68, 'tossedSlash/guess/silver/plastic', 'plastic_tune', 12, 8, 1, 'bam');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre) VALUES (69, 'tossedSlash/guess/silver/salt', 'salt_tune', 12, 8, 1, 'bam');
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc, genre) VALUES (70, 'tossedSlash/guess/silver/green', 'green_tune', 12, 8, 1, 'bam');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc) VALUES (16, 'foo/goo/shoo/hotel', 'hotel_song', 8, 1, 1);
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc) VALUES (17, 'foo/goo/shoo/india', 'india_song', 8, 2, 1);
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc) VALUES (18, 'foo/goo/shoo/juliet', 'juliet_song', 8, 3, 1);
INSERT INTO "Songs" (pk, path, name, "albumFk", track, disc) VALUES (19, 'foo/goo/shoo/kilo', 'kilo_song', 8, 4, 1);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (20, 'foo/goo/koo/lima', 'lima_song', 7, 1);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (21, 'foo/goo/koo/mike', 'mike_song', 7, 2);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (22, 'foo/goo/koo/november', 'november_song', 7, 3);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (37, 'foo/goo/moo/delta2', 'delta2_song', 2, 1);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (38, 'foo/goo/moo/echo2', 'echo2_song', 2, 2);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (39, 'foo/goo/moo/foxtrot2', 'foxtrot2_song', 2, 3);
INSERT INTO "Songs" (pk, path, name, "albumFk", track) VALUES (40, 'foo/goo/moo/golf2', 'golf2_song', 2, 4);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (23, 'foo/goo/roo/oscar', 'oscar_song', 6);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (24, 'foo/goo/roo/papa', 'papa_song', 6);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (25, 'foo/goo/roo/romeo', 'romeo_song', 6);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (26, 'foo/goo/roo/sierra2', 'sierra2_song', 6);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (29, 'foo/goo/roo/victor2', 'victor2_song', 4);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (41, 'foo/goo/broo/hotel2', 'hotel2_song', 1);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (42, 'foo/goo/broo/india2', 'india2_song', 1);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (43, 'foo/goo/broo/juliet2', 'juliet2_song', 1);
INSERT INTO "Songs" (pk, path, name, "albumFk") VALUES (58, 'jazz/lurk/toot/alpha4_song', 'alpha4_song', 7);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name) VALUES (27, 'foo/goo/roo/tango2', 'tango2_song');
INSERT INTO "Songs" (pk, path, name) VALUES (28, 'foo/goo/roo/uniform2', 'uniform2_song');
INSERT INTO "Songs" (pk, path, name) VALUES (30, 'foo/goo/roo/whiskey2', 'whiskey2_song');
INSERT INTO "Songs" (pk, path, name) VALUES (31, 'foo/goo/roo/xray2', 'xray2_song');
INSERT INTO "Songs" (pk, path, name) VALUES (50, 'foo/bar/baz/romeo2', '目黒将司');
INSERT INTO "Songs" (pk, path, name) VALUES (51, 'foo/bar/baz/sierra3', 'Aoife Ní Fhearraigh');
INSERT INTO "Songs" (pk, path, name) VALUES (52, 'jazz/rude/rog/tango3', 'tango3');
INSERT INTO "Songs" (pk, path, name) VALUES (53, 'jazz/rude/rog/uniform3', 'uniform3');
INSERT INTO "Songs" (pk, path, name) VALUES (54, 'jazz/cat/kitten/victor3', 'victor3');
INSERT INTO "Songs" (pk, path, name) VALUES (55, 'blitz/mar/wall/whiskey3', 'whiskey3');
INSERT INTO "Songs" (pk, path, name) VALUES (56, 'blitz/mar/wall/xray3', 'xray3');
INSERT INTO "Songs" (pk, path, name) VALUES (57, 'blitz/rhino/rhina/zulu3', 'zulu3');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", genre, explicit, bitrate) VALUES (32, 'foo/goo/doo/yankee2', 'yankee2_song', 5, 'bop', 0, 121.0);
INSERT INTO "Songs" (pk, path, name, "albumFk", genre, explicit, bitrate) VALUES (33, 'foo/goo/doo/zulu2', 'zulu2_song', 5, 'bop', 1, 121.0);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, explicit, bitrate) VALUES (34, 'foo/goo/soo/alpha2', 'alpha2_song', 4, 1, 1, 121.0);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, explicit) VALUES (35, 'foo/goo/soo/bravo2', 'bravo2_song', 4, 2, 1);
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path, name, "albumFk", track, comment) VALUES (36, 'foo/goo/soo/charlie2', 'charlie2_song', 4, 3, 'Boot ''n'' scoot');
COMMIT;
BEGIN;
INSERT INTO "Songs" (pk, path) VALUES (44, 'foo/rude/bog/kilo2');
INSERT INTO "Songs" (pk, path) VALUES (45, 'foo/rude/bog/lima2');
INSERT INTO "Songs" (pk, path) VALUES (46, 'foo/rude/rog/mike2');
INSERT INTO "Songs" (pk, path) VALUES (47, 'foo/rude/rog/november2');
INSERT INTO "Songs" (pk, path) VALUES (48, 'foo/rude/rog/oscar2');
INSERT INTO "Songs" (pk, path) VALUES (49, 'foo/dude/dog/papa2');
COMMIT;
BEGIN;
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (1, 40, 7);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (2, 39, 7);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (3, 38, 7);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (4, 37, 7);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (5, 36, 2);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (6, 35, 1);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (7, 34, 3);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (8, 33, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (9, 32, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (10, 31, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (11, 30, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (12, 29, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (13, 28, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (14, 27, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (15, 26, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (16, 25, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (17, 24, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (18, 23, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (19, 22, 2);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (20, 21, 2);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (21, 20, 2);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (22, 19, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (23, 18, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (24, 17, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (25, 16, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (26, 15, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (27, 14, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (28, 13, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (29, 12, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (30, 11, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (31, 10, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (32, 9, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (33, 8, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (34, 7, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (35, 6, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (36, 5, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (37, 4, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (38, 3, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (39, 2, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (40, 1, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (45, 21, 4);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (46, 21, 6);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (47, 17, 10);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (48, 17, 5);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (49, 17, 2);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (50, 17, 11);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (51, 35, 12);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (52, 59, 16);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk") VALUES (54, 59, 17);
COMMIT;
BEGIN;
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk", "isPrimaryArtist") VALUES (41, 43, 7, 1);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk", "isPrimaryArtist") VALUES (42, 42, 7, 1);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk", "isPrimaryArtist") VALUES (43, 41, 7, 1);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk", "isPrimaryArtist") VALUES (44, 1, 6, 1);
INSERT INTO "SongsArtists" (pk, "songFk", "artistFk", "isPrimaryArtist") VALUES (53, 59, 15, 1);
COMMIT;
BEGIN;
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (43, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (43, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (43, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (41, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (40, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (38, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (37, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (36, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (35, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (34, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (33, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (32, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (31, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (30, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (29, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (28, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (27, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (26, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (25, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (24, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (23, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (22, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (21, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (20, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (19, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (18, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (17, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (17, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (16, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (15, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (15, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (14, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (13, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (12, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (11, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (10, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (9, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (8, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (7, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (6, 3);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (5, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (4, 4);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (3, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (2, 1);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (1, 2);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (1, 6);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (4, 6);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (50, 6);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (44, 8);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (45, 8);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (46, 8);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (47, 8);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (59, 10);
INSERT INTO "StationsSongs" ("songFk", "stationFk") VALUES (59, 11);
COMMIT;
BEGIN;
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (1, 'oscar_station', 'Oscar the grouch', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (2, 'papa_station', 'Come to papa', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (3, 'romeo_station', 'But soft, what yonder wind breaks', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (4, 'sierra_station', 'The greatest lie the devil ever told', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (5, 'tango_station', 'Nuke the whales', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (6, 'yankee_station', 'Blurg the blergos', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (7, 'uniform_station', 'Asshole at the wheel', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (8, 'victor_station', 'Fat, drunk, and stupid', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (9, 'whiskey_station', 'Chris-cross apple sauce', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (10, 'xray_station', 'Pentagular', 2, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (11, 'zulu_station', 'Hammer time', 10, NULL);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (12, 'alpha_station_rerun', 'We rerun again and again', 22, 19);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (13, 'bravo_station_rerun', 'We rerun again and again', 22, 9);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (14, 'charlie_station_rerun', 'The Wide World of Sports', 22, 39);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (15, 'delta_station_rerun', 'Dookie Dan strikes again', 25, 49);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (16, 'foxtrot_station_rerun', 'fucked six ways to Sunday', 25, 59);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (17, 'golf_station_rerun', 'goliath bam bam', 37, 39);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (18, 'hotel_station_rerun', 'hella cool radio station', 37, 39);
INSERT INTO "Stations" (pk, name, "displayName", "ownerFk", "viewSecurityLevel") VALUES (19, 'india_station_rerun', 'bitchingly fast!', 45, 39);
COMMIT;
BEGIN;
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (1, 'testUser_alpha', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test@test.com', '', 0, 1622142780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (2, 'testUser_bravo', 'Bravo Test User', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test2@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (3, 'testUser_charlie', 'charlie the user of tests', NULL, 'test3@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (4, 'testUser_delta', 'DELTA USER', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test4@test.com', NULL, 1, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (5, 'testUser_echo', 'ECHO, ECHO', NULL, NULL, NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (6, 'testUser_foxtrot', 'ﬀ ozotroz', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test6@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (7, 'testUser_golf', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test7@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (8, 'testUser_hotel', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test8@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (9, 'testUser_india', 'IndiaDisplay', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test9@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (10, 'testUser_juliet', 'julietDisplay', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test10@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (11, 'testUser_kilo', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test11@test.com', '/foo', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (12, 'testUser_lima', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test12@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (13, 'testUser_mike', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test13@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (14, 'testUser_november', 'ñovoper', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test14@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (15, 'testUser_oscar', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test15@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (16, 'testUser_papa', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test16@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (17, 'testUser_quebec', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test17@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (18, 'testUser_romeo', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test18@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (19, 'testUser_sierra', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test19@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (20, 'testUser_tango', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test20@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (21, 'testUser_uniform', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test21@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (22, 'testUser_victor', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test22@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (23, 'testUser_whiskey', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test23@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (24, 'testUser_xray', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test24@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (25, 'testUser_yankee', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test25@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (26, 'testUser_zulu', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test26@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (27, 'testUser_alice', 'Alice is my name', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test27@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (28, 'bertrand', 'Bertrance', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test28@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (29, 'carl', 'Carl the Cactus', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test29@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (30, 'dan', 'Dookie Dan', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test30@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (31, 'felix', 'Felix the man', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test31@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (32, 'foxman', NULL, x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test32@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (33, 'foxtrain', 'Foxtrain chu', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test33@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (34, 'george', 'George Costanza', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test35@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (35, 'hamburger', 'HamBurger', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test36@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (36, 'horsetel', 'horsetelophone', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test37@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (37, 'ingo', 'Ingo      is a bad man', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test38@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (38, 'ned_land', 'Ned Land of the Spear', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test39@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (39, 'narlon', 'Narloni', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test40@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (40, '7', 'seven', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test41@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (41, 'testUser_oomdwell', 'Oomdwellmit', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test42@test.com', NULL, 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (42, 'paulBear_testUser', 'Paul Bear', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test43@test.com', 'paulBear_testUser', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (43, 'quirkyAdmon_testUser', 'Quirky Admin', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test44@test.com', 'quirkyAdmon_testUser', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (44, 'radicalPath_testUser', 'Radical Path', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test45@test.com', 'radicalPath_testUser', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (45, 'stationSaver_testUser', 'Station Saver', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test46@test.com', 'stationSaver_testUser', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (46, 'superPath_testUser', 'Super Pathouser', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test47@test.com', 'superPath_testUser', 0, 1653678780.0);
INSERT INTO "Users" (pk, username, "displayName", "hashedPW", email, "dirRoot", "isDisabled", "creationTimestamp") VALUES (47, 'tossedSlash_testUser', 'Tossed Slash', x'24326224313224577734337450627639635046794b36736b327a4136756e76345a4259497971375731587a377a743638624864344f735a354e4f7279', 'test48@test.com', 'tossedSlash', 0, 1653678780.0);
COMMIT;
BEGIN;
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (1, 'admin', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (2, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (3, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (4, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (4, 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (6, 'station:request', 15.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (6, 'path:edit', 120.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (6, 'path:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (7, 'user:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (10, 'station:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (17, 'station:request', 300.0, 15.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (2, 'station:create', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (20, 'station:create', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (9, 'path:edit', 0.0, 0.0, 21, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (9, 'path:view', 0.0, 0.0, 21, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (9, 'station:assign', 0.0, 0.0, 21, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (8, 'path:view', 0.0, 0.0, 21, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (8, 'path:edit', 0.0, 0.0, 21, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (23, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (14, 'station:request', 300.0, 10.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (12, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (13, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (15, 'station:request', 120.0, 5.0, 41, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (16, 'station:request', 300.0, 20.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (27, 'station:request', 300.0, 20.0, 18, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (42, 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (43, 'admin', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (44, 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "UserRoles" ("userFk", role, span, count, priority, "creationTimestamp") VALUES (46, 'path:edit', 0.0, 0.0, 60, 1622142780.0);
COMMIT;
BEGIN;
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (1, 3, 11, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (4, 3, 13, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (6, 3, 14, 'station:request', 300.0, 5.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (8, 3, 15, 'station:request', 60.0, 5.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (10, 3, 16, 'station:request', 300.0, 25.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (12, 3, 17, 'station:request', 300.0, 25.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (13, 9, 10, 'station:assign', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (14, 5, 10, 'station:assign', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (15, 9, 10, 'station:request', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (16, 9, 8, 'station:assign', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (17, 14, 24, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (18, 14, 26, 'station:assign', 0.0, 0.0, 35, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (19, 17, 39, 'station:assign', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (20, 17, 39, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (21, 17, 39, 'station:request', 5.0, 300.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (22, 18, 39, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (23, 18, 39, 'station:request', 100.0, 300.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (24, 17, 36, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (25, 17, 34, 'station:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (26, 17, 34, 'station:request', 70.0, 10.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (27, 17, 34, 'station:flip', 70.0, 10.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (28, 17, 29, 'station:flip', 70.0, 10.0, NULL, 1622142780.0);
INSERT INTO "StationUserPermissions" (pk, "stationFk", "userFk", role, span, count, priority, "creationTimestamp") VALUES (29, 11, 41, 'station:userassign', 0.0, 0.0, NULL, 1622142780.0);
COMMIT;
BEGIN;
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (1, 12, 'foo/goo/boo', 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (2, 11, 'foo/goo/shoo', 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (3, 11, 'foo/goo/moo', 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (4, 11, 'foo/goo/shoo', 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (5, 11, 'foo/goo/shoo', 'path:download', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (6, 12, 'foo/goo/boo', 'path:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (7, 13, '/foo/goo', 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (8, 13, '/foo/goo', 'path:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (9, 19, '/foo/goo', 'path:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (10, 19, '/foo/goo/who_1', 'path:view', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (11, 19, '/foo/goo', 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (12, 19, '/foo/goo/who_1', 'path:edit', 1.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (13, 6, '/foo/goo/boo', 'path:edit', 1.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (14, 21, '/foo/d', 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (15, 21, '/foo/b', 'path:list', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (16, 45, '/foo/b', 'path:edit', 0.0, 0.0, NULL, 1622142780.0);
INSERT INTO "PathUserPermissions" (pk, "userFk", path, role, span, count, priority, "creationTimestamp") VALUES (17, 45, '/foo/b', 'path:view', 0.0, 0.0, NULL, 1622142780.0);
COMMIT;
BEGIN;
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (1, 10, 'station:request', 1622142780.0, 1622142780.0, 1622142780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (2, 10, 'station:request', 1622143780.0, 1622143780.0, 1622143780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (3, 10, 'station:request', 1622144780.0, 1622144780.0, 1622144780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (4, 10, 'station:create', 1622145780.0, 1622145780.0, 1622145780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (5, 10, 'station:assign', 1622146780.0, 1622146780.0, 1622146780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (6, 10, 'station:assign', 1622147780.0, 1622147780.0, 1622147780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (7, 10, 'station:assign', 1622148780.0, 1622148780.0, 1622148780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (8, 10, 'station:flip', 1622149780.0, 1622149780.0, 1622149780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (9, 10, 'station:flip', 1622150780.0, 1622150780.0, 1622150780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (10, 10, 'station:flip', 1622151780.0, 1622151780.0, 1622151780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (11, 10, 'station:request', 1622152780.0, 1622152780.0, 1622152780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (12, 10, 'station:request', 1622153780.0, 1622153780.0, 1622153780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (13, 10, 'station:request', 1622154780.0, 1622154780.0, 1622154780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (14, 10, 'station:request', 1622155780.0, 1622155780.0, 1622155780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (15, 10, 'station:request', 1622156780.0, 1622156780.0, 1622156780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (16, 10, 'station:request', 1622157780.0, 1622157780.0, 1622157780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (17, 10, 'station:create', 1622158780.0, 1622158780.0, 1622158780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (18, 10, 'station:request', 1622160780.0, 1622160780.0, 1622160780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (19, 10, 'station:request', 1622161780.0, 1622161780.0, 1622161780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (20, 10, 'station:request', 1622162780.0, 1622162780.0, 1622162780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (21, 10, 'station:request', 1622163780.0, 1622163780.0, 1622163780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (22, 10, 'station:request', 1622164780.0, 1622164780.0, 1622164780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (23, 10, 'station:request', 1622165780.0, 1622165780.0, 1622165780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (24, 10, 'station:request', 1622166780.0, 1622166780.0, 1622166780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (25, 10, 'station:edit', 1622167780.0, 1622167780.0, 1622167780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (26, 10, 'station:flip', 1622168780.0, 1622168780.0, 1622168780.0);
INSERT INTO "UserActionHistory" (pk, "userFk", action, timestamp, "queuedTimestamp", "requestedTimestamp") VALUES (27, 10, 'station:flip', 1622169780.0, 1622169780.0, 1622169780.0);
COMMIT;
BEGIN;
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (1, 2, 3);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (2, 2, 4);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (3, 2, 5);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (8, 5, NULL);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (9, 5, NULL);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (10, 5, NULL);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (11, 5, 5);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (12, 5, 6);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (13, 5, 7);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (14, 5, 8);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (15, 5, 9);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (16, 5, 10);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (18, 6, 10);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (19, 6, 11);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (20, 6, 12);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (21, 6, 13);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (22, 6, 14);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (23, 6, 15);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (24, 6, 16);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (25, 6, NULL);
INSERT INTO "StationQueue" ("userActionHistoryFk", "stationFk", "songFk") VALUES (26, 6, NULL);
COMMIT;
