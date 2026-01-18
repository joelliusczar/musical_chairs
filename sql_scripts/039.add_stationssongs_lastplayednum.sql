USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'stationssongs'
		AND column_name = 'lastplayednum'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `stationssongs`
		ADD COLUMN `lastplayednum` INT(11) NOT NULL DEFAULT 0;
	END;
END IF|
DELIMITER ;