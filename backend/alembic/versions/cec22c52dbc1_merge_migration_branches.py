"""merge migration branches

Revision ID: cec22c52dbc1
Revises: 5b85b5db370e
Create Date: 2026-06-03 12:39:37.765931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cec22c52dbc1'
down_revision: Union[str, Sequence[str], None] = '5b85b5db370e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
