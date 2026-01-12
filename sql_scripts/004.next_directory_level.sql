CREATE OR REPLACE FUNCTION next_directory_level (
	path VARCHAR(2000),
	prefix VARCHAR(2000)
) RETURNS VARCHAR(2000) CHARSET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci
BEGIN
	DECLARE escapedPrefix VARCHAR(2000);
	DECLARE pattern VARCHAR(2000);
	DECLARE matchResult VARCHAR(2000);
	SET escapedPrefix = REPLACE(prefix, '\(', '\\(');
	SET escapedPrefix = REPLACE(escapedPrefix, '\)', '\\)');
	SET escapedPrefix = REPLACE(escapedPrefix, '\*', '\\*');
	SET escapedPrefix = REPLACE(escapedPrefix, '\+', '\\+');
	SET escapedPrefix = REPLACE(escapedPrefix, '\[', '\\[');
	SET escapedPrefix = REPLACE(escapedPrefix, '\]', '\\]');
	SET escapedPrefix = REPLACE(escapedPrefix, '\?', '\\?');
	SET escapedPrefix = REPLACE(escapedPrefix, '\$', '\\$');
	SET escapedPrefix = REPLACE(escapedPrefix, '\^', '\\^');
	SET escapedPrefix = REPLACE(escapedPrefix, '\{', '\\{');
	SET escapedPrefix = REPLACE(escapedPrefix, '\}', '\\}');
	SET escapedPrefix = REPLACE(escapedPrefix, '\|', '\\|');
	SET pattern = CONCAT('(',COALESCE(escapedPrefix, ''), '[^/]*/?)');
	SET matchResult = REGEXP_SUBSTR(path, pattern);
	RETURN matchResult;
END;

GRANT EXECUTE ON FUNCTION next_directory_level TO <apiUser>;