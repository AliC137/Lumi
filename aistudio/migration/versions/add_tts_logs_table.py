"""add tts_logs table

Revision ID: add_tts_logs_001
Revises: add_last_login_002
Create Date: 2025-12-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_tts_logs_001'
down_revision: Union[str, Sequence[str], None] = 'add_last_login_002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tts_logs table for logging text-to-speech conversions."""
    op.create_table(
        'tts_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('speech_uid', sa.String(36), nullable=False, comment='UUID of the speech text'),
        sa.Column('uuid_file', sa.String(36), nullable=False, comment='UUID of the generated audio file'),
        sa.Column('text', sa.Text(), nullable=False, comment='Text that was converted to speech'),
        sa.Column('index', sa.Integer(), nullable=False, server_default='0', comment='Fragment index if text is split'),
        sa.Column('lang', sa.String(10), nullable=False, comment="Language: 'ru' or 'tg'"),
        sa.Column('service', sa.String(50), nullable=False, comment='TTS service used'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create indexes for common queries
    op.create_index('idx_tts_logs_speech_uid', 'tts_logs', ['speech_uid'])
    op.create_index('idx_tts_logs_created_at', 'tts_logs', ['created_at'])
    op.create_index('idx_tts_logs_lang', 'tts_logs', ['lang'])
    op.create_index('idx_tts_logs_service', 'tts_logs', ['service'])


def downgrade() -> None:
    """Drop tts_logs table."""
    op.drop_index('idx_tts_logs_service', table_name='tts_logs')
    op.drop_index('idx_tts_logs_lang', table_name='tts_logs')
    op.drop_index('idx_tts_logs_created_at', table_name='tts_logs')
    op.drop_index('idx_tts_logs_speech_uid', table_name='tts_logs')
    op.drop_table('tts_logs')
