"""
models/tts_log.py

Model for logging text-to-speech conversions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from aistudio.core.database import Base


class TTSLog(Base):
    """
    Text-to-Speech conversion log model.
    Stores information about each TTS conversion for tracking and analytics.
    """
    __tablename__ = "tts_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    speech_uid = Column(String(36), nullable=False, index=True, comment="UUID of the speech text")
    uuid_file = Column(String(36), nullable=False, comment="UUID of the generated audio file")
    text = Column(Text, nullable=False, comment="Text that was converted to speech")
    index = Column(Integer, nullable=False, default=0, comment="Fragment index if text is split")
    lang = Column(String(10), nullable=False, comment="Language: 'ru' or 'tg'")
    service = Column(String(50), nullable=False, comment="TTS service used (yandex, lumi)")
    stage = Column(Integer, nullable=False, default=0, index=True, comment="Processing stage (0=original, 1=mono, 2=noise_reduced, etc.)")
    stage_name = Column(String(50), nullable=True, comment="Name of the processing stage")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<TTSLog(id={self.id}, lang={self.lang}, service={self.service}, stage={self.stage})>"
