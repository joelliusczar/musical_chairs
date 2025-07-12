USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'albums'
		AND column_name = 'versionnote'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `albums`
		ADD COLUMN `versionnote` CHAR(200) NULL;
	END;
END IF|
DELIMITER ;