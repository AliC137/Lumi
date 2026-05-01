from pydantic import BaseModel, Field
from typing import Optional


class SubjectTypeCreate(BaseModel):
    """
    Схема для создания типа субъекта (классификатора субъектов)
    """
    name: str = Field(..., min_length=1, max_length=50, description="Наименование типа субъекта")
    slug: str = Field(..., min_length=1, max_length=10, description="Обозначение типа субъекта")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Школа",
                "slug": "school"
            }
        } 