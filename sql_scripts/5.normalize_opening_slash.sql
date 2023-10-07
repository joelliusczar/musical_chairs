CREATE OR REPLACE FUNCTION normalize_opening_slash (
	path VARCHAR(2000),
	addSlash BOOL
) RETURNS VARCHAR(2000)
BEGIN
	IF COALESCE(addSlash, 0) = 1 THEN
		IF LENGTH(path) > 0 AND SUBSTRING(path, 1, 1) = '/' THEN
			RETURN PATH;
		END IF;
		RETURN CONCAT('/', path);
	ELSE
		IF LENGTH(path) > 0 AND SUBSTRING(path, 1, 1) <> '/' THEN
			RETURN path;
		END IF;
	END IF;
	RETURN SUBSTRING(path, 2);
END;

GRANT EXECUTE ON FUNCTION normalize_opening_slash TO <apiUser>;