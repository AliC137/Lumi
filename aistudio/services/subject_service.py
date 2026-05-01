"""
services/subject_service.py

Содержит бизнес-логику для работы с субъектами.
Вызывает методы из репозиториев и возвращает данные контроллерам.
"""

from typing import List, Optional, Dict, Any
from aistudio.models.subject import Subject
from aistudio.schemas.subject_create import SubjectCreate
from aistudio.schemas.subject_update import SubjectUpdate
from aistudio.schemas.subject_filter import SubjectFilter
from aistudio.repositories import RepositoryFactory


class SubjectService:
    """
    Сервис для работы с субъектами.
    Использует фабрику репозиториев для получения доступа к данным.
    """

    def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """
        Создает новый субъект.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            # Проверяем существование типа субъекта
            if not self._validate_subject_type(subject_data.type_id):
                raise ValueError(f"SubjectType with id {subject_data.type_id} does not exist")
            
            # Проверяем существование родительского субъекта
            if subject_data.parent_id and not self._validate_parent_subject(subject_data.parent_id):
                raise ValueError(f"Parent subject with id {subject_data.parent_id} does not exist")
            
            return repo.create(
                name=subject_data.name,
                type_id=subject_data.type_id,
                parent_id=subject_data.parent_id
            )
        finally:
            repo.db.close()

    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        """
        Получает субъект по ID.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_by_id(subject_id)
        finally:
            repo.db.close()

    def get_all_subjects(self) -> List[Subject]:
        """
        Получает все активные субъекты.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_all_active()
        finally:
            repo.db.close()

    def get_subjects_by_type(self, type_id: int) -> List[Subject]:
        """
        Получает все субъекты определенного типа.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_by_type(type_id)
        finally:
            repo.db.close()

    def get_root_subjects(self) -> List[Subject]:
        """
        Получает все корневые субъекты (без родителя).
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_root_subjects()
        finally:
            repo.db.close()

    def get_subject_hierarchy(self, subject_id: int) -> List[Subject]:
        """
        Получает полную иерархию субъекта (все родители).
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_hierarchy(subject_id)
        finally:
            repo.db.close()

    def get_subject_children_tree(self, subject_id: int) -> List[Subject]:
        """
        Получает дерево дочерних субъектов.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_children_tree(subject_id)
        finally:
            repo.db.close()

    def search_subjects_by_name(self, name: str) -> List[Subject]:
        """
        Поиск субъектов по названию.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.search_by_name(name)
        finally:
            repo.db.close()

    def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[Subject]:
        """
        Обновляет субъект.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            # Проверяем существование субъекта
            existing = repo.get_by_id(subject_id)
            if not existing:
                return None
            
            # Подготавливаем данные для обновления
            update_data = {}
            if subject_data.name is not None:
                update_data['name'] = subject_data.name
            
            if subject_data.type_id is not None:
                # Проверяем существование типа субъекта
                if not self._validate_subject_type(subject_data.type_id):
                    raise ValueError(f"SubjectType with id {subject_data.type_id} does not exist")
                update_data['type_id'] = subject_data.type_id
            
            if subject_data.parent_id is not None:
                # Проверяем существование родительского субъекта
                if subject_data.parent_id and not self._validate_parent_subject(subject_data.parent_id):
                    raise ValueError(f"Parent subject with id {subject_data.parent_id} does not exist")
                update_data['parent_id'] = subject_data.parent_id
            
            if not update_data:
                return existing  # Нет изменений
            
            return repo.update(subject_id, **update_data)
        finally:
            repo.db.close()

    def move_subject(self, subject_id: int, new_parent_id: Optional[int]) -> bool:
        """
        Перемещает субъект в другую ветку иерархии.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            # Проверяем существование субъекта
            if not repo.get_by_id(subject_id):
                return False
            
            # Проверяем существование нового родителя
            if new_parent_id and not self._validate_parent_subject(new_parent_id):
                return False
            
            return repo.move_subject(subject_id, new_parent_id)
        finally:
            repo.db.close()

    def soft_delete_subject(self, subject_id: int) -> bool:
        """
        Мягко удаляет субъект.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.soft_delete(subject_id)
        finally:
            repo.db.close()

    def hard_delete_subject(self, subject_id: int) -> bool:
        """
        Жестко удаляет субъект.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.hard_delete(subject_id)
        finally:
            repo.db.close()

    def filter_subjects(self, filter_data: SubjectFilter) -> List[Subject]:
        """
        Фильтрует субъекты по различным критериям.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.filter_subjects(
                name=filter_data.name,
                type_id=filter_data.type_id,
                parent_id=filter_data.parent_id,
                include_deleted=filter_data.include_deleted
            )
        finally:
            repo.db.close()

    def count_subject_children(self, subject_id: int) -> int:
        """
        Подсчитывает количество дочерних субъектов.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.count_children(subject_id)
        finally:
            repo.db.close()

    def get_subject_with_details(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает субъект с дополнительной информацией.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            subject = repo.get_by_id(subject_id)
            if not subject:
                return None
            
            # Получаем дополнительную информацию
            children_count = repo.count_children(subject_id)
            hierarchy = repo.get_hierarchy(subject_id)
            
            return {
                'subject': subject,
                'children_count': children_count,
                'hierarchy': hierarchy
            }
        finally:
            repo.db.close()

    def _validate_subject_type(self, type_id: int) -> bool:
        """
        Проверяет существование типа субъекта.
        """
        from aistudio.services.subject_type_service import SubjectTypeService
        service = SubjectTypeService()
        return service.exists_subject_type(type_id)

    def _validate_parent_subject(self, parent_id: int) -> bool:
        """
        Проверяет существование родительского субъекта.
        """
        repo = RepositoryFactory.get_subject_repository()
        try:
            return repo.get_by_id(parent_id) is not None
        finally:
            repo.db.close()

    def validate_subject_data(self, name: str, type_id: int, parent_id: Optional[int] = None) -> List[str]:
        """
        Валидирует данные субъекта.
        Возвращает список ошибок.
        """
        errors = []
        
        # Проверка названия
        if not name or not name.strip():
            errors.append("Name is required")
        elif len(name) > 50:
            errors.append("Name must be less than 50 characters")
        
        # Проверка типа субъекта
        if not self._validate_subject_type(type_id):
            errors.append(f"SubjectType with id {type_id} does not exist")
        
        # Проверка родительского субъекта
        if parent_id and not self._validate_parent_subject(parent_id):
            errors.append(f"Parent subject with id {parent_id} does not exist")
        
        return errors 