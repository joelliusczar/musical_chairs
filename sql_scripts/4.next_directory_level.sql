CREATE OR REPLACE FUNCTION next_directory_level (
	path VARCHAR(2000),
	prefix VARCHAR(2000)
) RETURNS VARCHAR(2000)
BEGIN
	DECLARE pattern VARCHAR(2000);
	DECLARE matchResult VARCHAR(2000);
	SET pattern = CONCAT('(',COALESCE(prefix, ''), '[^/]*/?)');
	SET matchResult = REGEXP_SUBSTR(path, pattern);
	RETURN matchResult;
END;

GRANT EXECUTE ON FUNCTION next_directory_level TO <apiUser>;