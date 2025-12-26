USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) > 0 FROM information_schema.STATISTICS
	WHERE table_name = 'lastplayed'
		AND index_name = 'idx_lastplayed'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `lastplayed` DROP INDEX `idx_lastplayed`;
	END;
END IF|
DELIMITER ;