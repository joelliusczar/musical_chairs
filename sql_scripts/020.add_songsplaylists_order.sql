USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'songsplaylists'
		AND column_name = 'order'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songsplaylists`
		ADD COLUMN `order` DOUBLE DEFAULT 0;
	END;
END IF|
DELIMITER ;