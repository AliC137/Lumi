"""
models/role.py

Содержит описание модели роли для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from aistudio.core.database import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # Наименование роли
    slug = Column(String(10), nullable=False, unique=True)  # Обозначение (owner, editor, viewer)
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True) 