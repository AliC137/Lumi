"""
models/subject.py

Содержит описание модели субъекта для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from aistudio.core.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)  # Ссылка на родительский субъект
    name = Column(String(50), nullable=False)  # Наименование субъекта
    type_id = Column(Integer, ForeignKey("subject_types.id"), nullable=False)  # Ссылка на тип субъекта
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    subject_type = relationship("SubjectType", back_populates="subjects")
    parent = relationship("Subject", remote_side=[id], back_populates="children")
    children = relationship("Subject", back_populates="parent") 