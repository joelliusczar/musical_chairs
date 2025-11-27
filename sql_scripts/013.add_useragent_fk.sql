USE `<dbName>`;
DELIMITER |
IF (SELECT COUNT(1) = 0 FROM information_schema.COLUMNS
	WHERE table_name = 'useractionhistory'
		AND column_name = 'useragentsfk'
		AND table_schema = '<dbName>'
	) THEN
	BEGIN NOT ATOMIC
		ALTER TABLE `useractionhistory`
		ADD COLUMN `useragentsfk` INT NULL;
		ALTER TABLE `useractionhistory`
		ADD CONSTRAINT `fk_useragents` FOREIGN KEY (`useragentsfk`) REFERENCES `useragents`(`pk`);
	END;
END IF|
DELIMITER ;