from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserSubjectOut(BaseModel):
    """
    Схема для вывода связи пользователь-субъект
    """
    subject_id: int = Field(..., description="Ссылка на субъекта")
    user_id: int = Field(..., description="Ссылка на пользователя")
    role_id: int = Field(..., description="Ссылка на роль")
    created_dt: Optional[datetime] = Field(None, description="Время создания")
    updated_dt: Optional[datetime] = Field(None, description="Время обновления")
    deleted_dt: Optional[datetime] = Field(None, description="Время удаления")
    
    # Дополнительные поля для удобства
    subject_name: Optional[str] = Field(None, description="Наименование субъекта")
    user_name: Optional[str] = Field(None, description="Имя пользователя")
    user_login: Optional[str] = Field(None, description="Логин пользователя")
    role_name: Optional[str] = Field(None, description="Наименование роли")
    role_slug: Optional[str] = Field(None, description="Обозначение роли")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "subject_id": 1,
                "user_id": 1,
                "role_id": 1,
                "created_dt": "2024-01-01T00:00:00",
                "updated_dt": "2024-01-01T00:00:00",
                "deleted_dt": None,
                "subject_name": "Московская школа №1",
                "user_name": "Иван Иванов",
                "user_login": "ivan@example.com",
                "role_name": "Владелец",
                "role_slug": "owner"
            }
        } 