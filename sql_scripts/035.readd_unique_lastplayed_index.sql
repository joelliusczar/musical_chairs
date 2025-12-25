USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.STATISTICS
	WHERE table_name = 'lastplayed'
		AND index_name = 'idx_lastplayed2'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `lastplayed` ADD UNIQUE INDEX `idx_lastplayed2` (`stationfk`,`songfk`,`itemtype`,`parentkey`);
	END;
END IF|
DELIMITER ;