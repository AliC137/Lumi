from pydantic import BaseModel, Field
from typing import Optional


class UserSubjectUpdate(BaseModel):
    """
    Схема для обновления связи пользователь-субъект
    """
    role_id: int = Field(..., description="Новая ссылка на роль")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 2
            }
        } 