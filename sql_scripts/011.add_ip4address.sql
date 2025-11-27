USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'useractionhistory'
		AND column_name = 'ipv4address'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useractionhistory`
		ADD COLUMN `ipv4address` CHAR(24) NULL;
	END;
END IF|
DELIMITER ;