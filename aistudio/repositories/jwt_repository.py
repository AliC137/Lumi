"""
repositories/jwt_repository.py

Содержит логику взаимодействия с базой данных (CRUD-операции) для модели JWT токенов.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from aistudio.models.jwt_token import JWTToken


class JWTRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, user_id: int, access_token: str, refresh_token: str, 
                    access_expires: datetime, refresh_expires: datetime):
        """
        Создает новую запись JWT токена в базе данных.
        """
        try:
            token_record = JWTToken(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expired_time=access_expires,
                refresh_token_expired_time=refresh_expires
            )
            self.db.add(token_record)
            self.db.commit()
            self.db.refresh(token_record)
            return token_record
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to create token record")

    def get_token_by_user_id(self, user_id: int):
        """
        Получает активный токен пользователя.
        """
        return self.db.query(JWTToken).filter(
            JWTToken.user_id == user_id,
            JWTToken.deleted_dt.is_(None)
        ).first()

    def get_token_by_access_token(self, access_token: str):
        """
        Получает токен по access token.
        """
        return self.db.query(JWTToken).filter(
            JWTToken.access_token == access_token,
            JWTToken.deleted_dt.is_(None)
        ).first()

    def get_token_by_refresh_token(self, refresh_token: str):
        """
        Получает токен по refresh token.
        """
        return self.db.query(JWTToken).filter(
            JWTToken.refresh_token == refresh_token,
            JWTToken.deleted_dt.is_(None)
        ).first()

    def update_tokens(self, token_id: int, access_token: str, refresh_token: str,
                     access_expires: datetime, refresh_expires: datetime):
        """
        Обновляет токены пользователя.
        """
        token = self.db.query(JWTToken).filter(JWTToken.id == token_id).first()
        if not token:
            return None
        
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.access_token_expired_time = access_expires
        token.refresh_token_expired_time = refresh_expires
        
        self.db.commit()
        self.db.refresh(token)
        return token

    def invalidate_token(self, token_id: int):
        """
        Инвалидирует токен (мягкое удаление).
        """
        token = self.db.query(JWTToken).filter(JWTToken.id == token_id).first()
        if not token:
            return False
        
        token.deleted_dt = datetime.now()
        self.db.commit()
        return True

    def invalidate_user_tokens(self, user_id: int):
        """
        Инвалидирует все токены пользователя.
        """
        tokens = self.db.query(JWTToken).filter(
            JWTToken.user_id == user_id,
            JWTToken.deleted_dt.is_(None)
        ).all()
        
        for token in tokens:
            token.deleted_dt = datetime.now()
        
        self.db.commit()
        return len(tokens) 