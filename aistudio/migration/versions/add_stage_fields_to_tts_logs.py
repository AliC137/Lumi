"""add stage fields to tts_logs

Revision ID: add_stage_fields_001
Revises: add_tts_logs_001
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_stage_fields_001'
down_revision = 'add_tts_logs_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add stage and stage_name columns to tts_logs table
    op.add_column('tts_logs', sa.Column('stage', sa.Integer(), nullable=False, server_default='0', comment='Processing stage'))
    op.add_column('tts_logs', sa.Column('stage_name', sa.String(length=50), nullable=True, comment='Name of the processing stage'))
    
    # Add index on stage for better query performance
    op.create_index('ix_tts_logs_stage', 'tts_logs', ['stage'])


def downgrade():
    # Remove index and columns
    op.drop_index('ix_tts_logs_stage', table_name='tts_logs')
    op.drop_column('tts_logs', 'stage_name')
    op.drop_column('tts_logs', 'stage')
