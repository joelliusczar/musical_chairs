
CREATE OR REPLACE TEMPORARY TABLE `historyids` (
	`pk` int(11), KEY `pk`(`pk`) USING HASH
) ENGINE=MEMORY
SELECT Q.`pk` FROM `stationlogs` Q
WHERE Q.`action` = %(action)s
AND Q.`timestamp` < %(timestamp)s
AND Q.`stationfk` = %(stationid)s;


DELETE FROM `stationlogs` WHERE `pk` IN (SELECT `pk` FROM `historyids`);
