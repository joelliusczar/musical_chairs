USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.STATISTICS
	WHERE table_name = 'useragents'
		AND index_name = 'idx_useragent2'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useragents` ADD UNIQUE INDEX `idx_useragent2` (`ipv6address`,`ipv4address`,`hash`,`length`);
	END;
END IF|
DELIMITER ;