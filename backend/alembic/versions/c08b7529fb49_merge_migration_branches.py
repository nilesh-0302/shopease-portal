"""merge migration branches

Revision ID: c08b7529fb49
Revises: 7a938eb653fc, e5f6a7b8c9d0
Create Date: 2026-06-02 19:27:58.762703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c08b7529fb49'
down_revision: Union[str, Sequence[str], None] = ('7a938eb653fc', 'e5f6a7b8c9d0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
