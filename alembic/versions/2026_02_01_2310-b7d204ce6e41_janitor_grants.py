"""janitor_grants

Revision ID: b7d204ce6e41
Revises: bfbc65870010
Create Date: 2026-02-01 23:10:30.017195

"""
from typing import Sequence

from alembic import op
import musical_chairs_libs.dtos_and_utilities as mcr_u


# revision identifiers, used by Alembic.
revision: str = 'b7d204ce6e41'
down_revision: str | Sequence[str] | None = 'bfbc65870010'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    selectTables = [
        "albums",
        "artists",
        "jobs",
        "lastplayed",
        "songs",
        "songsartists",
        "stations",
        "stationlogs",
        "users",
    ]

    action = "SELECT"
    for table in selectTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )
    
    updateTables = [
        "lastplayed",
        "songs",
        "jobs",
    ]

    action = "UPDATE"
    for table in updateTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )

    insertTables = [
        "lastplayed",
        "songs",
    ]

    action = "INSERT"
    for table in insertTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )

    insertTables = [
        "jobs",
        "songs",
        "stationlogs",
    ]

    action = "DELETE"
    for table in insertTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )

    op.execute(
        f"GRANT CREATE TEMPORARY TABLES ON `<dbName>`.* TO <janitorUser>;"\
            .replace("<janitorUser>", mcr_u.DbUsers.JANITOR_USER("localhost"))\
            .replace("<dbName>", mcr_u.ConfigAcessors.db_name())
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass