USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'songs'
		AND column_name = 'deletedbyuserfk'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `songs`
		ADD COLUMN `deletedbyuserfk` int(11) DEFAULT NULL;
		ALTER TABLE `songs`
		ADD CONSTRAINT `songs_ibfk_3` FOREIGN KEY (`deletedbyuserfk`) REFERENCES `users` (`pk`);
	END;	
END IF|
DELIMITER ;