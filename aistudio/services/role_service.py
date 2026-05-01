"""
services/role_service.py

Содержит бизнес-логику для работы с ролями.
Вызывает методы из репозиториев и возвращает данные контроллерам.
"""

from typing import List, Optional
from aistudio.models.role import Role
from aistudio.schemas.role_create import RoleCreate
from aistudio.schemas.role_update import RoleUpdate
from aistudio.repositories import RepositoryFactory


class RoleService:
    """
    Сервис для работы с ролями.
    Использует фабрику репозиториев для получения доступа к данным.
    """

    def create_role(self, role_data: RoleCreate) -> Role:
        """
        Создает новую роль.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            # Проверяем уникальность slug
            if repo.exists_by_slug(role_data.slug):
                raise ValueError(f"Role with slug '{role_data.slug}' already exists")
            
            # Проверяем уникальность названия
            if repo.exists_by_name(role_data.name):
                raise ValueError(f"Role with name '{role_data.name}' already exists")
            
            return repo.create(
                name=role_data.name,
                slug=role_data.slug
            )
        finally:
            repo.db.close()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        Получает роль по ID.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.get_by_id(role_id)
        finally:
            repo.db.close()

    def get_role_by_slug(self, slug: str) -> Optional[Role]:
        """
        Получает роль по slug.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.get_by_slug(slug)
        finally:
            repo.db.close()

    def get_all_roles(self) -> List[Role]:
        """
        Получает все активные роли.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.get_all_active()
        finally:
            repo.db.close()

    def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """
        Обновляет роль.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            # Проверяем существование роли
            existing = repo.get_by_id(role_id)
            if not existing:
                return None
            
            # Подготавливаем данные для обновления
            update_data = {}
            if role_data.name is not None:
                # Проверяем уникальность нового названия
                if repo.exists_by_name(role_data.name) and existing.name != role_data.name:
                    raise ValueError(f"Role with name '{role_data.name}' already exists")
                update_data['name'] = role_data.name
            
            if role_data.slug is not None:
                # Проверяем уникальность нового slug
                if repo.exists_by_slug(role_data.slug) and existing.slug != role_data.slug:
                    raise ValueError(f"Role with slug '{role_data.slug}' already exists")
                update_data['slug'] = role_data.slug
            
            if not update_data:
                return existing  # Нет изменений
            
            return repo.update(role_id, **update_data)
        finally:
            repo.db.close()

    def soft_delete_role(self, role_id: int) -> bool:
        """
        Мягко удаляет роль.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.soft_delete(role_id)
        finally:
            repo.db.close()

    def hard_delete_role(self, role_id: int) -> bool:
        """
        Жестко удаляет роль.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.hard_delete(role_id)
        finally:
            repo.db.close()

    def exists_role(self, role_id: int) -> bool:
        """
        Проверяет существование роли.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.get_by_id(role_id) is not None
        finally:
            repo.db.close()

    def get_default_roles(self) -> List[Role]:
        """
        Получает стандартные роли (owner, editor, viewer).
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.get_default_roles()
        finally:
            repo.db.close()

    def create_default_roles(self) -> List[Role]:
        """
        Создает стандартные роли, если они не существуют.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            return repo.create_default_roles()
        finally:
            repo.db.close()

    def get_roles_by_slugs(self, slugs: List[str]) -> List[Role]:
        """
        Получает роли по списку slug.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            all_roles = repo.get_all_active()
            return [role for role in all_roles if role.slug in slugs]
        finally:
            repo.db.close()

    def get_roles_by_ids(self, role_ids: List[int]) -> List[Role]:
        """
        Получает роли по списку ID.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            all_roles = repo.get_all_active()
            return [role for role in all_roles if role.id in role_ids]
        finally:
            repo.db.close()

    def validate_role_data(self, name: str, slug: str) -> List[str]:
        """
        Валидирует данные роли.
        Возвращает список ошибок.
        """
        errors = []
        
        # Проверка названия
        if not name or not name.strip():
            errors.append("Name is required")
        elif len(name) > 50:
            errors.append("Name must be less than 50 characters")
        
        # Проверка slug
        if not slug or not slug.strip():
            errors.append("Slug is required")
        elif len(slug) > 10:
            errors.append("Slug must be less than 10 characters")
        elif not slug.replace('-', '').replace('_', '').isalnum():
            errors.append("Slug must contain only letters, numbers, hyphens and underscores")
        
        return errors

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        Получает роль по названию.
        """
        repo = RepositoryFactory.get_role_repository()
        try:
            all_roles = repo.get_all_active()
            for role in all_roles:
                if role.name == name:
                    return role
            return None
        finally:
            repo.db.close()

    def ensure_default_roles_exist(self) -> List[Role]:
        """
        Убеждается, что стандартные роли существуют.
        Создает их, если они отсутствуют.
        """
        default_roles = self.get_default_roles()
        if len(default_roles) < 3:  # owner, editor, viewer
            return self.create_default_roles()
        return default_roles 