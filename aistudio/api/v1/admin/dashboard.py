"""
api/v1/admin/dashboard.py

Admin dashboard endpoints for statistics and metrics.
All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from aistudio.models.user import User
from aistudio.repositories import RepositoryFactory
from aistudio.utils.role_checker import admin_required
from pydantic import BaseModel


router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics response model"""
    total_users: int
    admin_users: int
    regular_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    active_users: int  # Users without deleted_dt


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(user=Depends(admin_required)):
    """
    Get dashboard statistics including user counts and growth metrics.
    Only accessible by admins.
    
    Returns:
    - total_users: Total number of users (excluding deleted)
    - admin_users: Number of admin users
    - regular_users: Number of regular users
    - new_users_today: Users created today
    - new_users_this_week: Users created in the last 7 days
    - new_users_this_month: Users created in the last 30 days
    - active_users: Users that are not soft-deleted
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate date ranges
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Base query for active users (not deleted)
        active_users_query = repo.db.query(User).filter(User.deleted_dt.is_(None))
        
        # Total active users
        total_users = active_users_query.count()
        
        # Count by role
        admin_users = active_users_query.filter(User.role == "admin").count()
        regular_users = active_users_query.filter(User.role == "user").count()
        
        # New users today
        new_users_today = active_users_query.filter(
            User.created_dt >= today_start
        ).count()
        
        # New users this week
        new_users_this_week = active_users_query.filter(
            User.created_dt >= week_ago
        ).count()
        
        # New users this month
        new_users_this_month = active_users_query.filter(
            User.created_dt >= month_ago
        ).count()
        
        return DashboardStats(
            total_users=total_users,
            admin_users=admin_users,
            regular_users=regular_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month,
            active_users=total_users
        )
    
    finally:
        repo.db.close()
