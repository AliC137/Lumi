"""
services/user_service.py

Содержит бизнес-логику, связанную с пользователями.
Вызывает методы из репозиториев и возвращает данные контроллерам.
"""

from datetime import datetime, timedelta, UTC
from aistudio.models.user import User
from aistudio.schemas.user_create import UserCreate
from aistudio.repositories import RepositoryFactory
from aistudio.utils.jwt_utils import create_access_token, create_refresh_token


class UserService:
    """
    Сервис для работы с пользователями.
    Использует фабрику репозиториев для получения доступа к данным.
    """

    def register_user(self, user_data: UserCreate) -> User:
        """
        Регистрирует нового пользователя.
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            if repo.get_by_login(user_data.login):
                raise ValueError("User with this login already exists")
            return repo.create(user_data.login, user_data.name, user_data.password)
        finally:
            repo.db.close()
    
    def get_user_by_id(self, user_id: int) -> User:
        """
        Получает пользователя по ID.
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            user = repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            return user
        finally:
            repo.db.close()
    
    def get_all_users(self) -> list[User]:
        """
        Получает всех активных пользователей.
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            return repo.get_all_active()
        finally:
            repo.db.close()
    
    def soft_delete_user(self, user_id: int) -> bool:
        """
        Мягко удаляет пользователя (устанавливает deleted_dt).
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            success = repo.soft_delete(user_id)
            if not success:
                raise ValueError("User not found or already deleted")
            return True
        finally:
            repo.db.close()

    def authenticate_user(self, login: str, password: str) -> User | None:
        """
        Аутентифицирует пользователя по логину и паролю.
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            return repo.authenticate_user(login, password)
        finally:
            repo.db.close()

    def create_user_tokens(self, user: User) -> dict:
        """
        Создает access и refresh токены для пользователя и сохраняет их в БД.
        """
        # Создаем токены
        access_token = create_access_token({
            "sub": user.login,
            "user_id": user.id,
            "role": user.role
        })
        
        refresh_token = create_refresh_token({
            "sub": user.login,
            "user_id": user.id,
            "role": user.role
        })
        
        # Вычисляем время истечения
        access_expires = datetime.now(UTC) + timedelta(minutes=30)
        refresh_expires = datetime.now(UTC) + timedelta(days=7)
        
        # Сохраняем в БД
        jwt_repo = RepositoryFactory.get_jwt_repository()
        try:
            # Инвалидируем старые токены пользователя
            jwt_repo.invalidate_user_tokens(user.id)
            
            # Создаем новые токены
            jwt_repo.create_token(
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                access_expires=access_expires,
                refresh_expires=refresh_expires
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        finally:
            jwt_repo.db.close()

    def refresh_user_tokens(self, refresh_token: str) -> dict | None:
        """
        Обновляет токены пользователя по refresh токену.
        """
        from aistudio.utils.jwt_utils import decode_refresh_token, is_token_expired
        
        # Проверяем refresh токен
        payload = decode_refresh_token(refresh_token)
        if not payload or is_token_expired(refresh_token, is_refresh=True):
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        # Получаем пользователя
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Проверяем, что refresh токен существует в БД
        jwt_repo = RepositoryFactory.get_jwt_repository()
        try:
            token_record = jwt_repo.get_token_by_refresh_token(refresh_token)
            if not token_record:
                return None
            
            # Создаем новые токены
            return self.create_user_tokens(user)
        finally:
            jwt_repo.db.close()

    def logout_user(self, access_token: str) -> bool:
        """
        Инвалидирует токен пользователя (логаут).
        Всегда возвращает True, даже если токен не найден.
        """
        jwt_repo = RepositoryFactory.get_jwt_repository()
        try:
            token_record = jwt_repo.get_token_by_access_token(access_token)
            if token_record:
                jwt_repo.invalidate_token(token_record.id)
            return True  # Всегда возвращаем True
        finally:
            jwt_repo.db.close()

    def change_user_role(self, user_id: int, new_role: str) -> User:
        """
        Изменяет роль пользователя. Только для админов.
        """
        repo = RepositoryFactory.get_user_repository()
        try:
            return repo.change_user_role(user_id, new_role)
        finally:
            repo.db.close()

    def update_last_login(self, user_id: int) -> None:
        """
        Updates the last_login timestamp for a user.
        Called after successful authentication.
        """
        from datetime import datetime, timezone
        repo = RepositoryFactory.get_user_repository()
        try:
            user = repo.get_by_id(user_id)
            if user:
                user.last_login = datetime.now(timezone.utc)
                repo.db.commit()
        finally:
            repo.db.close()
