USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'stations'
		AND column_name = 'playnum'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `stations`
		ADD COLUMN `playnum` INT(11) NOT NULL DEFAULT 1;
	END;
END IF|
DELIMITER ;