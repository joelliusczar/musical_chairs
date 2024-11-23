USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 1 FROM information_schema.COLUMNS
	WHERE table_name = 'useractionhistory'
		AND column_name = 'requestedtimestamp'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useractionhistory` DROP COLUMN `requestedtimestamp`;
	END;
END IF|
DELIMITER ;