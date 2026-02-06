"""normalize_opening_slash

Revision ID: ef3d7aae9a7e
Revises: a16fee024f6c
Create Date: 2026-02-01 22:02:59.710150

"""
from typing import Sequence

from alembic import op
import musical_chairs_libs.dtos_and_utilities as mcr_u


# revision identifiers, used by Alembic.
revision: str = 'ef3d7aae9a7e'
down_revision: str | Sequence[str] | None = 'a16fee024f6c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        r"""
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
        """.replace("<apiUser>",mcr_u.DbUsers.API_USER("localhost"))
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass