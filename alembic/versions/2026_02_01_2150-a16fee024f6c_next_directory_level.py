"""next_directory_level

Revision ID: a16fee024f6c
Revises: 
Create Date: 2026-02-01 21:50:45.076093

"""
from typing import Sequence

from alembic import op
import musical_chairs_libs.dtos_and_utilities as mcr_u


# revision identifiers, used by Alembic.
revision: str = 'a16fee024f6c'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        r"""
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
        """.replace("<apiUser>",mcr_u.DbUsers.API_USER("localhost"))
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass