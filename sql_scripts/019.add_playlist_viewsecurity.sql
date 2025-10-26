USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'playlists'
		AND column_name = 'viewsecuritylevel'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `playlists`
		ADD COLUMN `viewsecuritylevel` INT(11) DEFAULT NULL;
	END;
END IF|
DELIMITER ;