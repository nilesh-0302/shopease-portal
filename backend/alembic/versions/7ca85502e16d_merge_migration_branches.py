"""merge migration branches

Revision ID: 7ca85502e16d
Revises: adc68a4f39f9, b2c3d4e5f6a7
Create Date: 2026-06-03 16:20:24.537862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ca85502e16d'
down_revision: Union[str, Sequence[str], None] = ('adc68a4f39f9', 'b2c3d4e5f6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
