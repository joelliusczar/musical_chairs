GRANT SELECT ON TABLE `<dbName>`.`albums` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`artists` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`songcovers` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`songs` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`songsartists` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`stationssongs` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`users` TO <radioUser>;

GRANT SELECT ON TABLE `<dbName>`.`stations` TO <radioUser>;
GRANT UPDATE ON TABLE `<dbName>`.`stations` TO <radioUser>;

GRANT UPDATE ON TABLE `<dbName>`.`stationqueue` TO <radioUser>;
GRANT INSERT ON TABLE `<dbName>`.`stationqueue` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`stationqueue` TO <radioUser>;

GRANT UPDATE ON TABLE `<dbName>`.`useractionhistory` TO <radioUser>;
GRANT INSERT ON TABLE `<dbName>`.`useractionhistory` TO <radioUser>;
GRANT SELECT ON TABLE `<dbName>`.`useractionhistory` TO <radioUser>;