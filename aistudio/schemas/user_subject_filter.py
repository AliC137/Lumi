from pydantic import BaseModel, Field
from typing import Optional


class UserSubjectFilter(BaseModel):
    """
    Схема для фильтрации связей пользователь-субъект
    """
    user_id: Optional[int] = Field(None, description="Фильтр по пользователю")
    subject_id: Optional[int] = Field(None, description="Фильтр по субъекту")
    role_id: Optional[int] = Field(None, description="Фильтр по роли")
    include_deleted: bool = Field(False, description="Включить удаленные записи")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "subject_id": None,
                "role_id": 1,
                "include_deleted": False
            }
        } 