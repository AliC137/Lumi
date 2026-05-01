"""add transcription_logs table

Revision ID: add_transcription_logs_001
Revises: add_stage_fields_001
Create Date: 2026-01-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_transcription_logs_001'
down_revision = 'add_stage_fields_001'
branch_labels = None
depends_on = None


def upgrade():
    # Create transcription_logs table
    op.create_table(
        'transcription_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('file_uuid', sa.String(length=36), nullable=False, comment='UUID of the temporary audio file'),
        sa.Column('text', sa.Text(), nullable=False, comment='Transcribed text from speech'),
        sa.Column('lang', sa.String(length=10), nullable=False, comment="Language: 'ru' or 'tg'"),
        sa.Column('service', sa.String(length=50), nullable=False, comment='Transcription service used'),
        sa.Column('correct_text', sa.Text(), nullable=True, comment='Corrected/verified text'),
        sa.Column('stage', sa.Integer(), nullable=False, server_default='0', comment='Processing stage'),
        sa.Column('stage_name', sa.String(length=50), nullable=True, comment='Name of the processing stage'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_transcription_logs_file_uuid', 'transcription_logs', ['file_uuid'])
    op.create_index('ix_transcription_logs_lang', 'transcription_logs', ['lang'])
    op.create_index('ix_transcription_logs_service', 'transcription_logs', ['service'])
    op.create_index('ix_transcription_logs_stage', 'transcription_logs', ['stage'])
    op.create_index('ix_transcription_logs_created_at', 'transcription_logs', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_transcription_logs_created_at', table_name='transcription_logs')
    op.drop_index('ix_transcription_logs_stage', table_name='transcription_logs')
    op.drop_index('ix_transcription_logs_service', table_name='transcription_logs')
    op.drop_index('ix_transcription_logs_lang', table_name='transcription_logs')
    op.drop_index('ix_transcription_logs_file_uuid', table_name='transcription_logs')
    
    # Drop table
    op.drop_table('transcription_logs')
