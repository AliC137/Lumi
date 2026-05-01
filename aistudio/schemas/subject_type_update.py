from pydantic import BaseModel, Field
from typing import Optional


class SubjectTypeUpdate(BaseModel):
    """
    Схема для обновления типа субъекта
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Наименование типа субъекта")
    slug: Optional[str] = Field(None, min_length=1, max_length=10, description="Обозначение типа субъекта")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Обновленная школа",
                "slug": "updated_school"
            }
        } 