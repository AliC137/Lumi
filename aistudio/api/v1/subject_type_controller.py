"""
api/v1/subject_type_controller.py

Обрабатывает HTTP-запросы, связанные с типами субъектов.
Вызывает соответствующие методы из сервисов.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from aistudio.models.subject_type import SubjectType
from aistudio.schemas.subject_type_create import SubjectTypeCreate
from aistudio.schemas.subject_type_update import SubjectTypeUpdate
from aistudio.schemas.subject_type_out import SubjectTypeOut
from aistudio.services.subject_type_service import SubjectTypeService
from aistudio.dependencies.database import get_current_user
from aistudio.utils.role_checker import admin_required

router = APIRouter()


@router.post("/", response_model=SubjectTypeOut)
def create_subject_type(
    subject_type_data: SubjectTypeCreate,
    user=Depends(admin_required)
) -> SubjectTypeOut:
    """
    Создает новый тип субъекта.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        
        # Валидация данных
        errors = service.validate_subject_type_data(
            subject_type_data.name, 
            subject_type_data.slug
        )
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        
        subject_type = service.create_subject_type(subject_type_data)
        return SubjectTypeOut.model_validate(subject_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[SubjectTypeOut])
def get_all_subject_types(
    user=Depends(admin_required)
) -> List[SubjectTypeOut]:
    """
    Получает все активные типы субъектов.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        subject_types = service.get_all_subject_types()
        return [SubjectTypeOut.model_validate(st) for st in subject_types]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{type_id}", response_model=SubjectTypeOut)
def get_subject_type_by_id(
    type_id: int,
    user=Depends(admin_required)
) -> SubjectTypeOut:
    """
    Получает тип субъекта по ID.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        subject_type = service.get_subject_type_by_id(type_id)
        if not subject_type:
            raise HTTPException(status_code=404, detail="SubjectType not found")
        return SubjectTypeOut.model_validate(subject_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/slug/{slug}", response_model=SubjectTypeOut)
def get_subject_type_by_slug(
    slug: str,
    user=Depends(admin_required)
) -> SubjectTypeOut:
    """
    Получает тип субъекта по slug.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        subject_type = service.get_subject_type_by_slug(slug)
        if not subject_type:
            raise HTTPException(status_code=404, detail="SubjectType not found")
        return SubjectTypeOut.model_validate(subject_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{type_id}", response_model=SubjectTypeOut)
def update_subject_type(
    type_id: int,
    subject_type_data: SubjectTypeUpdate,
    user=Depends(admin_required)
) -> SubjectTypeOut:
    """
    Обновляет тип субъекта.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        
        # Валидация данных, если они предоставлены
        if subject_type_data.name is not None or subject_type_data.slug is not None:
            name = subject_type_data.name or ""
            slug = subject_type_data.slug or ""
            errors = service.validate_subject_type_data(name, slug)
            if errors:
                raise HTTPException(status_code=400, detail="; ".join(errors))
        
        subject_type = service.update_subject_type(type_id, subject_type_data)
        if not subject_type:
            raise HTTPException(status_code=404, detail="SubjectType not found")
        
        return SubjectTypeOut.model_validate(subject_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{type_id}")
def soft_delete_subject_type(
    type_id: int,
    user=Depends(admin_required)
):
    """
    Мягко удаляет тип субъекта.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        success = service.soft_delete_subject_type(type_id)
        if not success:
            raise HTTPException(status_code=404, detail="SubjectType not found")
        
        return {"message": f"SubjectType {type_id} has been soft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{type_id}/hard")
def hard_delete_subject_type(
    type_id: int,
    user=Depends(admin_required)
):
    """
    Жестко удаляет тип субъекта.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        success = service.hard_delete_subject_type(type_id)
        if not success:
            raise HTTPException(status_code=404, detail="SubjectType not found")
        
        return {"message": f"SubjectType {type_id} has been hard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/exists/{type_id}")
def check_subject_type_exists(
    type_id: int,
    user=Depends(admin_required)
):
    """
    Проверяет существование типа субъекта.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        exists = service.exists_subject_type(type_id)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/by-ids/")
def get_subject_types_by_ids(
    type_ids: List[int] = Query(...),
    user=Depends(admin_required)
) -> List[SubjectTypeOut]:
    """
    Получает типы субъектов по списку ID.
    Только для админов.
    """
    try:
        service = SubjectTypeService()
        subject_types = service.get_subject_types_by_ids(type_ids)
        return [SubjectTypeOut.model_validate(st) for st in subject_types]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 