USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'stations'
		AND column_name = 'typeid'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `stations`
		ADD COLUMN `typeid` INT(11) DEFAULT 0;
	END;
END IF|
DELIMITER ;