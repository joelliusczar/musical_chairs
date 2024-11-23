USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'songs'
		AND column_name = 'internalpath'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songs`
		ADD COLUMN `internalpath` varchar(255) NOT NULL DEFAULT `path`;
	END;
END IF|
DELIMITER ;