"""
repositories/tts_log_repository.py

Repository for TTS log database operations.
"""

from sqlalchemy.orm import Session
from aistudio.models.tts_log import TTSLog
from aistudio.schemas.tts_log_out import TTSLogCreate
from datetime import datetime, timedelta
from typing import List, Optional


class TTSLogRepository:
    """Repository for managing TTS logs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, log_data: TTSLogCreate) -> TTSLog:
        """Create a new TTS log entry"""
        log = TTSLog(
            speech_uid=log_data.speech_uid,
            uuid_file=log_data.uuid_file,
            text=log_data.text,
            index=log_data.index,
            lang=log_data.lang,
            service=log_data.service
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_by_id(self, log_id: int) -> Optional[TTSLog]:
        """Get TTS log by ID"""
        return self.db.query(TTSLog).filter(TTSLog.id == log_id).first()
    
    def get_by_speech_uid(self, speech_uid: str) -> List[TTSLog]:
        """Get all logs for a specific speech UUID"""
        return self.db.query(TTSLog).filter(
            TTSLog.speech_uid == speech_uid
        ).order_by(TTSLog.index).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[TTSLog]:
        """Get all TTS logs with pagination"""
        return self.db.query(TTSLog).order_by(
            TTSLog.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_by_language(self, lang: str, skip: int = 0, limit: int = 100) -> List[TTSLog]:
        """Get logs filtered by language"""
        return self.db.query(TTSLog).filter(
            TTSLog.lang == lang
        ).order_by(TTSLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_service(self, service: str, skip: int = 0, limit: int = 100) -> List[TTSLog]:
        """Get logs filtered by service"""
        return self.db.query(TTSLog).filter(
            TTSLog.service == service
        ).order_by(TTSLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_stage(self, stage: int, skip: int = 0, limit: int = 100) -> List[TTSLog]:
        """Get logs filtered by processing stage"""
        return self.db.query(TTSLog).filter(
            TTSLog.stage == stage
        ).order_by(TTSLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_recent(self, hours: int = 24) -> List[TTSLog]:
        """Get logs from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.db.query(TTSLog).filter(
            TTSLog.created_at >= cutoff
        ).order_by(TTSLog.created_at.desc()).all()
    
    def count_by_stage(self, stage: int = None) -> int:
        """Get count of conversions by stage"""
        if stage is not None:
            return self.db.query(TTSLog).filter(TTSLog.stage == stage).count()
        return self.db.query(TTSLog).count()
    
    def count_total(self) -> int:
        """Get total count of TTS logs"""
        return self.db.query(TTSLog).count()
    
    def count_by_language(self, lang: str = None) -> dict | int:
        """Get count of conversions by language"""
        from sqlalchemy import func
        
        if lang:
            # Count specific language
            return self.db.query(TTSLog).filter(TTSLog.lang == lang).count()
        
        # Count all languages grouped
        results = self.db.query(
            TTSLog.lang,
            func.count(TTSLog.id).label('count')
        ).group_by(TTSLog.lang).all()
        
        return {lang: count for lang, count in results}
    
    def count_by_service(self, service: str = None) -> dict | int:
        """Get count of conversions by service"""
        from sqlalchemy import func
        
        if service:
            # Count specific service
            return self.db.query(TTSLog).filter(TTSLog.service == service).count()
        
        # Count all services grouped
        results = self.db.query(
            TTSLog.service,
            func.count(TTSLog.id).label('count')
        ).group_by(TTSLog.service).all()
        
        return {service: count for service, count in results}
    
    def get_average_text_length(self) -> float:
        """Calculate average text length"""
        from sqlalchemy import func
        result = self.db.query(
            func.avg(func.length(TTSLog.text))
        ).scalar()
        
        return float(result) if result else 0.0
    
    def delete(self, log_id: int) -> bool:
        """Delete a TTS log entry"""
        log = self.get_by_id(log_id)
        if log:
            self.db.delete(log)
            self.db.commit()
            return True
        return False
