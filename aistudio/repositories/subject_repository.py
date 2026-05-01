"""
repositories/subject_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели субъектов.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from datetime import datetime
from typing import List, Optional
from aistudio.models.subject import Subject


class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, type_id: int, parent_id: Optional[int] = None) -> Subject:
        """
        Создает новый субъект.
        """
        try:
            subject = Subject(
                name=name,
                type_id=type_id,
                parent_id=parent_id
            )
            self.db.add(subject)
            self.db.commit()
            self.db.refresh(subject)
            return subject
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Subject creation failed - check type_id and parent_id")

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """
        Получает субъект по ID.
        """
        return self.db.query(Subject).filter(
            Subject.id == subject_id,
            Subject.deleted_dt.is_(None)
        ).first()

    def get_all_active(self) -> List[Subject]:
        """
        Получает все активные субъекты.
        """
        return self.db.query(Subject).filter(
            Subject.deleted_dt.is_(None)
        ).all()

    def get_by_type(self, type_id: int) -> List[Subject]:
        """
        Получает все субъекты определенного типа.
        """
        return self.db.query(Subject).filter(
            Subject.type_id == type_id,
            Subject.deleted_dt.is_(None)
        ).all()

    def get_by_parent(self, parent_id: int) -> List[Subject]:
        """
        Получает все дочерние субъекты.
        """
        return self.db.query(Subject).filter(
            Subject.parent_id == parent_id,
            Subject.deleted_dt.is_(None)
        ).all()

    def get_root_subjects(self) -> List[Subject]:
        """
        Получает все корневые субъекты (без родителя).
        """
        return self.db.query(Subject).filter(
            Subject.parent_id.is_(None),
            Subject.deleted_dt.is_(None)
        ).all()

    def search_by_name(self, name: str) -> List[Subject]:
        """
        Поиск субъектов по названию (подстрока).
        """
        return self.db.query(Subject).filter(
            Subject.name.contains(name),
            Subject.deleted_dt.is_(None)
        ).all()

    def get_hierarchy(self, subject_id: int) -> List[Subject]:
        """
        Получает полную иерархию субъекта (все родители).
        """
        hierarchy = []
        current = self.get_by_id(subject_id)
        
        while current:
            hierarchy.append(current)
            if current.parent_id:
                current = self.get_by_id(current.parent_id)
            else:
                break
        
        return list(reversed(hierarchy))  # От корня к листу

    def get_children_tree(self, subject_id: int) -> List[Subject]:
        """
        Получает дерево дочерних субъектов.
        """
        children = self.get_by_parent(subject_id)
        result = []
        
        for child in children:
            result.append(child)
            result.extend(self.get_children_tree(child.id))
        
        return result

    def update(self, subject_id: int, **kwargs) -> Optional[Subject]:
        """
        Обновляет субъект.
        """
        subject = self.get_by_id(subject_id)
        if not subject:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(subject, key) and value is not None:
                    setattr(subject, key, value)
            
            self.db.commit()
            self.db.refresh(subject)
            return subject
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Subject update failed - check type_id and parent_id")

    def soft_delete(self, subject_id: int) -> bool:
        """
        Мягко удаляет субъект.
        """
        subject = self.get_by_id(subject_id)
        if not subject:
            return False
        
        subject.deleted_dt = datetime.now()
        self.db.commit()
        return True

    def hard_delete(self, subject_id: int) -> bool:
        """
        Жестко удаляет субъект.
        """
        subject = self.get_by_id(subject_id)
        if not subject:
            return False
        
        self.db.delete(subject)
        self.db.commit()
        return True

    def filter_subjects(self, name: Optional[str] = None, 
                       type_id: Optional[int] = None, 
                       parent_id: Optional[int] = None,
                       include_deleted: bool = False) -> List[Subject]:
        """
        Фильтрация субъектов по различным критериям.
        """
        query = self.db.query(Subject)
        
        if not include_deleted:
            query = query.filter(Subject.deleted_dt.is_(None))
        
        if name:
            query = query.filter(Subject.name.contains(name))
        
        if type_id is not None:
            query = query.filter(Subject.type_id == type_id)
        
        if parent_id is not None:
            query = query.filter(Subject.parent_id == parent_id)
        
        return query.all()

    def count_children(self, subject_id: int) -> int:
        """
        Подсчитывает количество дочерних субъектов.
        """
        return self.db.query(Subject).filter(
            Subject.parent_id == subject_id,
            Subject.deleted_dt.is_(None)
        ).count()

    def move_subject(self, subject_id: int, new_parent_id: Optional[int]) -> bool:
        """
        Перемещает субъект в другую ветку иерархии.
        """
        subject = self.get_by_id(subject_id)
        if not subject:
            return False
        
        # Проверяем, что новый родитель существует
        if new_parent_id:
            new_parent = self.get_by_id(new_parent_id)
            if not new_parent:
                return False
        
        try:
            subject.parent_id = new_parent_id
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False 