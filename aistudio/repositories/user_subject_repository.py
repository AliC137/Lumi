"""
repositories/user_subject_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели связей пользователь-субъект.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from aistudio.models.user_subject import UserSubject


class UserSubjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, subject_id: int, role_id: int) -> UserSubject:
        """
        Создает новую связь пользователь-субъект.
        """
        try:
            user_subject = UserSubject(
                user_id=user_id,
                subject_id=subject_id,
                role_id=role_id
            )
            self.db.add(user_subject)
            self.db.commit()
            self.db.refresh(user_subject)
            return user_subject
        except IntegrityError:
            self.db.rollback()
            raise ValueError("UserSubject with this user_id and subject_id already exists")

    def get_by_user_and_subject(self, user_id: int, subject_id: int) -> Optional[UserSubject]:
        """
        Получает связь по пользователю и субъекту.
        """
        return self.db.query(UserSubject).filter(
            UserSubject.user_id == user_id,
            UserSubject.subject_id == subject_id,
            UserSubject.deleted_dt.is_(None)
        ).first()

    def get_by_user_id(self, user_id: int) -> List[UserSubject]:
        """
        Получает все связи для пользователя.
        """
        return self.db.query(UserSubject).filter(
            UserSubject.user_id == user_id,
            UserSubject.deleted_dt.is_(None)
        ).all()

    def get_by_subject_id(self, subject_id: int) -> List[UserSubject]:
        """
        Получает все связи для субъекта.
        """
        return self.db.query(UserSubject).filter(
            UserSubject.subject_id == subject_id,
            UserSubject.deleted_dt.is_(None)
        ).all()

    def get_by_role_id(self, role_id: int) -> List[UserSubject]:
        """
        Получает все связи с определенной ролью.
        """
        return self.db.query(UserSubject).filter(
            UserSubject.role_id == role_id,
            UserSubject.deleted_dt.is_(None)
        ).all()

    def get_all_active(self) -> List[UserSubject]:
        """
        Получает все активные связи.
        """
        return self.db.query(UserSubject).filter(
            UserSubject.deleted_dt.is_(None)
        ).all()

    def update_role(self, user_id: int, subject_id: int, new_role_id: int) -> Optional[UserSubject]:
        """
        Обновляет роль в связи пользователь-субъект.
        """
        user_subject = self.get_by_user_and_subject(user_id, subject_id)
        if not user_subject:
            return None
        
        try:
            user_subject.role_id = new_role_id
            self.db.commit()
            self.db.refresh(user_subject)
            return user_subject
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to update role")

    def soft_delete(self, user_id: int, subject_id: int) -> bool:
        """
        Мягко удаляет связь пользователь-субъект.
        """
        user_subject = self.get_by_user_and_subject(user_id, subject_id)
        if not user_subject:
            return False
        
        user_subject.deleted_dt = datetime.now()
        self.db.commit()
        return True

    def hard_delete(self, user_id: int, subject_id: int) -> bool:
        """
        Жестко удаляет связь пользователь-субъект.
        """
        user_subject = self.get_by_user_and_subject(user_id, subject_id)
        if not user_subject:
            return False
        
        self.db.delete(user_subject)
        self.db.commit()
        return True

    def delete_user_connections(self, user_id: int) -> int:
        """
        Удаляет все связи пользователя.
        """
        connections = self.get_by_user_id(user_id)
        count = 0
        for connection in connections:
            connection.deleted_dt = datetime.now()
            count += 1
        
        self.db.commit()
        return count

    def delete_subject_connections(self, subject_id: int) -> int:
        """
        Удаляет все связи субъекта.
        """
        connections = self.get_by_subject_id(subject_id)
        count = 0
        for connection in connections:
            connection.deleted_dt = datetime.now()
            count += 1
        
        self.db.commit()
        return count

    def filter_connections(self, user_id: Optional[int] = None,
                         subject_id: Optional[int] = None,
                         role_id: Optional[int] = None,
                         include_deleted: bool = False) -> List[UserSubject]:
        """
        Фильтрация связей по различным критериям.
        """
        query = self.db.query(UserSubject)
        
        if not include_deleted:
            query = query.filter(UserSubject.deleted_dt.is_(None))
        
        if user_id is not None:
            query = query.filter(UserSubject.user_id == user_id)
        
        if subject_id is not None:
            query = query.filter(UserSubject.subject_id == subject_id)
        
        if role_id is not None:
            query = query.filter(UserSubject.role_id == role_id)
        
        return query.all()

    def get_users_for_subject(self, subject_id: int) -> List[int]:
        """
        Получает список пользователей для субъекта.
        """
        connections = self.get_by_subject_id(subject_id)
        return [conn.user_id for conn in connections]

    def get_subjects_for_user(self, user_id: int) -> List[int]:
        """
        Получает список субъектов для пользователя.
        """
        connections = self.get_by_user_id(user_id)
        return [conn.subject_id for conn in connections]

    def check_user_access(self, user_id: int, subject_id: int) -> Optional[str]:
        """
        Проверяет доступ пользователя к субъекту и возвращает роль.
        """
        connection = self.get_by_user_and_subject(user_id, subject_id)
        if connection:
            return connection.role.slug if hasattr(connection, 'role') else None
        return None

    def get_user_role_in_subject(self, user_id: int, subject_id: int) -> Optional[int]:
        """
        Получает роль пользователя в субъекте.
        """
        connection = self.get_by_user_and_subject(user_id, subject_id)
        return connection.role_id if connection else None

    def assign_user_to_subject(self, user_id: int, subject_id: int, role_id: int) -> UserSubject:
        """
        Назначает пользователя к субъекту с определенной ролью.
        Если связь уже существует, обновляет роль.
        """
        existing = self.get_by_user_and_subject(user_id, subject_id)
        if existing:
            return self.update_role(user_id, subject_id, role_id)
        else:
            return self.create(user_id, subject_id, role_id)

    def remove_user_from_subject(self, user_id: int, subject_id: int) -> bool:
        """
        Удаляет пользователя из субъекта.
        """
        return self.soft_delete(user_id, subject_id)

    def get_subject_users_with_roles(self, subject_id: int) -> List[dict]:
        """
        Получает пользователей субъекта с их ролями.
        """
        connections = self.get_by_subject_id(subject_id)
        result = []
        for conn in connections:
            result.append({
                'user_id': conn.user_id,
                'role_id': conn.role_id,
                'created_dt': conn.created_dt
            })
        return result 