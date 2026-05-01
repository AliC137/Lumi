"""
api/v1/admin/users.py

Admin endpoints for user management (CRUD operations).
All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from aistudio.api.v1.admin.schemas import PaginatedResponse
from aistudio.schemas.user_create import UserCreate
from aistudio.schemas.user_update import UserUpdate
from aistudio.schemas.user_out import UserOut, UserDetailOut
from aistudio.models.user import User
from aistudio.repositories import RepositoryFactory
from aistudio.utils.role_checker import admin_required
from aistudio.utils.security import hash_password
from math import ceil

router = APIRouter()


class PaginatedUserResponse(PaginatedResponse):
    """Paginated response for users list"""
    items: List[UserOut]


@router.get("", response_model=PaginatedUserResponse)
def get_all_users(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    role: Optional[str] = Query(None, description="Filter by role (user/admin)"),
    search: Optional[str] = Query(None, description="Search by name or login"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    sort_by: str = Query("created_dt", description="Sort field (created_dt, name, login)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    user=Depends(admin_required)
):
    """
    Get all users with pagination, filtering, and sorting.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Build query
        query = repo.db.query(User)
        
        # Filter by deleted status
        if not include_deleted:
            query = query.filter(User.deleted_dt.is_(None))
        
        # Filter by role
        if role:
            query = query.filter(User.role == role)
        
        # Search by name or login
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.login.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort_by == "name":
            sort_column = User.name
        elif sort_by == "login":
            sort_column = User.login
        elif sort_by == "created_dt":
            sort_column = User.created_dt
        else:
            sort_column = User.created_dt
        
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = ceil(total / limit) if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        return PaginatedUserResponse(
            items=[UserOut.model_validate(u) for u in users],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    finally:
        repo.db.close()


@router.get("/summary/overview")
def get_users_summary(user=Depends(admin_required)):
    """
    Get a quick summary overview of all users.
    Returns counts and basic statistics.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        from datetime import datetime, timedelta
        
        # Get all active users
        all_users = repo.db.query(User).filter(User.deleted_dt.is_(None)).all()
        
        total = len(all_users)
        active = sum(1 for u in all_users if u.is_active)
        inactive = sum(1 for u in all_users if not u.is_active)
        admins = sum(1 for u in all_users if u.role == "admin")
        regular = sum(1 for u in all_users if u.role == "user")
        
        # Get deleted users count
        deleted = repo.db.query(User).filter(User.deleted_dt.isnot(None)).count()
        
        # Calculate average account age
        if all_users:
            now = datetime.now()
            ages = [(now - u.created_dt).days for u in all_users if u.created_dt]
            avg_age = sum(ages) / len(ages) if ages else 0
        else:
            avg_age = 0
        
        return {
            "total_users": total,
            "active_users": active,
            "inactive_users": inactive,
            "admin_users": admins,
            "regular_users": regular,
            "deleted_users": deleted,
            "average_account_age_days": round(avg_age, 1)
        }
    finally:
        repo.db.close()


@router.get("/{user_id}", response_model=UserDetailOut)
def get_user_by_id(
    user_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
    user=Depends(admin_required)
):
    """
    Get detailed user information by ID.
    Returns extended user data including computed fields.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        if include_deleted:
            # Get user including deleted ones
            db_user = repo.db.query(User).filter(User.id == user_id).first()
        else:
            # Get only active user
            db_user = repo.get_by_id(user_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserDetailOut.from_user(db_user)
    finally:
        repo.db.close()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    role: str = Query("user", description="User role (user/admin)"),
    user=Depends(admin_required)
):
    """
    Create a new user.
    Only accessible by admins.
    """
    # Validate role
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Allowed roles: user, admin"
        )
    
    repo = RepositoryFactory.get_user_repository()
    try:
        # Check if user with this login already exists
        existing_user = repo.get_by_login(user_data.login)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this login already exists"
            )
        
        # Create user
        new_user = repo.create(
            login=user_data.login,
            name=user_data.name,
            password=user_data.password,
            role=role
        )
        
        return UserOut.model_validate(new_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    finally:
        repo.db.close()


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    user=Depends(admin_required)
):
    """
    Update user information.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Get user (including deleted ones for update)
        db_user = repo.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Prepare update data
        update_data = {}
        
        if user_data.login is not None:
            # Check if login is already taken by another user
            existing_user = repo.get_by_login(user_data.login)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this login already exists"
                )
            update_data['login'] = user_data.login
        
        if user_data.name is not None:
            update_data['name'] = user_data.name
        
        if user_data.password is not None:
            update_data['password'] = hash_password(user_data.password)
        
        if user_data.role is not None:
            if user_data.role not in ["user", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role. Allowed roles: user, admin"
                )
            update_data['role'] = user_data.role
        
        # Update user
        updated_user = repo.update_user(user_id, **update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserOut.model_validate(updated_user)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    finally:
        repo.db.close()


@router.patch("/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: int,
    is_active: bool,
    user=Depends(admin_required)
):
    """
    Update user active status (activate or deactivate user).
    When deactivated, user cannot login.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Get user
        db_user = repo.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Update status
        db_user.is_active = is_active
        repo.db.commit()
        repo.db.refresh(db_user)
        
        status_text = "activated" if is_active else "deactivated"
        return UserOut.model_validate(db_user)
    
    except HTTPException:
        raise
    except Exception as e:
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )
    finally:
        repo.db.close()


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    role: str,
    user=Depends(admin_required)
):
    """
    Update user role (change between 'user' and 'admin').
    Safety check: Prevents admin from demoting themselves.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Validate role
        if role not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Allowed roles: 'user', 'admin'"
            )
        
        # Get target user
        db_user = repo.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Safety check: Prevent admin from demoting themselves
        current_user_id = user.get('user_id')
        if current_user_id == user_id and role == "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot demote yourself from admin role. Ask another admin to change your role."
            )
        
        # Update role
        db_user.role = role
        repo.db.commit()
        repo.db.refresh(db_user)
        
        return UserOut.model_validate(db_user)
    
    except HTTPException:
        raise
    except Exception as e:
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )
    finally:
        repo.db.close()


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def soft_delete_user(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Soft delete user (sets deleted_dt).
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        success = repo.soft_delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found or already deleted"
            )
        
        return {"message": f"User {user_id} has been soft deleted successfully"}
    except HTTPException:
        raise
    finally:
        repo.db.close()


@router.delete("/{user_id}/hard", status_code=status.HTTP_200_OK)
def hard_delete_user(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Hard delete user (permanently removes from database).
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Get user including deleted ones
        db_user = repo.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Hard delete
        repo.db.delete(db_user)
        repo.db.commit()
        
        return {"message": f"User {user_id} has been permanently deleted"}
    except HTTPException:
        raise
    except Exception as e:
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
    finally:
        repo.db.close()


@router.post("/{user_id}/restore", response_model=UserOut, status_code=status.HTTP_200_OK)
def restore_user(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Restore a soft-deleted user.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_user_repository()
    try:
        # Get user including deleted ones
        db_user = repo.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Check if user is actually deleted
        if db_user.deleted_dt is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is not deleted"
            )
        
        # Restore user
        db_user.deleted_dt = None
        repo.db.commit()
        repo.db.refresh(db_user)
        
        return UserOut.model_validate(db_user)
    except HTTPException:
        raise
    except Exception as e:
        repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring user: {str(e)}"
        )
    finally:
        repo.db.close()

