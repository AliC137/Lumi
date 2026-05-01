from fastapi import Depends, HTTPException, status, Path
from aistudio.dependencies.database import get_current_user
from typing import List, Optional

class RoleChecker:
    """Базовый класс для проверки ролей без user_id"""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user=Depends(get_current_user)):
        user_role = user.get('role')
        
        # Проверяем роль
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {self.allowed_roles}"
            )
        
        return user

class RoleCheckerWithUserId:
    """Класс для проверки ролей с user_id (для эндпоинтов с параметром user_id)"""
    def __init__(self, allowed_roles: List[str], allow_self_access: bool = False):
        self.allowed_roles = allowed_roles
        self.allow_self_access = allow_self_access

    def __call__(self, user=Depends(get_current_user), user_id: int = Path(...)):
        user_role = user.get('role')
        current_user_id = user.get('user_id')
        
        # Проверяем роль
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {self.allowed_roles}"
            )
        
        # Если разрешен доступ к своим данным и пользователь запрашивает свои данные
        if self.allow_self_access and current_user_id == user_id:
            return user
            
        # Админ может получить любого пользователя
        if user_role == 'admin':
            return user
            
        # Обычный пользователь не может получить данные другого пользователя
        if user_role == 'user' and self.allow_self_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own data"
            )
        
        return user

# Предопределенные проверки для эндпоинтов БЕЗ user_id
admin_required = RoleChecker(["admin"])
user_required = RoleChecker(["user"])
user_or_admin_required_simple = RoleChecker(["user", "admin"])

# Предопределенные проверки для эндпоинтов С user_id
admin_required_with_id = RoleCheckerWithUserId(["admin"])
user_or_admin_required = RoleCheckerWithUserId(["user", "admin"], allow_self_access=True) 