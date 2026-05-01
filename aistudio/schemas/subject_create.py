from pydantic import BaseModel, Field
from typing import Optional


class SubjectCreate(BaseModel):
    """
    Схема для создания субъекта
    """
    name: str = Field(..., min_length=1, max_length=50, description="Наименование субъекта")
    type_id: int = Field(..., description="Ссылка на тип субъекта")
    parent_id: Optional[int] = Field(None, description="Ссылка на родительский субъект")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Московская школа №1",
                "type_id": 1,
                "parent_id": None
            }
        } 