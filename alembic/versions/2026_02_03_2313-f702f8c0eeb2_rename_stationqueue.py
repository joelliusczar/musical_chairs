"""rename_stationqueue

Revision ID: f702f8c0eeb2
Revises: b4113a98e44a
Create Date: 2026-02-03 23:13:22.045492

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'f702f8c0eeb2'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('stationqueue', if_exists=True)

    op.drop_table('useractionhistory', if_exists=True)

    op.create_table('stationlogs',
        sa.Column('pk', sa.Integer, primary_key=True),
        sa.Column('stationfk', sa.Integer, sa.ForeignKey('stations.pk'), nullable=False),
        sa.Column('songfk', sa.Integer, sa.ForeignKey('songs.pk'), nullable=True),
        sa.Column('itemtype', sa.String(50), nullable=False, default='song'),
        sa.Column('action', sa.String(50), nullable=True),
        sa.Column('parentkey', sa.Integer, nullable=True),
        sa.Column('queuedtimestamp', sa.Double[float], nullable=False),
        sa.Column('playedtimestamp', sa.Double[float], nullable=True),
        sa.Column('userfk', sa.Integer, sa.ForeignKey('users.pk'), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        if_not_exists=True
    )

    op.create_index('idx_stationlogsstations', 'stationlogs', ['stationfk'], if_not_exists=True)


def downgrade() -> None:
    """Downgrade schema."""
    pass