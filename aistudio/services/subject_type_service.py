"""
services/subject_type_service.py

Содержит бизнес-логику для работы с типами субъектов.
Вызывает методы из репозиториев и возвращает данные контроллерам.
"""

from typing import List, Optional
from aistudio.models.subject_type import SubjectType
from aistudio.schemas.subject_type_create import SubjectTypeCreate
from aistudio.schemas.subject_type_update import SubjectTypeUpdate
from aistudio.repositories import RepositoryFactory


class SubjectTypeService:
    """
    Сервис для работы с типами субъектов.
    Использует фабрику репозиториев для получения доступа к данным.
    """

    def create_subject_type(self, subject_type_data: SubjectTypeCreate) -> SubjectType:
        """
        Создает новый тип субъекта.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            # Проверяем уникальность slug
            if repo.exists_by_slug(subject_type_data.slug):
                raise ValueError(f"SubjectType with slug '{subject_type_data.slug}' already exists")
            
            # Проверяем уникальность названия
            if repo.exists_by_name(subject_type_data.name):
                raise ValueError(f"SubjectType with name '{subject_type_data.name}' already exists")
            
            return repo.create(
                name=subject_type_data.name,
                slug=subject_type_data.slug
            )
        finally:
            repo.db.close()

    def get_subject_type_by_id(self, type_id: int) -> Optional[SubjectType]:
        """
        Получает тип субъекта по ID.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.get_by_id(type_id)
        finally:
            repo.db.close()

    def get_subject_type_by_slug(self, slug: str) -> Optional[SubjectType]:
        """
        Получает тип субъекта по slug.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.get_by_slug(slug)
        finally:
            repo.db.close()

    def get_all_subject_types(self) -> List[SubjectType]:
        """
        Получает все активные типы субъектов.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.get_all_active()
        finally:
            repo.db.close()

    def update_subject_type(self, type_id: int, subject_type_data: SubjectTypeUpdate) -> Optional[SubjectType]:
        """
        Обновляет тип субъекта.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            # Проверяем существование типа субъекта
            existing = repo.get_by_id(type_id)
            if not existing:
                return None
            
            # Подготавливаем данные для обновления
            update_data = {}
            if subject_type_data.name is not None:
                # Проверяем уникальность нового названия
                if repo.exists_by_name(subject_type_data.name) and existing.name != subject_type_data.name:
                    raise ValueError(f"SubjectType with name '{subject_type_data.name}' already exists")
                update_data['name'] = subject_type_data.name
            
            if subject_type_data.slug is not None:
                # Проверяем уникальность нового slug
                if repo.exists_by_slug(subject_type_data.slug) and existing.slug != subject_type_data.slug:
                    raise ValueError(f"SubjectType with slug '{subject_type_data.slug}' already exists")
                update_data['slug'] = subject_type_data.slug
            
            if not update_data:
                return existing  # Нет изменений
            
            return repo.update(type_id, **update_data)
        finally:
            repo.db.close()

    def soft_delete_subject_type(self, type_id: int) -> bool:
        """
        Мягко удаляет тип субъекта.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.soft_delete(type_id)
        finally:
            repo.db.close()

    def hard_delete_subject_type(self, type_id: int) -> bool:
        """
        Жестко удаляет тип субъекта.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.hard_delete(type_id)
        finally:
            repo.db.close()

    def exists_subject_type(self, type_id: int) -> bool:
        """
        Проверяет существование типа субъекта.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            return repo.get_by_id(type_id) is not None
        finally:
            repo.db.close()

    def validate_subject_type_data(self, name: str, slug: str) -> List[str]:
        """
        Валидирует данные типа субъекта.
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

    def get_subject_types_by_ids(self, type_ids: List[int]) -> List[SubjectType]:
        """
        Получает типы субъектов по списку ID.
        """
        repo = RepositoryFactory.get_subject_type_repository()
        try:
            all_types = repo.get_all_active()
            return [st for st in all_types if st.id in type_ids]
        finally:
            repo.db.close() 