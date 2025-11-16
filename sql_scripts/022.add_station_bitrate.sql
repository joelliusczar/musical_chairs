USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'stations'
		AND column_name = 'bitratekps'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `stations`
		ADD COLUMN `bitratekps` INT(11) NULL;
	END;
END IF|
DELIMITER ;