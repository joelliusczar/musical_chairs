"""userrole_keypath_index

Revision ID: f0f6aa97edac
Revises: b7d204ce6e41
Create Date: 2026-02-01 23:19:05.040659

"""
from typing import Sequence

# from alembic import op



# revision identifiers, used by Alembic.
revision: str = 'f0f6aa97edac'
down_revision: str | Sequence[str] | None = 'b7d204ce6e41'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass
#     op.execute(
# """
# CREATE UNIQUE INDEX IF NOT EXISTS `idx_pathpermissions`
# 	ON `pathuserpermissions` (`userfk`, `path`, `role`);
# """
#     )


def downgrade() -> None:
    """Downgrade schema."""
    pass