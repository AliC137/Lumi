"""
repositories/role_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели ролей.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional
from aistudio.models.role import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, slug: str) -> Role:
        """
        Создает новую роль.
        """
        try:
            role = Role(
                name=name,
                slug=slug
            )
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Role with this name or slug already exists")

    def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Получает роль по ID.
        """
        return self.db.query(Role).filter(
            Role.id == role_id,
            Role.deleted_dt.is_(None)
        ).first()

    def get_by_slug(self, slug: str) -> Optional[Role]:
        """
        Получает роль по slug.
        """
        return self.db.query(Role).filter(
            Role.slug == slug,
            Role.deleted_dt.is_(None)
        ).first()

    def get_all_active(self) -> List[Role]:
        """
        Получает все активные роли.
        """
        return self.db.query(Role).filter(
            Role.deleted_dt.is_(None)
        ).all()

    def update(self, role_id: int, **kwargs) -> Optional[Role]:
        """
        Обновляет роль.
        """
        role = self.get_by_id(role_id)
        if not role:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(role, key) and value is not None:
                    setattr(role, key, value)
            
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Role with this name or slug already exists")

    def soft_delete(self, role_id: int) -> bool:
        """
        Мягко удаляет роль.
        """
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        role.deleted_dt = datetime.now()
        self.db.commit()
        return True

    def hard_delete(self, role_id: int) -> bool:
        """
        Жестко удаляет роль.
        """
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        self.db.delete(role)
        self.db.commit()
        return True

    def exists_by_name(self, name: str) -> bool:
        """
        Проверяет существование роли по названию.
        """
        return self.db.query(Role).filter(
            Role.name == name,
            Role.deleted_dt.is_(None)
        ).first() is not None

    def exists_by_slug(self, slug: str) -> bool:
        """
        Проверяет существование роли по slug.
        """
        return self.db.query(Role).filter(
            Role.slug == slug,
            Role.deleted_dt.is_(None)
        ).first() is not None

    def get_default_roles(self) -> List[Role]:
        """
        Получает стандартные роли (owner, editor, viewer).
        """
        default_slugs = ['owner', 'editor', 'viewer']
        return self.db.query(Role).filter(
            Role.slug.in_(default_slugs),
            Role.deleted_dt.is_(None)
        ).all()

    def create_default_roles(self) -> List[Role]:
        """
        Создает стандартные роли, если они не существуют.
        """
        default_roles = [
            {"name": "Владелец", "slug": "owner"},
            {"name": "Редактор", "slug": "editor"},
            {"name": "Просмотр", "slug": "viewer"}
        ]
        
        created_roles = []
        for role_data in default_roles:
            if not self.exists_by_slug(role_data["slug"]):
                role = self.create(role_data["name"], role_data["slug"])
                created_roles.append(role)
        
        return created_roles 