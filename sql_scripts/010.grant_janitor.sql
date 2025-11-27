GRANT INSERT ON TABLE `<dbName>`.`pathuserpermissions` TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`songs` TO <janitorUser>;
GRANT INSERT ON TABLE `<dbName>`.`songs` TO <janitorUser>;
GRANT UPDATE ON TABLE `<dbName>`.`songs` TO <janitorUser>;
GRANT DELETE ON TABLE `<dbName>`.`songs` TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`albums` TO <janitorUser>;
GRANT SELECT ON TABLE `<dbName>`.`artists` TO <janitorUser>;
GRANT SELECT ON TABLE `<dbName>`.`songsartists` TO <janitorUser>;
GRANT SELECT ON TABLE `<dbName>`.`stations` TO <janitorUser>;
GRANT SELECT ON TABLE `<dbName>`.`users` TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`lastplayed` TO <janitorUser>;
GRANT INSERT ON TABLE `<dbName>`.`lastplayed` TO <janitorUser>;
GRANT UPDATE ON TABLE `<dbName>`.`lastplayed` TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`stationqueue` TO <janitorUser>;
GRANT DELETE ON TABLE `<dbName>`.`stationqueue` TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`useractionhistory` TO <janitorUser>;
GRANT DELETE ON TABLE `<dbName>`.`useractionhistory` TO <janitorUser>;

GRANT CREATE TEMPORARY TABLES ON `<dbName>`.* TO <janitorUser>;

GRANT SELECT ON TABLE `<dbName>`.`jobs` TO <janitorUser>;
GRANT DELETE ON TABLE `<dbName>`.`jobs` TO <janitorUser>;
GRANT UPDATE ON TABLE `<dbName>`.`jobs` TO <janitorUser>;


