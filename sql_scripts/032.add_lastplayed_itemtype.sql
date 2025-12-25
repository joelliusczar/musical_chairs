USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'lastplayed'
		AND column_name = 'itemtype'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `lastplayed`
		ADD COLUMN `itemtype` CHAR(50) NOT NULL DEFAULT 'song';
	END;
END IF|
DELIMITER ;