
CREATE OR REPLACE TEMPORARY TABLE `historyids` (
	`pk` int(11), KEY `pk`(`pk`) USING HASH
) ENGINE=MEMORY
SELECT H.`pk` FROM `useractionhistory` H
JOIN `stationqueue` Q ON Q.`useractionhistoryfk` = H.`pk`
WHERE H.`action` = %(action)s
AND H.`timestamp` < %(timestamp)s
AND Q.`stationfk` = %(stationid)s;


DELETE FROM `stationqueue` WHERE `useractionhistoryfk` IN (SELECT `pk` FROM `historyids`);

DELETE FROM `useractionhistory`
WHERE `pk` IN (SELECT `pk` FROM `historyids`);