"""
repositories/subject_type_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели типов субъектов.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional
from aistudio.models.subject_type import SubjectType


class SubjectTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, slug: str) -> SubjectType:
        """
        Создает новый тип субъекта.
        """
        try:
            subject_type = SubjectType(
                name=name,
                slug=slug
            )
            self.db.add(subject_type)
            self.db.commit()
            self.db.refresh(subject_type)
            return subject_type
        except IntegrityError:
            self.db.rollback()
            raise ValueError("SubjectType with this name or slug already exists")

    def get_by_id(self, type_id: int) -> Optional[SubjectType]:
        """
        Получает тип субъекта по ID.
        """
        return self.db.query(SubjectType).filter(
            SubjectType.id == type_id,
            SubjectType.deleted_dt.is_(None)
        ).first()

    def get_by_slug(self, slug: str) -> Optional[SubjectType]:
        """
        Получает тип субъекта по slug.
        """
        return self.db.query(SubjectType).filter(
            SubjectType.slug == slug,
            SubjectType.deleted_dt.is_(None)
        ).first()

    def get_all_active(self) -> List[SubjectType]:
        """
        Получает все активные типы субъектов.
        """
        return self.db.query(SubjectType).filter(
            SubjectType.deleted_dt.is_(None)
        ).all()

    def update(self, type_id: int, **kwargs) -> Optional[SubjectType]:
        """
        Обновляет тип субъекта.
        """
        subject_type = self.get_by_id(type_id)
        if not subject_type:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(subject_type, key) and value is not None:
                    setattr(subject_type, key, value)
            
            self.db.commit()
            self.db.refresh(subject_type)
            return subject_type
        except IntegrityError:
            self.db.rollback()
            raise ValueError("SubjectType with this name or slug already exists")

    def soft_delete(self, type_id: int) -> bool:
        """
        Мягко удаляет тип субъекта.
        """
        subject_type = self.get_by_id(type_id)
        if not subject_type:
            return False
        
        subject_type.deleted_dt = datetime.now()
        self.db.commit()
        return True

    def hard_delete(self, type_id: int) -> bool:
        """
        Жестко удаляет тип субъекта.
        """
        subject_type = self.get_by_id(type_id)
        if not subject_type:
            return False
        
        self.db.delete(subject_type)
        self.db.commit()
        return True

    def exists_by_name(self, name: str) -> bool:
        """
        Проверяет существование типа субъекта по названию.
        """
        return self.db.query(SubjectType).filter(
            SubjectType.name == name,
            SubjectType.deleted_dt.is_(None)
        ).first() is not None

    def exists_by_slug(self, slug: str) -> bool:
        """
        Проверяет существование типа субъекта по slug.
        """
        return self.db.query(SubjectType).filter(
            SubjectType.slug == slug,
            SubjectType.deleted_dt.is_(None)
        ).first() is not None 