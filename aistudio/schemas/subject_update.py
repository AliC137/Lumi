from pydantic import BaseModel, Field
from typing import Optional


class SubjectUpdate(BaseModel):
    """
    Схема для обновления субъекта
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Наименование субъекта")
    type_id: Optional[int] = Field(None, description="Ссылка на тип субъекта")
    parent_id: Optional[int] = Field(None, description="Ссылка на родительский субъект")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Обновленная школа №1",
                "type_id": 1,
                "parent_id": None
            }
        } 