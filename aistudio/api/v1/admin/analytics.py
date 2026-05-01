"""
api/v1/admin/analytics.py

Admin analytics endpoints for tracking growth and activity metrics.
All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Literal
from sqlalchemy import func, and_, or_
from aistudio.models.user import User
from aistudio.repositories import RepositoryFactory
from aistudio.utils.role_checker import admin_required
from pydantic import BaseModel


router = APIRouter()


class GrowthDataPoint(BaseModel):
    """Single data point for growth analytics"""
    date: str
    count: int


class UserGrowthResponse(BaseModel):
    """User growth analytics response"""
    period: str
    total_new_users: int
    data_points: List[GrowthDataPoint]


@router.get("/user-growth", response_model=UserGrowthResponse)
def get_user_growth(
    period: Literal["7days", "30days", "90days", "1year"] = Query("30days", description="Time period for analytics"),
    user=Depends(admin_required)
):
    """
    Get user growth analytics showing day-by-day registration counts.
    
    Parameters:
    - period: Time period to analyze (7days, 30days, 90days, 1year)
    
    Returns day-by-day breakdown of new user registrations.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate date range based on period
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        
        if period == "7days":
            days = 7
            start_date = today_start - timedelta(days=6)  # Include today
        elif period == "30days":
            days = 30
            start_date = today_start - timedelta(days=29)
        elif period == "90days":
            days = 90
            start_date = today_start - timedelta(days=89)
        elif period == "1year":
            days = 365
            start_date = today_start - timedelta(days=364)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")
        
        # Get all users created in the period
        users = repo.db.query(User).filter(
            User.created_dt >= start_date,
            User.created_dt < today_start + timedelta(days=1)
        ).all()
        
        # Group by date
        date_counts = {}
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_counts[date_str] = 0
        
        # Count users per day
        for user in users:
            user_date = user.created_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = user_date.strftime("%Y-%m-%d")
            if date_str in date_counts:
                date_counts[date_str] += 1
        
        # Convert to response format
        data_points = [
            GrowthDataPoint(date=date, count=count)
            for date, count in sorted(date_counts.items())
        ]
        
        total_new_users = sum(dp.count for dp in data_points)
        
        return UserGrowthResponse(
            period=period,
            total_new_users=total_new_users,
            data_points=data_points
        )
    
    finally:
        repo.db.close()


class ActiveUsersResponse(BaseModel):
    """Response for active users analytics"""
    total_active: int
    active_today: int
    active_this_week: int
    active_this_month: int


@router.get("/active-users", response_model=ActiveUsersResponse)
def get_active_users(user=Depends(admin_required)):
    """
    Get statistics about recently active users based on last_login timestamp.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate date ranges
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Base query for active users (not deleted, is_active=True)
        active_users_query = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True
        )
        
        total_active = active_users_query.count()
        
        # Users who logged in today
        active_today = active_users_query.filter(
            User.last_login >= today_start
        ).count()
        
        # Users who logged in this week
        active_this_week = active_users_query.filter(
            User.last_login >= week_ago
        ).count()
        
        # Users who logged in this month
        active_this_month = active_users_query.filter(
            User.last_login >= month_ago
        ).count()
        
        return ActiveUsersResponse(
            total_active=total_active,
            active_today=active_today,
            active_this_week=active_this_week,
            active_this_month=active_this_month
        )
    
    finally:
        repo.db.close()


class RoleDistributionResponse(BaseModel):
    """Role distribution analytics"""
    admin_count: int
    user_count: int
    admin_percentage: float
    user_percentage: float


@router.get("/role-distribution", response_model=RoleDistributionResponse)
def get_role_distribution(user=Depends(admin_required)):
    """
    Get distribution of users by role.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Count active users by role
        active_users = repo.db.query(User).filter(User.deleted_dt.is_(None))
        
        admin_count = active_users.filter(User.role == "admin").count()
        user_count = active_users.filter(User.role == "user").count()
        total = admin_count + user_count
        
        admin_percentage = (admin_count / total * 100) if total > 0 else 0
        user_percentage = (user_count / total * 100) if total > 0 else 0
        
        return RoleDistributionResponse(
            admin_count=admin_count,
            user_count=user_count,
            admin_percentage=round(admin_percentage, 2),
            user_percentage=round(user_percentage, 2)
        )
    
    finally:
        repo.db.close()


class RecentLoginUser(BaseModel):
    """User with recent login information"""
    id: int
    login: str
    name: str
    role: str
    last_login: datetime
    minutes_since_login: int


class RecentlyActiveUsersResponse(BaseModel):
    """Response for recently active users list"""
    count: int
    users: List[RecentLoginUser]


@router.get("/recently-active", response_model=RecentlyActiveUsersResponse)
def get_recently_active_users(
    limit: int = Query(10, ge=1, le=50, description="Number of users to return"),
    user=Depends(admin_required)
):
    """
    Get list of recently active users ordered by last login.
    Shows users who have logged in, sorted by most recent first.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Get active users with last_login, ordered by most recent
        recent_users = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True,
            User.last_login.isnot(None)
        ).order_by(User.last_login.desc()).limit(limit).all()
        
        # Calculate minutes since login for each user
        now = datetime.now()
        users_data = []
        for u in recent_users:
            last_login = u.last_login
            if last_login.tzinfo is None:
                from datetime import timezone as tz
                last_login = last_login.replace(tzinfo=tz.utc)
                now_utc = datetime.now(tz.utc)
            else:
                now_utc = datetime.now(last_login.tzinfo)
            
            minutes_since = int((now_utc - last_login).total_seconds() / 60)
            
            users_data.append(RecentLoginUser(
                id=u.id,
                login=u.login,
                name=u.name,
                role=u.role,
                last_login=u.last_login,
                minutes_since_login=minutes_since
            ))
        
        return RecentlyActiveUsersResponse(
            count=len(users_data),
            users=users_data
        )
    
    finally:
        repo.db.close()


class UserEngagementMetrics(BaseModel):
    """User engagement and retention metrics"""
    total_users: int
    users_with_login: int
    users_without_login: int
    never_logged_in_percentage: float
    average_days_since_last_login: float


@router.get("/engagement", response_model=UserEngagementMetrics)
def get_user_engagement(user=Depends(admin_required)):
    """
    Get user engagement metrics including login statistics.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Get all active users
        all_users = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True
        ).all()
        
        total_users = len(all_users)
        users_with_login = sum(1 for u in all_users if u.last_login is not None)
        users_without_login = total_users - users_with_login
        
        never_logged_in_percentage = (users_without_login / total_users * 100) if total_users > 0 else 0
        
        # Calculate average days since last login for users who have logged in
        if users_with_login > 0:
            now = datetime.now()
            days_list = []
            for u in all_users:
                if u.last_login:
                    last_login = u.last_login
                    if last_login.tzinfo is None:
                        from datetime import timezone as tz
                        last_login = last_login.replace(tzinfo=tz.utc)
                        now_utc = datetime.now(tz.utc)
                    else:
                        now_utc = datetime.now(last_login.tzinfo)
                    days_since = (now_utc - last_login).days
                    days_list.append(days_since)
            
            average_days = sum(days_list) / len(days_list) if days_list else 0
        else:
            average_days = 0
        
        return UserEngagementMetrics(
            total_users=total_users,
            users_with_login=users_with_login,
            users_without_login=users_without_login,
            never_logged_in_percentage=round(never_logged_in_percentage, 2),
            average_days_since_last_login=round(average_days, 2)
        )
    
    finally:
        repo.db.close()


class UserRetentionData(BaseModel):
    """User retention data by time period"""
    period: str
    retained_users: int
    total_users: int
    retention_rate: float


@router.get("/retention", response_model=UserRetentionData)
def get_user_retention(
    period: Literal["7days", "30days", "90days"] = Query("30days", description="Retention period"),
    user=Depends(admin_required)
):
    """
    Calculate user retention rate for a given period.
    Shows how many users who were created before the period have logged in during the period.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate date range
        now = datetime.now()
        if period == "7days":
            days = 7
        elif period == "30days":
            days = 30
        elif period == "90days":
            days = 90
        else:
            days = 30
        
        period_start = now - timedelta(days=days)
        
        # Get users created before the period started
        users_before_period = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True,
            User.created_dt < period_start
        ).all()
        
        total_users = len(users_before_period)
        
        # Count how many of these users logged in during the period
        retained_users = sum(
            1 for u in users_before_period 
            if u.last_login and u.last_login >= period_start
        )
        
        retention_rate = (retained_users / total_users * 100) if total_users > 0 else 0
        
        return UserRetentionData(
            period=period,
            retained_users=retained_users,
            total_users=total_users,
            retention_rate=round(retention_rate, 2)
        )
    
    finally:
        repo.db.close()


class InactiveUsersResponse(BaseModel):
    """Response for inactive users list"""
    count: int
    inactive_users: List[dict]


@router.get("/inactive-users", response_model=InactiveUsersResponse)
def get_inactive_users(
    days: int = Query(30, ge=1, le=365, description="Days of inactivity"),
    limit: int = Query(10, ge=1, le=50, description="Number of users to return"),
    user=Depends(admin_required)
):
    """
    Get list of users who haven't logged in for a specified number of days.
    Useful for identifying disengaged users.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get users who either never logged in or haven't logged in since cutoff
        inactive = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True,
            or_(
                User.last_login.is_(None),
                User.last_login < cutoff_date
            )
        ).order_by(User.created_dt.desc()).limit(limit).all()
        
        inactive_list = []
        for u in inactive:
            days_inactive = None
            if u.last_login:
                last_login = u.last_login
                if last_login.tzinfo is None:
                    from datetime import timezone as tz
                    last_login = last_login.replace(tzinfo=tz.utc)
                    now_utc = datetime.now(tz.utc)
                else:
                    now_utc = datetime.now(last_login.tzinfo)
                days_inactive = (now_utc - last_login).days
            else:
                # Never logged in - show days since creation
                created = u.created_dt
                if created.tzinfo is None:
                    from datetime import timezone as tz
                    created = created.replace(tzinfo=tz.utc)
                    now_utc = datetime.now(tz.utc)
                else:
                    now_utc = datetime.now(created.tzinfo)
                days_inactive = (now_utc - created).days
            
            inactive_list.append({
                "id": u.id,
                "login": u.login,
                "name": u.name,
                "role": u.role,
                "last_login": u.last_login,
                "days_inactive": days_inactive,
                "never_logged_in": u.last_login is None
            })
        
        return InactiveUsersResponse(
            count=len(inactive_list),
            inactive_users=inactive_list
        )
    
    finally:
        repo.db.close()


class OverviewStats(BaseModel):
    """Comprehensive overview statistics"""
    total_users: int
    active_today: int
    active_this_week: int
    active_this_month: int
    new_users_this_week: int
    new_users_this_month: int
    admin_count: int
    user_count: int
    inactive_30days: int
    never_logged_in: int


@router.get("/overview", response_model=OverviewStats)
def get_analytics_overview(user=Depends(admin_required)):
    """
    Get comprehensive analytics overview with all key metrics in one call.
    Optimized for dashboard homepage.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    
    try:
        # Calculate date ranges
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Get all active users
        all_users = repo.db.query(User).filter(
            User.deleted_dt.is_(None),
            User.is_active == True
        ).all()
        
        total_users = len(all_users)
        
        # Activity metrics
        active_today = sum(1 for u in all_users if u.last_login and u.last_login >= today_start)
        active_this_week = sum(1 for u in all_users if u.last_login and u.last_login >= week_ago)
        active_this_month = sum(1 for u in all_users if u.last_login and u.last_login >= month_ago)
        
        # New users
        new_users_this_week = sum(1 for u in all_users if u.created_dt >= week_ago)
        new_users_this_month = sum(1 for u in all_users if u.created_dt >= month_ago)
        
        # Role distribution
        admin_count = sum(1 for u in all_users if u.role == "admin")
        user_count = sum(1 for u in all_users if u.role == "user")
        
        # Inactivity
        inactive_30days = sum(
            1 for u in all_users 
            if u.last_login is None or u.last_login < month_ago
        )
        never_logged_in = sum(1 for u in all_users if u.last_login is None)
        
        return OverviewStats(
            total_users=total_users,
            active_today=active_today,
            active_this_week=active_this_week,
            active_this_month=active_this_month,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month,
            admin_count=admin_count,
            user_count=user_count,
            inactive_30days=inactive_30days,
            never_logged_in=never_logged_in
        )
    
    finally:
        repo.db.close()
