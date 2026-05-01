from pydantic import BaseModel, Field
from typing import Optional


class RoleUpdate(BaseModel):
    """
    Схема для обновления роли
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Наименование роли")
    slug: Optional[str] = Field(None, min_length=1, max_length=10, description="Обозначение роли")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Обновленная роль",
                "slug": "updated_role"
            }
        } 