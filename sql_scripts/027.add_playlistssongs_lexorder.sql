USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'playlistssongs'
		AND column_name = 'lexorder'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `playlistssongs`
		ADD COLUMN `lexorder` BINARY(200) DEFAULT '';
	END;
END IF|
DELIMITER ;