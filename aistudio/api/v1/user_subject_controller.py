"""
api/v1/user_subject_controller.py

Обрабатывает HTTP-запросы, связанные со связями пользователь-субъект.
Вызывает соответствующие методы из сервисов.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from aistudio.models.user_subject import UserSubject
from aistudio.schemas.user_subject_create import UserSubjectCreate
from aistudio.schemas.user_subject_update import UserSubjectUpdate
from aistudio.schemas.user_subject_out import UserSubjectOut
from aistudio.schemas.user_subject_filter import UserSubjectFilter
from aistudio.services.user_subject_service import UserSubjectService
from aistudio.dependencies.database import get_current_user
from aistudio.utils.role_checker import admin_required

router = APIRouter()


@router.post("/", response_model=UserSubjectOut)
def create_user_subject_connection(
    connection_data: UserSubjectCreate,
    user=Depends(admin_required)
) -> UserSubjectOut:
    """
    Создает новую связь пользователь-субъект.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        
        # Валидация данных
        errors = service.validate_connection_data(
            connection_data.user_id,
            connection_data.subject_id,
            connection_data.role_id
        )
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        
        connection = service.create_user_subject_connection(connection_data)
        return UserSubjectOut.model_validate(connection)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[UserSubjectOut])
def get_all_connections(
    user=Depends(admin_required)
) -> List[UserSubjectOut]:
    """
    Получает все активные связи пользователь-субъект.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connections = service.get_all_connections()
        return [UserSubjectOut.model_validate(c) for c in connections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}", response_model=List[UserSubjectOut])
def get_user_connections(
    user_id: int,
    user=Depends(admin_required)
) -> List[UserSubjectOut]:
    """
    Получает все связи пользователя.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connections = service.get_user_connections(user_id)
        return [UserSubjectOut.model_validate(c) for c in connections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/subject/{subject_id}", response_model=List[UserSubjectOut])
def get_subject_connections(
    subject_id: int,
    user=Depends(admin_required)
) -> List[UserSubjectOut]:
    """
    Получает все связи субъекта.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connections = service.get_subject_connections(subject_id)
        return [UserSubjectOut.model_validate(c) for c in connections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}/subject/{subject_id}", response_model=UserSubjectOut)
def get_user_subject_connection(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
) -> UserSubjectOut:
    """
    Получает связь пользователь-субъект.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connection = service.get_user_subject_connection(user_id, subject_id)
        if not connection:
            raise HTTPException(status_code=404, detail="UserSubject connection not found")
        return UserSubjectOut.model_validate(connection)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/user/{user_id}/subject/{subject_id}/role/{new_role_id}")
def update_user_role_in_subject(
    user_id: int,
    subject_id: int,
    new_role_id: int,
    user=Depends(admin_required)
):
    """
    Обновляет роль пользователя в субъекте.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connection = service.update_user_role_in_subject(user_id, subject_id, new_role_id)
        if not connection:
            raise HTTPException(status_code=404, detail="UserSubject connection not found")
        
        return {"message": f"Role updated successfully for user {user_id} in subject {subject_id}"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/assign")
def assign_user_to_subject(
    user_id: int = Query(...),
    subject_id: int = Query(...),
    role_id: int = Query(...),
    user=Depends(admin_required)
):
    """
    Назначает пользователя к субъекту с определенной ролью.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        
        # Валидация данных
        errors = service.validate_connection_data(user_id, subject_id, role_id)
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        
        connection = service.assign_user_to_subject(user_id, subject_id, role_id)
        return {
            "message": f"User {user_id} assigned to subject {subject_id} with role {role_id}",
            "connection": UserSubjectOut.model_validate(connection)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/user/{user_id}/subject/{subject_id}")
def remove_user_from_subject(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Удаляет пользователя из субъекта.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        success = service.remove_user_from_subject(user_id, subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="UserSubject connection not found")
        
        return {"message": f"User {user_id} removed from subject {subject_id} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/user/{user_id}/subject/{subject_id}/soft")
def soft_delete_connection(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Мягко удаляет связь пользователь-субъект.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        success = service.soft_delete_connection(user_id, subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="UserSubject connection not found")
        
        return {"message": f"UserSubject connection {user_id}-{subject_id} has been soft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/user/{user_id}/subject/{subject_id}/hard")
def hard_delete_connection(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Жестко удаляет связь пользователь-субъект.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        success = service.hard_delete_connection(user_id, subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="UserSubject connection not found")
        
        return {"message": f"UserSubject connection {user_id}-{subject_id} has been hard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/filter", response_model=List[UserSubjectOut])
def filter_connections(
    filter_data: UserSubjectFilter,
    user=Depends(admin_required)
) -> List[UserSubjectOut]:
    """
    Фильтрует связи по различным критериям.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        connections = service.filter_connections(filter_data)
        return [UserSubjectOut.model_validate(c) for c in connections]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/subject/{subject_id}/users")
def get_users_for_subject(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Получает список пользователей для субъекта.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        user_ids = service.get_users_for_subject(subject_id)
        return {"user_ids": user_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}/subjects")
def get_subjects_for_user(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Получает список субъектов для пользователя.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        subject_ids = service.get_subjects_for_user(user_id)
        return {"subject_ids": subject_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}/subject/{subject_id}/access")
def check_user_access(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Проверяет доступ пользователя к субъекту и возвращает роль.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        role = service.check_user_access(user_id, subject_id)
        return {"has_access": role is not None, "role": role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}/subject/{subject_id}/role")
def get_user_role_in_subject(
    user_id: int,
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Получает роль пользователя в субъекте.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        role_id = service.get_user_role_in_subject(user_id, subject_id)
        return {"role_id": role_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/subject/{subject_id}/users-with-roles")
def get_subject_users_with_roles(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Получает пользователей субъекта с их ролями.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        users_with_roles = service.get_subject_users_with_roles(subject_id)
        return {"users_with_roles": users_with_roles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/user/{user_id}/all-connections")
def delete_user_connections(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Удаляет все связи пользователя.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        count = service.delete_user_connections(user_id)
        return {"message": f"Deleted {count} connections for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/subject/{subject_id}/all-connections")
def delete_subject_connections(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Удаляет все связи субъекта.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        count = service.delete_subject_connections(subject_id)
        return {"message": f"Deleted {count} connections for subject {subject_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/user/{user_id}/subjects-with-details")
def get_user_subjects_with_details(
    user_id: int,
    user=Depends(admin_required)
):
    """
    Получает субъекты пользователя с дополнительной информацией.
    Только для админов.
    """
    try:
        service = UserSubjectService()
        details = service.get_user_subjects_with_details(user_id)
        return {"user_subjects_with_details": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 