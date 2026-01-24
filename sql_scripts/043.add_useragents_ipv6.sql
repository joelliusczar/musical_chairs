USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'useragents'
		AND column_name = 'ipv6address'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useragents`
		ADD COLUMN `ipv6address` CHAR(50) NULL;
	END;
END IF|
DELIMITER ;