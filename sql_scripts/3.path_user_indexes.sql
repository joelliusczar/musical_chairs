USE `<dbName>`;

#this script is necessary due to sqlalchemy not adding my explicit index
#and mariadb shitting the bed due to it thinking there's no index

CREATE INDEX IF NOT EXISTS `idx_pathuserpermissions_userfk`
	ON `pathuserpermissions`(`userfk`);

CREATE UNIQUE INDEX IF NOT EXISTS `idx_pathpermissions`
	ON `pathuserpermissions` (`userfk`, `path`, `role`);