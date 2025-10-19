USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'songs'
		AND column_name = 'tracknum'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songs`
		ADD COLUMN `tracknum` DOUBLE DEFAULT 0;
	END;	
END IF|
DELIMITER ;