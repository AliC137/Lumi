"""add is_active column to users table

Revision ID: add_is_active_001
Revises: 541be14d7255
Create Date: 2025-12-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_active_001'
down_revision: Union[str, Sequence[str], None] = '541be14d7255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_active column to users table."""
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Remove is_active column from users table."""
    op.drop_column('users', 'is_active')
