USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'stationqueue'
		AND column_name = 'itemtype'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `stationqueue`
		ADD COLUMN `itemtype` CHAR(50) NOT NULL DEFAULT 'song';
	END;
END IF|
DELIMITER ;