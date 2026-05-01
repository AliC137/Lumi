from pydantic import BaseModel, Field
from typing import Optional


class SubjectFilter(BaseModel):
    """
    Схема для фильтрации субъектов
    """
    name: Optional[str] = Field(None, description="Фильтр по наименованию (поиск по подстроке)")
    type_id: Optional[int] = Field(None, description="Фильтр по типу субъекта")
    parent_id: Optional[int] = Field(None, description="Фильтр по родительскому субъекту")
    include_deleted: bool = Field(False, description="Включить удаленные записи")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "школа",
                "type_id": 1,
                "parent_id": None,
                "include_deleted": False
            }
        } 