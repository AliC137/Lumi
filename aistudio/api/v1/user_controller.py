"""
v1/user_controller.py

Обрабатывает HTTP-запросы, связанные с пользователями.
Вызывает соответствующие методы из сервисов.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from aistudio.models.user import User
from aistudio.schemas.user_create import UserCreate
from aistudio.schemas.user_out import UserOut
from aistudio.schemas.user_login import UserLogin
from aistudio.schemas.refresh_token import RefreshTokenRequest, TokenResponse
from aistudio.schemas.role_change import RoleChangeRequest
from aistudio.services.user_service import UserService
from aistudio.dependencies.database import get_current_user
from aistudio.utils.jwt_utils import create_access_token
from aistudio.utils.role_checker import admin_required, user_or_admin_required

router = APIRouter()
security = HTTPBearer()

@router.get("/", response_model=List[UserOut])
def get_all_users(user=Depends(admin_required)) -> List[User]:
    """
    Get all active users (excluding soft-deleted users).
    Только для админов.
    """
    service = UserService()
    return service.get_all_users()

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user=Depends(get_current_user)) -> UserOut:
    """
    Get current authenticated user information.
    This endpoint is used for user authentication pages to fetch logged-in user details.
    IMPORTANT: Must be defined BEFORE /{user_id} to avoid route conflicts.
    """
    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: user_id not found"
            )
        
        service = UserService()
        user = service.get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, user=Depends(user_or_admin_required)) -> UserOut:
    """
    Get user by ID. 
    - Users can get only their own data
    - Admins can get any user data
    """
    try:
        service = UserService()
        return service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate) -> UserOut:
    """
    Register a new user. Validates required fields and uniqueness of login (email).
    """
    try:
        service = UserService()
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(user: UserLogin):
    """
    Login user and return access and refresh tokens.
    """
    service = UserService()
    auth_user = service.authenticate_user(user.login, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    
    # Check if user is active
    if not auth_user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated. Please contact support.")
    
    # Update last login timestamp
    service.update_last_login(auth_user.id)
    
    # Создаем токены и сохраняем в БД
    tokens = service.create_user_tokens(auth_user)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(refresh_request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    service = UserService()
    tokens = service.refresh_user_tokens(refresh_request.refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return tokens

@router.post("/logout")
def logout(current_user=Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user by invalidating the current token.
    Requires valid Bearer token in Authorization header.
    """
    access_token = credentials.credentials
    service = UserService()
    
    success = service.logout_user(access_token)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"message": "Successfully logged out"}

@router.delete("/{user_id}")
def soft_delete_user(user_id: int, user=Depends(user_or_admin_required)):
    """
    Soft delete user by ID. Sets deleted_dt to current timestamp.
    - Users can delete only themselves
    - Admins can delete any user
    """
    try:
        service = UserService()
        service.soft_delete_user(user_id)
        return {"message": f"User {user_id} has been soft deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}/role", response_model=UserOut)
def change_user_role(user_id: int, role_data: RoleChangeRequest, user=Depends(admin_required)):
    """
    Изменяет роль пользователя. Только для админов.
    """
    try:
        service = UserService()
        return service.change_user_role(user_id, role_data.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
