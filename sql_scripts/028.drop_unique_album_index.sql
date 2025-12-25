USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) > 0 FROM information_schema.STATISTICS
	WHERE table_name = 'albums'
		AND index_name = 'idx_uniquealbumnameforartist'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `albums` DROP INDEX `idx_uniquealbumnameforartist`;
	END;
END IF|
DELIMITER ;