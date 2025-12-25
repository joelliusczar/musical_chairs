USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.STATISTICS
	WHERE table_name = 'albums'
		AND index_name = 'idx_uniquealbumnameforartist2'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `albums` ADD UNIQUE INDEX `idx_uniquealbumnameforartist2` (`name`,`albumartistfk`,`ownerfk`,`versionnote`);
	END;
END IF|
DELIMITER ;