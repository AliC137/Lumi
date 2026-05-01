"""
repositories/user_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели пользователя.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime
from aistudio.models.user import User
from aistudio.utils.security import hash_password, verify_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_login(self, login: str):
        return self.db.query(User).filter(User.login == login).first()
    
    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(
            User.id == user_id,
            User.deleted_dt.is_(None)  # Exclude soft-deleted users
        ).first()

    def get_all_active(self):
        return self.db.query(User).filter(
            User.deleted_dt.is_(None)  # Exclude soft-deleted users
        ).all()

    def soft_delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        setattr(user, 'deleted_dt', datetime.now())
        self.db.commit()
        return True

    def create(self, login: str, name: str, password: str, role: str = "user"):
        try:
            user = User(
                login=login,
                name=name,
                password=hash_password(password),
                role=role
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this login already exists")
    
    def authenticate_user(self, login: str, password: str):
        user = self.get_by_login(login)
        if not user:
            return None
        if not verify_password(password, str(user.password)):
            return None
        return user
    
    def update_user(self, user_id: int, **kwargs):
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int):
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True

    def change_user_role(self, user_id: int, new_role: str) -> User:
        """
        Изменяет роль пользователя.
        """
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Валидация роли
        valid_roles = ["user", "admin"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Allowed roles: {valid_roles}")
        
        user.role = new_role
        self.db.commit()
        self.db.refresh(user)
        return user
