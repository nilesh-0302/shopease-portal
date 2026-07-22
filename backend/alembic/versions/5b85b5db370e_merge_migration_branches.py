"""merge migration branches

Revision ID: 5b85b5db370e
Revises: ca71c615ebe4, f6a7b8c9d0e1
Create Date: 2026-06-03 12:39:05.511001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b85b5db370e'
down_revision: Union[str, Sequence[str], None] = ('ca71c615ebe4', 'f6a7b8c9d0e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
