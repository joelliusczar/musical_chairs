USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) > 0 FROM information_schema.STATISTICS
	WHERE table_name = 'useragents'
		AND index_name = 'idx_useragenthash'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useragents` DROP INDEX `idx_useragenthash`;
	END;
END IF|
DELIMITER ;