"""api_grants

Revision ID: 9ef17243a398
Revises: ef3d7aae9a7e
Create Date: 2026-02-01 22:29:01.199212

"""
from typing import Sequence

from alembic import op
import musical_chairs_libs.dtos_and_utilities as mcr_u



# revision identifiers, used by Alembic.
revision: str = '9ef17243a398'
down_revision: str | Sequence[str] | None = 'ef3d7aae9a7e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    selectTables = [
        "albums",
        "artists",
        "jobs",
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
        "userroles",
        "users",
        "visitors"
    ]
    skipSet = {
        ("lastplayed", "UPDATE"),
        ("lastplayed", "INSERT"),
        ("visitors", "UPDATE"),
        ("visitors", "DELETE"),
    }
    for table in selectTables:
        for action in ["SELECT", "UPDATE", "INSERT", "DELETE"]:
            if (table, action) in skipSet:
                continue
            op.execute(
                f"GRANT {action} ON {table} TO "
                f"{mcr_u.DbUsers.API_USER("localhost")}"
            )




def downgrade() -> None:
    """Downgrade schema."""
    pass