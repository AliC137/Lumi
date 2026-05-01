from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class TranscriptionLogCreate(BaseModel):
    """Schema for creating a transcription log entry"""
    file_uuid: str = Field(..., description="UUID of the temporary audio file")
    text: str = Field(..., description="Transcribed text from speech")
    lang: str = Field(..., description="Language: 'ru' or 'tg'")
    service: str = Field(..., description="Transcription service used (vosk/yandex)")
    correct_text: Optional[str] = Field(None, description="Corrected/verified text")
    stage: int = Field(default=0, description="Processing stage")
    stage_name: Optional[str] = Field(None, description="Name of the processing stage")


class TranscriptionLogOut(BaseModel):
    """Schema for transcription log output"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    file_uuid: str
    text: str
    lang: str
    service: str
    correct_text: Optional[str]
    stage: int
    stage_name: Optional[str]
    created_at: datetime


class TranscriptionLogUpdate(BaseModel):
    """Schema for updating transcription log (corrections)"""
    correct_text: str = Field(..., description="Corrected/verified text")


class TranscriptionLogStats(BaseModel):
    """Statistics for transcription logs"""
    total_transcriptions: int = Field(..., description="Total number of transcriptions")
    by_language: dict = Field(..., description="Count by language")
    by_service: dict = Field(..., description="Count by service")
    by_stage: dict = Field(..., description="Count by processing stage")
    corrected_count: int = Field(..., description="Number of corrected transcriptions")
    average_text_length: float = Field(..., description="Average length of transcribed text")
    recent_transcriptions: List[TranscriptionLogOut] = Field(..., description="Recent transcription logs")
