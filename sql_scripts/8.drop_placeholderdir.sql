USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 1 FROM information_schema.COLUMNS 
	WHERE table_name = 'songs' 
		AND column_name = 'isdirectoryplaceholder' 
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songs` DROP COLUMN `isdirectoryplaceholder`;
	END;
END IF|
DELIMITER ;