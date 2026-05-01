"""
Service layer for TTS logging operations.
Hides repository implementation details from API layer.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from aistudio.repositories.tts_log_repository import TTSLogRepository
from aistudio.schemas.tts_log_out import TTSLogOut, TTSLogCreate, TTSLogStats


class PaginatedResult:
    """Standardized pagination result"""
    def __init__(self, data: List[Any], current_page: int, per_page: int, total: int):
        self.data = data
        self.meta = {
            'current_page': current_page,
            'last_page': (total + per_page - 1) // per_page if per_page > 0 else 1,
            'per_page': per_page,
            'total': total
        }
    
    def to_dict(self) -> dict:
        return {
            'data': self.data,
            'meta': self.meta
        }


class TTSLogService:
    """Service for TTS log operations"""
    
    def __init__(self, db: Session):
        self.repository = TTSLogRepository(db)
    
    def get_all_logs(
        self,
        page: int = 1,
        per_page: int = 50,
        language: Optional[str] = None,
        service: Optional[str] = None,
        stage: Optional[int] = None
    ) -> PaginatedResult:
        """
        Get all TTS logs with pagination and optional filtering
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of records per page
            language: Optional language filter (ru, tg)
            service: Optional service filter (yandex, lumi)
            stage: Optional stage filter
        
        Returns:
            PaginatedResult with data and meta information
        """
        skip = (page - 1) * per_page
        
        # Get filtered logs
        if language:
            logs = self.repository.get_by_language(language, skip, per_page)
            total = self.repository.count_by_language(language)
        elif service:
            logs = self.repository.get_by_service(service, skip, per_page)
            total = self.repository.count_by_service(service)
        elif stage is not None:
            logs = self.repository.get_by_stage(stage, skip, per_page)
            total = self.repository.count_by_stage(stage)
        else:
            logs = self.repository.get_all(skip, per_page)
            total = self.repository.count_total()
        
        # Convert to output schema
        data = [TTSLogOut.model_validate(log) for log in logs]
        
        return PaginatedResult(
            data=data,
            current_page=page,
            per_page=per_page,
            total=total
        )
    
    def get_log_by_id(self, log_id: int) -> Optional[TTSLogOut]:
        """Get a specific TTS log by ID"""
        log = self.repository.get_by_id(log_id)
        return TTSLogOut.model_validate(log) if log else None
    
    def get_logs_by_speech_uid(self, speech_uid: str) -> List[TTSLogOut]:
        """Get all logs for a specific speech UID"""
        logs = self.repository.get_by_speech_uid(speech_uid)
        return [TTSLogOut.model_validate(log) for log in logs]
    
    def get_statistics(self) -> TTSLogStats:
        """Get comprehensive TTS statistics"""
        total_conversions = self.repository.count_total()
        conversions_by_language = self.repository.count_by_language()
        conversions_by_service = self.repository.count_by_service()
        recent_conversions = self.repository.get_all(skip=0, limit=10)
        avg_text_length = self.repository.get_average_text_length()
        
        return TTSLogStats(
            total_conversions=total_conversions,
            conversions_by_language=conversions_by_language,
            conversions_by_service=conversions_by_service,
            recent_conversions=[TTSLogOut.model_validate(log) for log in recent_conversions],
            average_text_length=round(avg_text_length, 2) if avg_text_length else 0.0
        )
    
    def create_log(self, log_data: TTSLogCreate) -> TTSLogOut:
        """Create a new TTS log entry"""
        log = self.repository.create(log_data)
        return TTSLogOut.model_validate(log)
    
    def get_logs_by_stage(self, stage: int, page: int = 1, per_page: int = 50) -> PaginatedResult:
        """Get logs filtered by processing stage"""
        skip = (page - 1) * per_page
        logs = self.repository.get_by_stage(stage, skip, per_page)
        total = self.repository.count_by_stage(stage)
        
        data = [TTSLogOut.model_validate(log) for log in logs]
        
        return PaginatedResult(
            data=data,
            current_page=page,
            per_page=per_page,
            total=total
        )
