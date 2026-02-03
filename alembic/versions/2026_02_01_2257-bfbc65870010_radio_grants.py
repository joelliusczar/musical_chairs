"""radio_grants

Revision ID: bfbc65870010
Revises: 9ef17243a398
Create Date: 2026-02-01 22:57:50.802002

"""
from typing import Sequence

from alembic import op
import musical_chairs_libs.dtos_and_utilities as mcr_u


# revision identifiers, used by Alembic.
revision: str = 'bfbc65870010'
down_revision: str | Sequence[str] | None = '9ef17243a398'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    selectTables = [
        "albums",
        "artists",
        "lastplayed",
        "playlists",
        "playlistssongs",
        "songs",
        "songsartists",
        "songcovers",
        "stations",
        "stationlogs",
        "stationsalbums",
        "stationsplaylists",
        "stationssongs",
        "users",
    ]
    
    action = "SELECT"
    for table in selectTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )
    
    updateTables = [
        "stations",
        "stationssongs",
        "stationsalbums",
        "stationsplaylists",
        "stationlogs",
    ]

    action = "UPDATE"
    for table in updateTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )

    insertTables = [
        "stationlogs"
    ]

    action = "INSERT"
    for table in insertTables:
        op.execute(
            f"GRANT {action} ON {table} TO "
            f"{mcr_u.DbUsers.API_USER("localhost")}"
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass