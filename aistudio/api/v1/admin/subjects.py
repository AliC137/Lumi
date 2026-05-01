"""
api/v1/admin/subjects.py

Admin endpoints for subject management (CRUD operations).
All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy import or_
from math import ceil

from aistudio.api.v1.admin.schemas import PaginatedResponse
from aistudio.schemas.subject_create import SubjectCreate
from aistudio.schemas.subject_update import SubjectUpdate
from aistudio.schemas.subject_out import SubjectOut
from aistudio.models.subject import Subject
from aistudio.repositories import RepositoryFactory
from aistudio.services.subject_service import SubjectService
from aistudio.utils.role_checker import admin_required

router = APIRouter()


class PaginatedSubjectResponse(PaginatedResponse):
    """Paginated response for subjects list"""
    items: List[SubjectOut]


@router.get("", response_model=PaginatedSubjectResponse)
def get_all_subjects(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    type_id: Optional[int] = Query(None, description="Filter by subject type ID"),
    parent_id: Optional[int] = Query(None, description="Filter by parent subject ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    include_deleted: bool = Query(False, description="Include soft-deleted subjects"),
    sort_by: str = Query("created_dt", description="Sort field (created_dt, name)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    user=Depends(admin_required)
):
    """
    Get all subjects with pagination, filtering, and sorting.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_subject_repository()
    try:
        # Build query
        query = repo.db.query(Subject)
        
        # Filter by deleted status
        if not include_deleted:
            query = query.filter(Subject.deleted_dt.is_(None))
        
        # Filter by type_id
        if type_id is not None:
            query = query.filter(Subject.type_id == type_id)
        
        # Filter by parent_id
        if parent_id is not None:
            query = query.filter(Subject.parent_id == parent_id)
        
        # Search by name
        if search:
            query = query.filter(Subject.name.ilike(f"%{search}%"))
        
        # Get total count
        total = query.count()
        
        # Sorting
        if sort_by == "name":
            sort_column = Subject.name
        elif sort_by == "created_dt":
            sort_column = Subject.created_dt
        else:
            sort_column = Subject.created_dt
        
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Pagination
        offset = (page - 1) * limit
        subjects = query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        total_pages = ceil(total / limit) if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        # Convert to SubjectOut with additional info
        subject_out_list = []
        for subject in subjects:
            # Get additional info
            children_count = repo.count_children(subject.id)
            subject_dict = {
                "id": subject.id,
                "name": subject.name,
                "type_id": subject.type_id,
                "parent_id": subject.parent_id,
                "created_dt": subject.created_dt,
                "updated_dt": subject.updated_dt,
                "deleted_dt": subject.deleted_dt,
                "subject_type_name": None,  # Could be joined if needed
                "parent_name": None,  # Could be joined if needed
                "children_count": children_count
            }
            subject_out_list.append(SubjectOut(**subject_dict))
        
        return PaginatedSubjectResponse(
            items=subject_out_list,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    finally:
        repo.db.close()


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject_by_id(
    subject_id: int,
    include_deleted: bool = Query(False, description="Include soft-deleted subjects"),
    user=Depends(admin_required)
):
    """
    Get subject by ID.
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_subject_repository()
    try:
        if include_deleted:
            # Get subject including deleted ones
            db_subject = repo.db.query(Subject).filter(Subject.id == subject_id).first()
        else:
            # Get only active subject
            db_subject = repo.get_by_id(subject_id)
        
        if not db_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Get additional info
        children_count = repo.count_children(subject_id)
        subject_dict = {
            "id": db_subject.id,
            "name": db_subject.name,
            "type_id": db_subject.type_id,
            "parent_id": db_subject.parent_id,
            "created_dt": db_subject.created_dt,
            "updated_dt": db_subject.updated_dt,
            "deleted_dt": db_subject.deleted_dt,
            "subject_type_name": None,
            "parent_name": None,
            "children_count": children_count
        }
        
        return SubjectOut(**subject_dict)
    finally:
        repo.db.close()


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    user=Depends(admin_required)
):
    """
    Create a new subject.
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        new_subject = service.create_subject(subject_data)
        
        # Get additional info
        repo = RepositoryFactory.get_subject_repository()
        try:
            children_count = repo.count_children(new_subject.id)
            subject_dict = {
                "id": new_subject.id,
                "name": new_subject.name,
                "type_id": new_subject.type_id,
                "parent_id": new_subject.parent_id,
                "created_dt": new_subject.created_dt,
                "updated_dt": new_subject.updated_dt,
                "deleted_dt": new_subject.deleted_dt,
                "subject_type_name": None,
                "parent_name": None,
                "children_count": children_count
            }
            return SubjectOut(**subject_dict)
        finally:
            repo.db.close()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    user=Depends(admin_required)
):
    """
    Update subject information.
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        updated_subject = service.update_subject(subject_id, subject_data)
        
        if not updated_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Get additional info
        repo = RepositoryFactory.get_subject_repository()
        try:
            children_count = repo.count_children(subject_id)
            subject_dict = {
                "id": updated_subject.id,
                "name": updated_subject.name,
                "type_id": updated_subject.type_id,
                "parent_id": updated_subject.parent_id,
                "created_dt": updated_subject.created_dt,
                "updated_dt": updated_subject.updated_dt,
                "deleted_dt": updated_subject.deleted_dt,
                "subject_type_name": None,
                "parent_name": None,
                "children_count": children_count
            }
            return SubjectOut(**subject_dict)
        finally:
            repo.db.close()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{subject_id}", status_code=status.HTTP_200_OK)
def soft_delete_subject(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Soft delete subject (sets deleted_dt).
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        success = service.soft_delete_subject(subject_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found or already deleted"
            )
        
        return {"message": f"Subject {subject_id} has been soft deleted successfully"}
    except HTTPException:
        raise


@router.delete("/{subject_id}/hard", status_code=status.HTTP_200_OK)
def hard_delete_subject(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Hard delete subject (permanently removes from database).
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        success = service.hard_delete_subject(subject_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        return {"message": f"Subject {subject_id} has been permanently deleted"}
    except HTTPException:
        raise


@router.get("/{subject_id}/hierarchy", response_model=List[SubjectOut])
def get_subject_hierarchy(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Get full hierarchy of a subject (all parents from root to subject).
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        hierarchy = service.get_subject_hierarchy(subject_id)
        
        if not hierarchy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Convert to SubjectOut
        hierarchy_out = []
        repo = RepositoryFactory.get_subject_repository()
        try:
            for subject in hierarchy:
                children_count = repo.count_children(subject.id)
                subject_dict = {
                    "id": subject.id,
                    "name": subject.name,
                    "type_id": subject.type_id,
                    "parent_id": subject.parent_id,
                    "created_dt": subject.created_dt,
                    "updated_dt": subject.updated_dt,
                    "deleted_dt": subject.deleted_dt,
                    "subject_type_name": None,
                    "parent_name": None,
                    "children_count": children_count
                }
                hierarchy_out.append(SubjectOut(**subject_dict))
        finally:
            repo.db.close()
        
        return hierarchy_out
    except HTTPException:
        raise


@router.get("/{subject_id}/children", response_model=List[SubjectOut])
def get_subject_children(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Get all children of a subject (direct children only).
    Only accessible by admins.
    """
    repo = RepositoryFactory.get_subject_repository()
    try:
        # Verify subject exists
        subject = repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Get direct children
        children = repo.get_by_parent(subject_id)
        
        # Convert to SubjectOut
        children_out = []
        for child in children:
            children_count = repo.count_children(child.id)
            subject_dict = {
                "id": child.id,
                "name": child.name,
                "type_id": child.type_id,
                "parent_id": child.parent_id,
                "created_dt": child.created_dt,
                "updated_dt": child.updated_dt,
                "deleted_dt": child.deleted_dt,
                "subject_type_name": None,
                "parent_name": None,
                "children_count": children_count
            }
            children_out.append(SubjectOut(**subject_dict))
        
        return children_out
    except HTTPException:
        raise
    finally:
        repo.db.close()


@router.get("/{subject_id}/children-tree", response_model=List[SubjectOut])
def get_subject_children_tree(
    subject_id: int,
    user=Depends(admin_required)
):
    """
    Get full children tree of a subject (all descendants recursively).
    Only accessible by admins.
    """
    service = SubjectService()
    try:
        # Verify subject exists
        subject = service.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {subject_id} not found"
            )
        
        # Get children tree
        children_tree = service.get_subject_children_tree(subject_id)
        
        # Convert to SubjectOut
        children_out = []
        repo = RepositoryFactory.get_subject_repository()
        try:
            for child in children_tree:
                children_count = repo.count_children(child.id)
                subject_dict = {
                    "id": child.id,
                    "name": child.name,
                    "type_id": child.type_id,
                    "parent_id": child.parent_id,
                    "created_dt": child.created_dt,
                    "updated_dt": child.updated_dt,
                    "deleted_dt": child.deleted_dt,
                    "subject_type_name": None,
                    "parent_name": None,
                    "children_count": children_count
                }
                children_out.append(SubjectOut(**subject_dict))
        finally:
            repo.db.close()
        
        return children_out
    except HTTPException:
        raise

