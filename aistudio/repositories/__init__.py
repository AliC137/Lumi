"""
repositories/__init__.py

Фабрика репозиториев и контекстный менеджер для работы с базой данных.
"""

from contextlib import contextmanager
from sqlalchemy.orm import Session
from aistudio.core.database import SessionLocal
from aistudio.repositories.user_repository import UserRepository
from aistudio.repositories.jwt_repository import JWTRepository
from aistudio.repositories.subject_type_repository import SubjectTypeRepository
from aistudio.repositories.subject_repository import SubjectRepository
from aistudio.repositories.role_repository import RoleRepository
from aistudio.repositories.user_subject_repository import UserSubjectRepository


@contextmanager
def get_db_session():
    """
    Контекстный менеджер для работы с сессией базы данных.
    Автоматически закрывает соединение после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RepositoryFactory:
    """
    Фабрика для создания репозиториев с автоматическим управлением сессией БД.
    """
    
    @staticmethod
    def get_user_repository() -> UserRepository:
        """
        Возвращает экземпляр UserRepository с новой сессией БД.
        """
        db = SessionLocal()
        return UserRepository(db)
    
    @staticmethod
    def get_user_repository_with_session(db: Session) -> UserRepository:
        """
        Возвращает экземпляр UserRepository с переданной сессией БД.
        Используется для транзакций, которые должны использовать одну сессию.
        """
        return UserRepository(db)
    
    @staticmethod
    def get_jwt_repository() -> JWTRepository:
        """
        Возвращает экземпляр JWTRepository с новой сессией БД.
        """
        db = SessionLocal()
        return JWTRepository(db)
    
    @staticmethod
    def get_jwt_repository_with_session(db: Session) -> JWTRepository:
        """
        Возвращает экземпляр JWTRepository с переданной сессией БД.
        Используется для транзакций, которые должны использовать одну сессию.
        """
        return JWTRepository(db)
    
    @staticmethod
    def get_subject_type_repository() -> SubjectTypeRepository:
        """
        Возвращает экземпляр SubjectTypeRepository с новой сессией БД.
        """
        db = SessionLocal()
        return SubjectTypeRepository(db)
    
    @staticmethod
    def get_subject_type_repository_with_session(db: Session) -> SubjectTypeRepository:
        """
        Возвращает экземпляр SubjectTypeRepository с переданной сессией БД.
        """
        return SubjectTypeRepository(db)
    
    @staticmethod
    def get_subject_repository() -> SubjectRepository:
        """
        Возвращает экземпляр SubjectRepository с новой сессией БД.
        """
        db = SessionLocal()
        return SubjectRepository(db)
    
    @staticmethod
    def get_subject_repository_with_session(db: Session) -> SubjectRepository:
        """
        Возвращает экземпляр SubjectRepository с переданной сессией БД.
        """
        return SubjectRepository(db)
    
    @staticmethod
    def get_role_repository() -> RoleRepository:
        """
        Возвращает экземпляр RoleRepository с новой сессией БД.
        """
        db = SessionLocal()
        return RoleRepository(db)
    
    @staticmethod
    def get_role_repository_with_session(db: Session) -> RoleRepository:
        """
        Возвращает экземпляр RoleRepository с переданной сессией БД.
        """
        return RoleRepository(db)
    
    @staticmethod
    def get_user_subject_repository() -> UserSubjectRepository:
        """
        Возвращает экземпляр UserSubjectRepository с новой сессией БД.
        """
        db = SessionLocal()
        return UserSubjectRepository(db)
    
    @staticmethod
    def get_user_subject_repository_with_session(db: Session) -> UserSubjectRepository:
        """
        Возвращает экземпляр UserSubjectRepository с переданной сессией БД.
        """
        return UserSubjectRepository(db) 