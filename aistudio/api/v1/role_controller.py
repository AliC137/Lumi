"""
api/v1/role_controller.py

Обрабатывает HTTP-запросы, связанные с ролями.
Вызывает соответствующие методы из сервисов.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from aistudio.models.role import Role
from aistudio.schemas.role_create import RoleCreate
from aistudio.schemas.role_update import RoleUpdate
from aistudio.schemas.role_out import RoleOut
from aistudio.services.role_service import RoleService
from aistudio.dependencies.database import get_current_user
from aistudio.utils.role_checker import admin_required

router = APIRouter()


@router.post("/", response_model=RoleOut)
def create_role(
    role_data: RoleCreate,
    user=Depends(admin_required)
) -> RoleOut:
    """
    Создает новую роль.
    Только для админов.
    """
    try:
        service = RoleService()
        
        # Валидация данных
        errors = service.validate_role_data(role_data.name, role_data.slug)
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        
        role = service.create_role(role_data)
        return RoleOut.model_validate(role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[RoleOut])
def get_all_roles(
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Получает все активные роли.
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.get_all_roles()
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{role_id}", response_model=RoleOut)
def get_role_by_id(
    role_id: int,
    user=Depends(admin_required)
) -> RoleOut:
    """
    Получает роль по ID.
    Только для админов.
    """
    try:
        service = RoleService()
        role = service.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleOut.model_validate(role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/slug/{slug}", response_model=RoleOut)
def get_role_by_slug(
    slug: str,
    user=Depends(admin_required)
) -> RoleOut:
    """
    Получает роль по slug.
    Только для админов.
    """
    try:
        service = RoleService()
        role = service.get_role_by_slug(slug)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleOut.model_validate(role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    user=Depends(admin_required)
) -> RoleOut:
    """
    Обновляет роль.
    Только для админов.
    """
    try:
        service = RoleService()
        
        # Валидация данных, если они предоставлены
        if role_data.name is not None or role_data.slug is not None:
            name = role_data.name or ""
            slug = role_data.slug or ""
            errors = service.validate_role_data(name, slug)
            if errors:
                raise HTTPException(status_code=400, detail="; ".join(errors))
        
        role = service.update_role(role_id, role_data)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return RoleOut.model_validate(role)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{role_id}")
def soft_delete_role(
    role_id: int,
    user=Depends(admin_required)
):
    """
    Мягко удаляет роль.
    Только для админов.
    """
    try:
        service = RoleService()
        success = service.soft_delete_role(role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return {"message": f"Role {role_id} has been soft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{role_id}/hard")
def hard_delete_role(
    role_id: int,
    user=Depends(admin_required)
):
    """
    Жестко удаляет роль.
    Только для админов.
    """
    try:
        service = RoleService()
        success = service.hard_delete_role(role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return {"message": f"Role {role_id} has been hard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/default/all", response_model=List[RoleOut])
def get_default_roles(
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Получает стандартные роли (owner, editor, viewer).
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.get_default_roles()
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/default/create", response_model=List[RoleOut])
def create_default_roles(
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Создает стандартные роли, если они не существуют.
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.create_default_roles()
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/by-slugs/")
def get_roles_by_slugs(
    slugs: List[str] = Query(...),
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Получает роли по списку slug.
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.get_roles_by_slugs(slugs)
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/by-ids/")
def get_roles_by_ids(
    role_ids: List[int] = Query(...),
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Получает роли по списку ID.
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.get_roles_by_ids(role_ids)
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/name/{name}", response_model=RoleOut)
def get_role_by_name(
    name: str,
    user=Depends(admin_required)
) -> RoleOut:
    """
    Получает роль по названию.
    Только для админов.
    """
    try:
        service = RoleService()
        role = service.get_role_by_name(name)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleOut.model_validate(role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ensure-defaults", response_model=List[RoleOut])
def ensure_default_roles_exist(
    user=Depends(admin_required)
) -> List[RoleOut]:
    """
    Убеждается, что стандартные роли существуют.
    Создает их, если они отсутствуют.
    Только для админов.
    """
    try:
        service = RoleService()
        roles = service.ensure_default_roles_exist()
        return [RoleOut.model_validate(r) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/exists/{role_id}")
def check_role_exists(
    role_id: int,
    user=Depends(admin_required)
):
    """
    Проверяет существование роли.
    Только для админов.
    """
    try:
        service = RoleService()
        exists = service.exists_role(role_id)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 