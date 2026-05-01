from typing import List, Optional, Dict, Generic, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session
from aistudio.repositories.transcription_log_repository import TranscriptionLogRepository
from aistudio.schemas.transcription_log_out import (
    TranscriptionLogOut,
    TranscriptionLogCreate,
    TranscriptionLogStats
)

T = TypeVar('T')


class PaginatedResult(BaseModel, Generic[T]):
    """Pagination result with metadata"""
    data: List[T]
    meta: Dict[str, int]


class TranscriptionLogService:
    """Service layer for transcription log operations"""

    def __init__(self, db: Session):
        self.repository = TranscriptionLogRepository(db)

    def create_log(self, log_data: TranscriptionLogCreate) -> TranscriptionLogOut:
        """Create a new transcription log entry"""
        log = self.repository.create(
            file_uuid=log_data.file_uuid,
            text=log_data.text,
            lang=log_data.lang,
            service=log_data.service,
            correct_text=log_data.correct_text,
            stage=log_data.stage,
            stage_name=log_data.stage_name
        )
        return TranscriptionLogOut.model_validate(log)

    def get_log_by_id(self, log_id: int) -> Optional[TranscriptionLogOut]:
        """Get transcription log by ID"""
        log = self.repository.get_by_id(log_id)
        return TranscriptionLogOut.model_validate(log) if log else None

    def get_logs_by_file_uuid(self, file_uuid: str) -> List[TranscriptionLogOut]:
        """Get all transcription logs for a specific file"""
        logs = self.repository.get_by_file_uuid(file_uuid)
        return [TranscriptionLogOut.model_validate(log) for log in logs]

    def get_all_logs(
        self, 
        page: int = 1, 
        per_page: int = 20
    ) -> PaginatedResult[TranscriptionLogOut]:
        """Get all transcription logs with pagination"""
        skip = (page - 1) * per_page
        logs = self.repository.get_all(skip=skip, limit=per_page)
        total = self.repository.count_total()
        
        return PaginatedResult(
            data=[TranscriptionLogOut.model_validate(log) for log in logs],
            meta={
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "last_page": (total + per_page - 1) // per_page if total > 0 else 1
            }
        )

    def get_logs_by_language(
        self, 
        lang: str, 
        page: int = 1, 
        per_page: int = 20
    ) -> PaginatedResult[TranscriptionLogOut]:
        """Get transcription logs by language with pagination"""
        skip = (page - 1) * per_page
        logs = self.repository.get_by_language(lang, skip=skip, limit=per_page)
        total = self.repository.count_by_language(lang)
        
        return PaginatedResult(
            data=[TranscriptionLogOut.model_validate(log) for log in logs],
            meta={
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "last_page": (total + per_page - 1) // per_page if total > 0 else 1
            }
        )

    def get_logs_by_service(
        self, 
        service: str, 
        page: int = 1, 
        per_page: int = 20
    ) -> PaginatedResult[TranscriptionLogOut]:
        """Get transcription logs by service with pagination"""
        skip = (page - 1) * per_page
        logs = self.repository.get_by_service(service, skip=skip, limit=per_page)
        total = self.repository.count_by_service(service)
        
        return PaginatedResult(
            data=[TranscriptionLogOut.model_validate(log) for log in logs],
            meta={
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "last_page": (total + per_page - 1) // per_page if total > 0 else 1
            }
        )

    def get_logs_by_stage(
        self, 
        stage: int, 
        page: int = 1, 
        per_page: int = 20
    ) -> PaginatedResult[TranscriptionLogOut]:
        """Get transcription logs by processing stage with pagination"""
        skip = (page - 1) * per_page
        logs = self.repository.get_by_stage(stage, skip=skip, limit=per_page)
        total = self.repository.count_by_stage(stage)
        
        return PaginatedResult(
            data=[TranscriptionLogOut.model_validate(log) for log in logs],
            meta={
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "last_page": (total + per_page - 1) // per_page if total > 0 else 1
            }
        )

    def get_uncorrected_logs(
        self, 
        page: int = 1, 
        per_page: int = 20
    ) -> PaginatedResult[TranscriptionLogOut]:
        """Get transcription logs without corrections with pagination"""
        skip = (page - 1) * per_page
        logs = self.repository.get_uncorrected(skip=skip, limit=per_page)
        total = self.repository.count_total() - self.repository.get_corrected_count()
        
        return PaginatedResult(
            data=[TranscriptionLogOut.model_validate(log) for log in logs],
            meta={
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "last_page": (total + per_page - 1) // per_page if total > 0 else 1
            }
        )

    def update_correction(self, log_id: int, correct_text: str) -> Optional[TranscriptionLogOut]:
        """Update the corrected text for a transcription log"""
        log = self.repository.update_correction(log_id, correct_text)
        return TranscriptionLogOut.model_validate(log) if log else None

    def get_statistics(self) -> TranscriptionLogStats:
        """Get transcription statistics"""
        total = self.repository.count_total()
        by_language = self.repository.get_languages_stats()
        by_service = self.repository.get_services_stats()
        by_stage = self.repository.get_stages_stats()
        corrected_count = self.repository.get_corrected_count()
        avg_length = self.repository.get_average_text_length()
        recent_logs = self.repository.get_recent(limit=10)
        
        return TranscriptionLogStats(
            total_transcriptions=total,
            by_language=by_language,
            by_service=by_service,
            by_stage=by_stage,
            corrected_count=corrected_count,
            average_text_length=avg_length,
            recent_transcriptions=[
                TranscriptionLogOut.model_validate(log) for log in recent_logs
            ]
        )
