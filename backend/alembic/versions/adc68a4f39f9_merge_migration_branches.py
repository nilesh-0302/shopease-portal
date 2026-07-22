"""merge migration branches

Revision ID: adc68a4f39f9
Revises: a1b2c3d4e5f6, cec22c52dbc1
Create Date: 2026-06-03 14:25:42.058990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adc68a4f39f9'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'cec22c52dbc1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
