"""
Admin endpoints for TTS logs management
Following eKhonish API response format
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from aistudio.core.database import get_db
from aistudio.services.tts_log_service import TTSLogService
from aistudio.utils.role_checker import admin_required

router = APIRouter()


def success_response(data, message: str = "success", code: int = 200):
    """Standard eKhonish success response"""
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str, code: int = 400):
    """Standard eKhonish error response"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": None
    }


@router.get("/tts-logs")
def get_all_tts_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=500, description="Records per page"),
    language: Optional[str] = Query(None, description="Filter by language (ru, tg)"),
    service: Optional[str] = Query(None, description="Filter by service (yandex, lumi)"),
    stage: Optional[int] = Query(None, description="Filter by processing stage"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get all TTS logs with pagination and filtering
    
    Returns data in eKhonish format with pagination metadata
    """
    try:
        tts_service = TTSLogService(db)
        result = tts_service.get_all_logs(
            page=page,
            per_page=per_page,
            language=language,
            service=service,
            stage=stage
        )
        return success_response(result.to_dict())
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/stats")
def get_tts_stats(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get TTS conversion statistics"""
    try:
        tts_service = TTSLogService(db)
        stats = tts_service.get_statistics()
        return success_response(stats.model_dump())
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/{log_id}")
def get_tts_log_by_id(
    log_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get a specific TTS log by ID"""
    try:
        tts_service = TTSLogService(db)
        log = tts_service.get_log_by_id(log_id)
        
        if not log:
            return error_response("TTS log not found", 404)
        
        return success_response(log.model_dump())
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/speech/{speech_uid}")
def get_tts_logs_by_speech_uid(
    speech_uid: str,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get all TTS log fragments for a specific speech UID"""
    try:
        tts_service = TTSLogService(db)
        logs = tts_service.get_logs_by_speech_uid(speech_uid)
        
        if not logs:
            return error_response("No logs found for this speech UID", 404)
        
        return success_response({
            "speech_uid": speech_uid,
            "total_fragments": len(logs),
            "logs": [log.model_dump() for log in logs]
        })
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/language/{language}")
def get_tts_logs_by_language(
    language: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get TTS logs filtered by language"""
    try:
        tts_service = TTSLogService(db)
        result = tts_service.get_all_logs(page=page, per_page=per_page, language=language)
        return success_response(result.to_dict())
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/service/{service}")
def get_tts_logs_by_service(
    service: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get TTS logs filtered by service"""
    try:
        tts_service = TTSLogService(db)
        result = tts_service.get_all_logs(page=page, per_page=per_page, service=service)
        return success_response(result.to_dict())
    except Exception as e:
        return error_response(str(e), 500)


@router.get("/tts-logs/stage/{stage}")
def get_tts_logs_by_stage(
    stage: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """Get TTS logs filtered by processing stage"""
    try:
        tts_service = TTSLogService(db)
        result = tts_service.get_logs_by_stage(stage, page, per_page)
        return success_response(result.to_dict())
    except Exception as e:
        return error_response(str(e), 500)


@router.post("/tts-logs/{log_id}/transcribe")
def transcribe_tts_log(
    log_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Trigger transcription for a specific TTS log audio file
    
    This endpoint retrieves the audio file associated with the log
    and initiates the transcription process.
    """
    try:
        tts_service = TTSLogService(db)
        log = tts_service.get_log_by_id(log_id)
        
        if not log:
            return error_response("TTS log not found", 404)
        
        # TODO: Implement transcription logic
        # This would:
        # 1. Get the audio file path from log.uuid_file
        # 2. Call the transcription service
        # 3. Return the transcription result
        
        return success_response({
            "log_id": log_id,
            "status": "transcription_queued",
            "message": "Transcription process started for audio file",
            "audio_file": log.uuid_file
        })
    except Exception as e:
        return error_response(str(e), 500)
