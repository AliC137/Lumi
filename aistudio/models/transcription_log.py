"""
models/transcription_log.py

Model for logging speech-to-text transcription operations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from aistudio.core.database import Base


class TranscriptionLog(Base):
    """
    Speech-to-Text transcription log model.
    Stores information about each transcription for tracking, analytics, and corrections.
    """
    __tablename__ = "transcription_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_uuid = Column(String(36), nullable=False, index=True, comment="UUID of the temporary audio file")
    text = Column(Text, nullable=False, comment="Transcribed text from speech")
    lang = Column(String(10), nullable=False, index=True, comment="Language: 'ru' or 'tg'")
    service = Column(String(50), nullable=False, index=True, comment="Transcription service used (vosk, yandex, etc.)")
    correct_text = Column(Text, nullable=True, comment="Corrected/verified text")
    stage = Column(Integer, nullable=False, default=0, index=True, comment="Processing stage (0=original)")
    stage_name = Column(String(50), nullable=True, comment="Name of the processing stage")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<TranscriptionLog(id={self.id}, lang={self.lang}, service={self.service}, stage={self.stage})>"
