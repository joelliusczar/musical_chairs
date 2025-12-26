USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'lastplayed'
		AND column_name = 'parentkey'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `lastplayed`
		ADD COLUMN `parentkey` int(11) NULL;
	END;
END IF|
DELIMITER ;