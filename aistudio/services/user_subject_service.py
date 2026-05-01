"""
services/user_subject_service.py

Содержит бизнес-логику для работы со связями пользователь-субъект.
Вызывает методы из репозиториев и возвращает данные контроллерам.
"""

from typing import List, Optional, Dict, Any
from aistudio.models.user_subject import UserSubject
from aistudio.schemas.user_subject_create import UserSubjectCreate
from aistudio.schemas.user_subject_update import UserSubjectUpdate
from aistudio.schemas.user_subject_filter import UserSubjectFilter
from aistudio.repositories import RepositoryFactory


class UserSubjectService:
    """
    Сервис для работы со связями пользователь-субъект.
    Использует фабрику репозиториев для получения доступа к данным.
    """

    def create_user_subject_connection(self, connection_data: UserSubjectCreate) -> UserSubject:
        """
        Создает новую связь пользователь-субъект.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            # Проверяем существование пользователя
            if not self._validate_user(connection_data.user_id):
                raise ValueError(f"User with id {connection_data.user_id} does not exist")
            
            # Проверяем существование субъекта
            if not self._validate_subject(connection_data.subject_id):
                raise ValueError(f"Subject with id {connection_data.subject_id} does not exist")
            
            # Проверяем существование роли
            if not self._validate_role(connection_data.role_id):
                raise ValueError(f"Role with id {connection_data.role_id} does not exist")
            
            return repo.create(
                user_id=connection_data.user_id,
                subject_id=connection_data.subject_id,
                role_id=connection_data.role_id
            )
        finally:
            repo.db.close()

    def get_user_subject_connection(self, user_id: int, subject_id: int) -> Optional[UserSubject]:
        """
        Получает связь пользователь-субъект.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_by_user_and_subject(user_id, subject_id)
        finally:
            repo.db.close()

    def get_user_connections(self, user_id: int) -> List[UserSubject]:
        """
        Получает все связи пользователя.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_by_user_id(user_id)
        finally:
            repo.db.close()

    def get_subject_connections(self, subject_id: int) -> List[UserSubject]:
        """
        Получает все связи субъекта.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_by_subject_id(subject_id)
        finally:
            repo.db.close()

    def get_all_connections(self) -> List[UserSubject]:
        """
        Получает все активные связи.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_all_active()
        finally:
            repo.db.close()

    def update_user_role_in_subject(self, user_id: int, subject_id: int, new_role_id: int) -> Optional[UserSubject]:
        """
        Обновляет роль пользователя в субъекте.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            # Проверяем существование роли
            if not self._validate_role(new_role_id):
                raise ValueError(f"Role with id {new_role_id} does not exist")
            
            return repo.update_role(user_id, subject_id, new_role_id)
        finally:
            repo.db.close()

    def assign_user_to_subject(self, user_id: int, subject_id: int, role_id: int) -> UserSubject:
        """
        Назначает пользователя к субъекту с определенной ролью.
        Если связь уже существует, обновляет роль.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            # Проверяем существование пользователя
            if not self._validate_user(user_id):
                raise ValueError(f"User with id {user_id} does not exist")
            
            # Проверяем существование субъекта
            if not self._validate_subject(subject_id):
                raise ValueError(f"Subject with id {subject_id} does not exist")
            
            # Проверяем существование роли
            if not self._validate_role(role_id):
                raise ValueError(f"Role with id {role_id} does not exist")
            
            return repo.assign_user_to_subject(user_id, subject_id, role_id)
        finally:
            repo.db.close()

    def remove_user_from_subject(self, user_id: int, subject_id: int) -> bool:
        """
        Удаляет пользователя из субъекта.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.remove_user_from_subject(user_id, subject_id)
        finally:
            repo.db.close()

    def soft_delete_connection(self, user_id: int, subject_id: int) -> bool:
        """
        Мягко удаляет связь пользователь-субъект.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.soft_delete(user_id, subject_id)
        finally:
            repo.db.close()

    def hard_delete_connection(self, user_id: int, subject_id: int) -> bool:
        """
        Жестко удаляет связь пользователь-субъект.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.hard_delete(user_id, subject_id)
        finally:
            repo.db.close()

    def filter_connections(self, filter_data: UserSubjectFilter) -> List[UserSubject]:
        """
        Фильтрует связи по различным критериям.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.filter_connections(
                user_id=filter_data.user_id,
                subject_id=filter_data.subject_id,
                role_id=filter_data.role_id,
                include_deleted=filter_data.include_deleted
            )
        finally:
            repo.db.close()

    def get_users_for_subject(self, subject_id: int) -> List[int]:
        """
        Получает список пользователей для субъекта.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_users_for_subject(subject_id)
        finally:
            repo.db.close()

    def get_subjects_for_user(self, user_id: int) -> List[int]:
        """
        Получает список субъектов для пользователя.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_subjects_for_user(user_id)
        finally:
            repo.db.close()

    def check_user_access(self, user_id: int, subject_id: int) -> Optional[str]:
        """
        Проверяет доступ пользователя к субъекту и возвращает роль.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.check_user_access(user_id, subject_id)
        finally:
            repo.db.close()

    def get_user_role_in_subject(self, user_id: int, subject_id: int) -> Optional[int]:
        """
        Получает роль пользователя в субъекте.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_user_role_in_subject(user_id, subject_id)
        finally:
            repo.db.close()

    def get_subject_users_with_roles(self, subject_id: int) -> List[Dict[str, Any]]:
        """
        Получает пользователей субъекта с их ролями.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.get_subject_users_with_roles(subject_id)
        finally:
            repo.db.close()

    def delete_user_connections(self, user_id: int) -> int:
        """
        Удаляет все связи пользователя.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.delete_user_connections(user_id)
        finally:
            repo.db.close()

    def delete_subject_connections(self, subject_id: int) -> int:
        """
        Удаляет все связи субъекта.
        """
        repo = RepositoryFactory.get_user_subject_repository()
        try:
            return repo.delete_subject_connections(subject_id)
        finally:
            repo.db.close()

    def _validate_user(self, user_id: int) -> bool:
        """
        Проверяет существование пользователя.
        """
        from aistudio.services.user_service import UserService
        service = UserService()
        try:
            return service.get_user_by_id(user_id) is not None
        except ValueError:
            return False

    def _validate_subject(self, subject_id: int) -> bool:
        """
        Проверяет существование субъекта.
        """
        from aistudio.services.subject_service import SubjectService
        service = SubjectService()
        return service.get_subject_by_id(subject_id) is not None

    def _validate_role(self, role_id: int) -> bool:
        """
        Проверяет существование роли.
        """
        from aistudio.services.role_service import RoleService
        service = RoleService()
        return service.exists_role(role_id)

    def validate_connection_data(self, user_id: int, subject_id: int, role_id: int) -> List[str]:
        """
        Валидирует данные связи пользователь-субъект.
        Возвращает список ошибок.
        """
        errors = []
        
        # Проверка пользователя
        if not self._validate_user(user_id):
            errors.append(f"User with id {user_id} does not exist")
        
        # Проверка субъекта
        if not self._validate_subject(subject_id):
            errors.append(f"Subject with id {subject_id} does not exist")
        
        # Проверка роли
        if not self._validate_role(role_id):
            errors.append(f"Role with id {role_id} does not exist")
        
        return errors

    def get_user_subjects_with_details(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получает субъекты пользователя с дополнительной информацией.
        """
        connections = self.get_user_connections(user_id)
        result = []
        
        for connection in connections:
            # Получаем дополнительную информацию
            subject_service = __import__('aistudio.services.subject_service', fromlist=['SubjectService']).SubjectService()
            role_service = __import__('aistudio.services.role_service', fromlist=['RoleService']).RoleService()
            
            subject = subject_service.get_subject_by_id(connection.subject_id)
            role = role_service.get_role_by_id(connection.role_id)
            
            result.append({
                'connection': connection,
                'subject': subject,
                'role': role
            })
        
        return result 