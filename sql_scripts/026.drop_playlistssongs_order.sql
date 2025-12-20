USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 1 FROM information_schema.COLUMNS
	WHERE table_name = 'playlistssongs'
		AND column_name = 'order'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `playlistssongs` DROP COLUMN `order`;
	END;
END IF|
DELIMITER ;