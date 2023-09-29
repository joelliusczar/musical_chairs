GRANT SELECT ON TABLE `<dbName>`.`Albums` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`Artists` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`SongCovers` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`Songs` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`SongsArtists` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`StationsSongs` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`Stations` TO <radioUser>;

GRANT UPDATE ON TABLE `<dbName>`.`StationQueue` TO <radioUser>;
GRANT INSERT ON TABLE `<dbName>`.`StationQueue` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`StationQueue` TO <radioUser>;

GRANT UPDATE ON TABLE `<dbName>`.`UserActionHistory` TO <radioUser>;
GRANT INSERT ON TABLE `<dbName>`.`UserActionHistory` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`UserActionHistory` TO <radioUser>;