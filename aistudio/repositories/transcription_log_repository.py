from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict
from aistudio.models.transcription_log import TranscriptionLog


class TranscriptionLogRepository:
    """Repository for transcription log operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        file_uuid: str,
        text: str,
        lang: str,
        service: str,
        correct_text: Optional[str] = None,
        stage: int = 0,
        stage_name: Optional[str] = None
    ) -> TranscriptionLog:
        """Create a new transcription log entry"""
        transcription_log = TranscriptionLog(
            file_uuid=file_uuid,
            text=text,
            lang=lang,
            service=service,
            correct_text=correct_text,
            stage=stage,
            stage_name=stage_name
        )
        self.db.add(transcription_log)
        self.db.commit()
        self.db.refresh(transcription_log)
        return transcription_log

    def get_by_id(self, log_id: int) -> Optional[TranscriptionLog]:
        """Get transcription log by ID"""
        return self.db.query(TranscriptionLog).filter(TranscriptionLog.id == log_id).first()

    def get_by_file_uuid(self, file_uuid: str) -> List[TranscriptionLog]:
        """Get all transcription logs for a specific file"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.file_uuid == file_uuid
        ).order_by(desc(TranscriptionLog.created_at)).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TranscriptionLog]:
        """Get all transcription logs with pagination"""
        return self.db.query(TranscriptionLog).order_by(
            desc(TranscriptionLog.created_at)
        ).offset(skip).limit(limit).all()

    def get_by_language(self, lang: str, skip: int = 0, limit: int = 100) -> List[TranscriptionLog]:
        """Get transcription logs by language"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.lang == lang
        ).order_by(desc(TranscriptionLog.created_at)).offset(skip).limit(limit).all()

    def get_by_service(self, service: str, skip: int = 0, limit: int = 100) -> List[TranscriptionLog]:
        """Get transcription logs by service"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.service == service
        ).order_by(desc(TranscriptionLog.created_at)).offset(skip).limit(limit).all()

    def get_by_stage(self, stage: int, skip: int = 0, limit: int = 100) -> List[TranscriptionLog]:
        """Get transcription logs by processing stage"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.stage == stage
        ).order_by(desc(TranscriptionLog.created_at)).offset(skip).limit(limit).all()

    def get_uncorrected(self, skip: int = 0, limit: int = 100) -> List[TranscriptionLog]:
        """Get transcription logs without corrections"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.correct_text.is_(None)
        ).order_by(desc(TranscriptionLog.created_at)).offset(skip).limit(limit).all()

    def count_total(self) -> int:
        """Count total transcription logs"""
        return self.db.query(TranscriptionLog).count()

    def count_by_language(self, lang: Optional[str] = None) -> int:
        """Count transcription logs by language (or all if no lang specified)"""
        query = self.db.query(TranscriptionLog)
        if lang:
            query = query.filter(TranscriptionLog.lang == lang)
        return query.count()

    def count_by_service(self, service: Optional[str] = None) -> int:
        """Count transcription logs by service (or all if no service specified)"""
        query = self.db.query(TranscriptionLog)
        if service:
            query = query.filter(TranscriptionLog.service == service)
        return query.count()

    def count_by_stage(self, stage: Optional[int] = None) -> int:
        """Count transcription logs by stage (or all if no stage specified)"""
        query = self.db.query(TranscriptionLog)
        if stage is not None:
            query = query.filter(TranscriptionLog.stage == stage)
        return query.count()

    def get_corrected_count(self) -> int:
        """Count transcription logs with corrections"""
        return self.db.query(TranscriptionLog).filter(
            TranscriptionLog.correct_text.isnot(None)
        ).count()

    def get_languages_stats(self) -> Dict[str, int]:
        """Get count of transcriptions by language"""
        stats = self.db.query(
            TranscriptionLog.lang, func.count(TranscriptionLog.id)
        ).group_by(TranscriptionLog.lang).all()
        return {lang: count for lang, count in stats}

    def get_services_stats(self) -> Dict[str, int]:
        """Get count of transcriptions by service"""
        stats = self.db.query(
            TranscriptionLog.service, func.count(TranscriptionLog.id)
        ).group_by(TranscriptionLog.service).all()
        return {service: count for service, count in stats}

    def get_stages_stats(self) -> Dict[int, int]:
        """Get count of transcriptions by stage"""
        stats = self.db.query(
            TranscriptionLog.stage, func.count(TranscriptionLog.id)
        ).group_by(TranscriptionLog.stage).all()
        return {stage: count for stage, count in stats}

    def get_average_text_length(self) -> float:
        """Calculate average length of transcribed text"""
        avg_length = self.db.query(func.avg(func.length(TranscriptionLog.text))).scalar()
        return float(avg_length) if avg_length else 0.0

    def update_correction(self, log_id: int, correct_text: str) -> Optional[TranscriptionLog]:
        """Update the corrected text for a transcription log"""
        log = self.get_by_id(log_id)
        if log:
            log.correct_text = correct_text
            self.db.commit()
            self.db.refresh(log)
        return log

    def get_recent(self, limit: int = 10) -> List[TranscriptionLog]:
        """Get recent transcription logs"""
        return self.db.query(TranscriptionLog).order_by(
            desc(TranscriptionLog.created_at)
        ).limit(limit).all()
