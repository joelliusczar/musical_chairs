--formerly 020.add_songsplaylists_order
USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'playlistssongs'
		AND column_name = 'order'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `playlistssongs`
		ADD COLUMN `order` DOUBLE DEFAULT 0 NOT NULL;
	END;
END IF|
DELIMITER ;