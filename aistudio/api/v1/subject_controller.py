"""
api/v1/subject_controller.py

Обрабатывает HTTP-запросы, связанные с субъектами.
Вызывает соответствующие методы из сервисов.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from aistudio.models.subject import Subject
from aistudio.schemas.subject_create import SubjectCreate
from aistudio.schemas.subject_update import SubjectUpdate
from aistudio.schemas.subject_out import SubjectOut
from aistudio.schemas.subject_filter import SubjectFilter
from aistudio.services.subject_service import SubjectService
from aistudio.dependencies.database import get_current_user
from aistudio.utils.role_checker import admin_required

router = APIRouter()


@router.post("/", response_model=SubjectOut)
def create_subject(
    subject_data: SubjectCreate,
    user=Depends(admin_required)
) -> SubjectOut:
    """
    Создает новый субъект.
    Только для админов.
    """
    try:
        service = SubjectService()
        
        # Валидация данных
        errors = service.validate_subject_data(
            subject_data.name,
            subject_data.type_id,
            subject_data.parent_id
        )
        if errors:
            raise HTTPException(status_code=400, detail="; ".join(errors))
        
        subject = service.create_subject(subject_data)
        return SubjectOut.model_validate(subject)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[SubjectOut])
def get_all_subjects(
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Получает все активные субъекты.
    Только для админов.
    """
    try:
        service = SubjectService()
        subjects = service.get_all_subjects()
        return [SubjectOut.model_validate(s) for s in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject_by_id(
    subject_id: int,
    user=Depends(admin_required)
) -> SubjectOut:
    """
    Получает субъект по ID.
    Только для админов.
    """
    try:
        service = SubjectService()
        subject = service.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return SubjectOut.model_validate(subject)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/type/{type_id}", response_model=List[SubjectOut])
def get_subjects_by_type(
    type_id: int,
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Получает все субъекты определенного типа.
    Только для админов.
    """
    try:
        service = SubjectService()
        subjects = service.get_subjects_by_type(type_id)
        return [SubjectOut.model_validate(s) for s in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/root/all", response_model=List[SubjectOut])
def get_root_subjects(
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Получает все корневые субъекты (без родителя).
    Только для админов.
    """
    try:
        service = SubjectService()
        subjects = service.get_root_subjects()
        return [SubjectOut.model_validate(s) for s in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{subject_id}/hierarchy", response_model=List[SubjectOut])
def get_subject_hierarchy(
    subject_id: int,
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Получает полную иерархию субъекта (все родители).
    Только для админов.
    """
    try:
        service = SubjectService()
        hierarchy = service.get_subject_hierarchy(subject_id)
        return [SubjectOut.model_validate(s) for s in hierarchy]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{subject_id}/children-tree", response_model=List[SubjectOut])
def get_subject_children_tree(
    subject_id: int,
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Получает дерево дочерних субъектов.
    Только для админов.
    """
    try:
        service = SubjectService()
        children = service.get_subject_children_tree(subject_id)
        return [SubjectOut.model_validate(s) for s in children]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search/name/{name}", response_model=List[SubjectOut])
def search_subjects_by_name(
    name: str,
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Поиск субъектов по названию.
    Только для админов.
    """
    try:
        service = SubjectService()
        subjects = service.search_subjects_by_name(name)
        return [SubjectOut.model_validate(s) for s in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    user=Depends(admin_required)
) -> SubjectOut:
    """
    Обновляет субъект.
    Только для админов.
    """
    try:
        service = SubjectService()
        
        # Валидация данных, если они предоставлены
        if subject_data.name is not None:
            errors = service.validate_subject_data(
                subject_data.name,
                subject_data.type_id or 0,
                subject_data.parent_id
            )
            if errors:
                raise HTTPException(status_code=400, detail="; ".join(errors))
        
        subject = service.update_subject(subject_id, subject_data)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return SubjectOut.model_validate(subject)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{subject_id}/move")
def move_subject(
    subject_id: int,
    new_parent_id: Optional[int] = Query(None),
    user=Depends(admin_required)
):
    """
    Перемещает субъект в другую ветку иерархии.
    Только для админов.
    """
    try:
        service = SubjectService()
        success = service.move_subject(subject_id, new_parent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Subject or new parent not found")
        
        return {"message": f"Subject {subject_id} moved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{subject_id}")
def soft_delete_subject(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Мягко удаляет субъект.
    Только для админов.
    """
    try:
        service = SubjectService()
        success = service.soft_delete_subject(subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return {"message": f"Subject {subject_id} has been soft deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{subject_id}/hard")
def hard_delete_subject(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Жестко удаляет субъект.
    Только для админов.
    """
    try:
        service = SubjectService()
        success = service.hard_delete_subject(subject_id)
        if not success:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return {"message": f"Subject {subject_id} has been hard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/filter", response_model=List[SubjectOut])
def filter_subjects(
    filter_data: SubjectFilter,
    user=Depends(admin_required)
) -> List[SubjectOut]:
    """
    Фильтрует субъекты по различным критериям.
    Только для админов.
    """
    try:
        service = SubjectService()
        subjects = service.filter_subjects(filter_data)
        return [SubjectOut.model_validate(s) for s in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{subject_id}/children-count")
def count_subject_children(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Подсчитывает количество дочерних субъектов.
    Только для админов.
    """
    try:
        service = SubjectService()
        count = service.count_subject_children(subject_id)
        return {"children_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{subject_id}/details")
def get_subject_with_details(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Получает субъект с дополнительной информацией.
    Только для админов.
    """
    try:
        service = SubjectService()
        details = service.get_subject_with_details(subject_id)
        if not details:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        return {
            "subject": SubjectOut.model_validate(details['subject']),
            "children_count": details['children_count'],
            "hierarchy": [SubjectOut.model_validate(s) for s in details['hierarchy']]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 