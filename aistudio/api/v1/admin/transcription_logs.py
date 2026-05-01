from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from aistudio.dependencies.database import get_db
from aistudio.services.transcription_log_service import TranscriptionLogService
from aistudio.schemas.transcription_log_out import (
    TranscriptionLogOut,
    TranscriptionLogUpdate,
    TranscriptionLogStats
)
from aistudio.utils.role_checker import admin_required


router = APIRouter()


def success_response(data, message: str = "Success", code: int = 200):
    """Helper for eKhonish success response format"""
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str, code: int = 400):
    """Helper for eKhonish error response format"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": None
    }


@router.get("/transcription-logs/stats")
def get_transcription_statistics(
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription statistics
    
    Returns comprehensive statistics about all transcription logs including:
    - Total transcriptions
    - Count by language (ru/tg)
    - Count by service (vosk/yandex)
    - Count by processing stage
    - Number of corrected transcriptions
    - Average text length
    - Recent transcriptions
    """
    service = TranscriptionLogService(db)
    stats = service.get_statistics()
    return success_response(
        data=stats.model_dump(),
        message="Transcription statistics retrieved successfully"
    )


@router.get("/transcription-logs")
def get_all_transcription_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get all transcription logs with pagination
    
    Returns paginated list of all transcription logs with metadata:
    - data: List of transcription logs
    - meta: Pagination metadata (current_page, last_page, per_page, total)
    """
    service = TranscriptionLogService(db)
    result = service.get_all_logs(page=page, per_page=per_page)
    return success_response(
        data={
            "data": [log.model_dump() for log in result.data],
            "meta": result.meta
        },
        message=f"Retrieved {len(result.data)} transcription logs"
    )


@router.get("/transcription-logs/uncorrected")
def get_uncorrected_transcription_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription logs without corrections
    
    Returns paginated transcription logs that haven't been corrected yet
    """
    service = TranscriptionLogService(db)
    result = service.get_uncorrected_logs(page=page, per_page=per_page)
    
    return success_response(
        data={
            "data": [log.model_dump() for log in result.data],
            "meta": result.meta
        },
        message=f"Retrieved {len(result.data)} uncorrected transcription logs"
    )


@router.get("/transcription-logs/{log_id}")
def get_transcription_log_by_id(
    log_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription log by ID
    
    Returns a single transcription log entry by its ID
    """
    service = TranscriptionLogService(db)
    log = service.get_log_by_id(log_id)
    
    if not log:
        return error_response(
            message=f"Transcription log with ID {log_id} not found",
            code=404
        )
    
    return success_response(
        data=log.model_dump(),
        message="Transcription log retrieved successfully"
    )


@router.get("/transcription-logs/file/{file_uuid}")
def get_transcription_logs_by_file_uuid(
    file_uuid: str,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get all transcription logs for a specific audio file
    
    Returns all transcription attempts for a given file UUID
    """
    service = TranscriptionLogService(db)
    logs = service.get_logs_by_file_uuid(file_uuid)
    
    return success_response(
        data=[log.model_dump() for log in logs],
        message=f"Retrieved {len(logs)} transcription logs for file {file_uuid}"
    )


@router.get("/transcription-logs/language/{lang}")
def get_transcription_logs_by_language(
    lang: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription logs by language with pagination
    
    Returns paginated transcription logs filtered by language (ru/tg)
    """
    service = TranscriptionLogService(db)
    result = service.get_logs_by_language(lang=lang, page=page, per_page=per_page)
    
    return success_response(
        data={
            "data": [log.model_dump() for log in result.data],
            "meta": result.meta
        },
        message=f"Retrieved {len(result.data)} transcription logs for language '{lang}'"
    )


@router.get("/transcription-logs/service/{service_name}")
def get_transcription_logs_by_service(
    service_name: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription logs by service with pagination
    
    Returns paginated transcription logs filtered by service (vosk/yandex)
    """
    service = TranscriptionLogService(db)
    result = service.get_logs_by_service(service=service_name, page=page, per_page=per_page)
    
    return success_response(
        data={
            "data": [log.model_dump() for log in result.data],
            "meta": result.meta
        },
        message=f"Retrieved {len(result.data)} transcription logs for service '{service_name}'"
    )


@router.get("/transcription-logs/stage/{stage}")
def get_transcription_logs_by_stage(
    stage: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Get transcription logs by processing stage with pagination
    
    Returns paginated transcription logs filtered by processing stage
    """
    service = TranscriptionLogService(db)
    result = service.get_logs_by_stage(stage=stage, page=page, per_page=per_page)
    
    return success_response(
        data={
            "data": [log.model_dump() for log in result.data],
            "meta": result.meta
        },
        message=f"Retrieved {len(result.data)} transcription logs for stage {stage}"
    )


@router.put("/transcription-logs/{log_id}/correct")
def update_transcription_correction(
    log_id: int,
    correction: TranscriptionLogUpdate,
    db: Session = Depends(get_db),
    user=Depends(admin_required)
):
    """
    Update the corrected text for a transcription log
    
    Allows admin to provide corrected/verified text for a transcription
    """
    service = TranscriptionLogService(db)
    updated_log = service.update_correction(log_id, correction.correct_text)
    
    if not updated_log:
        return error_response(
            message=f"Transcription log with ID {log_id} not found",
            code=404
        )
    
    return success_response(
        data=updated_log.model_dump(),
        message="Transcription correction updated successfully"
    )
