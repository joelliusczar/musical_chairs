USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'songs'
		AND column_name = 'deletedtimestamp'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songs`
		ADD COLUMN `deletedtimestamp` DOUBLE NULL;
	END;
END IF|
DELIMITER ;