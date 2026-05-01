"""
models/user_subject.py

Содержит описание модели связи пользователь-субъект для работы с базой данных (SQLAlchemy ORM).
"""

from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from aistudio.core.database import Base


class UserSubject(Base):
    __tablename__ = "user_subjects"
    subject_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)  # Ссылка на субъекта
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # Ссылка на пользователя
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)  # Ссылка на роль
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_dt = Column(DateTime(timezone=True), nullable=True)
    
    # Связи (используем строковые ссылки для избежания циклических импортов)
    subject = relationship("Subject")
    role = relationship("Role")
    
    # Уникальное ограничение на комбинацию user_id и subject_id
    __table_args__ = (
        UniqueConstraint('user_id', 'subject_id', name='uq_user_subject'),
    ) 