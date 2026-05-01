"""
api/v1/admin/admin_router.py

Main router for admin panel API endpoints.
All endpoints in this router require admin authentication.
"""

from fastapi import APIRouter
from aistudio.api.v1.admin.auth import router as auth_router
from aistudio.api.v1.admin.users import router as users_router
from aistudio.api.v1.admin.subjects import router as subjects_router
from aistudio.api.v1.admin.dashboard import router as dashboard_router
from aistudio.api.v1.admin.analytics import router as analytics_router
from aistudio.api.v1.admin.tts_logs import router as tts_logs_router
from aistudio.api.v1.admin.transcription_logs import router as transcription_logs_router

# Create the main admin router
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Admin access required"},
    }
)

# Include sub-routers
admin_router.include_router(auth_router)
admin_router.include_router(users_router, prefix="/users", tags=["Admin - Users"])
admin_router.include_router(subjects_router, prefix="/subjects", tags=["Admin - Subjects"])
admin_router.include_router(dashboard_router, prefix="/dashboard", tags=["Admin - Dashboard"])
admin_router.include_router(analytics_router, prefix="/analytics", tags=["Admin - Analytics"])
admin_router.include_router(tts_logs_router, tags=["Admin - TTS Logs"])
admin_router.include_router(transcription_logs_router, tags=["Admin - Transcription Logs"])

@admin_router.get("/")
def admin_root():
    """
    Root endpoint for admin panel API.
    Returns basic information about the admin API.
    """
    return {
        "message": "Admin Panel API",
        "version": "1.0.0",
        "description": "Admin panel endpoints for managing the system"
    }

