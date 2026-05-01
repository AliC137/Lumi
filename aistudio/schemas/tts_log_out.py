"""
schemas/tts_log_out.py

Pydantic schemas for TTS log output.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TTSLogOut(BaseModel):
    """Output schema for TTS log"""
    id: int
    speech_uid: str
    uuid_file: str
    text: str
    index: int
    lang: str = Field(..., description="Language: 'ru' or 'tg'")
    service: str
    stage: int = Field(default=0, description="Processing stage number")
    stage_name: Optional[str] = Field(None, description="Name of the processing stage")
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class TTSLogCreate(BaseModel):
    """Schema for creating a TTS log entry"""
    speech_uid: str
    uuid_file: str
    text: str
    index: int = 0
    lang: str = Field(..., description="Language: 'ru' or 'tg'")
    service: str
    stage: int = Field(default=0, description="Processing stage number")
    stage_name: Optional[str] = Field(None, description="Name of the processing stage")


class TTSLogStats(BaseModel):
    """Statistics for TTS logs"""
    total_conversions: int
    conversions_by_language: dict
    conversions_by_service: dict
    recent_conversions: List[TTSLogOut]
    average_text_length: float
