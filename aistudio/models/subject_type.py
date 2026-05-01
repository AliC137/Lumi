"""
models/subject_type.py

Содержит описание модели типа субъекта для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from aistudio.core.database import Base


class SubjectType(Base):
    __tablename__ = "subject_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)  # Наименование типа
    slug = Column(String(10), nullable=False, unique=True)  # Обозначение (school, class, subject, lesson)
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True)
    
    # Связь с субъектами этого типа
    subjects = relationship("Subject", back_populates="subject_type") 