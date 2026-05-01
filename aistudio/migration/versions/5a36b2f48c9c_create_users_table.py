"""create users table

Revision ID: 5a36b2f48c9c
Revises: 
Create Date: 2025-07-07 17:45:40.112034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5a36b2f48c9c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('login', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('created_dt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_dt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_dt', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)


    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_users_login'), table_name='users')
    op.drop_table('users')

