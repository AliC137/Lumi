from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SubjectTypeOut(BaseModel):
    """
    Схема для вывода типа субъекта (классификатора субъектов)
    """
    id: int = Field(..., description="Идентификатор типа субъекта")
    name: str = Field(..., description="Наименование типа субъекта")
    slug: str = Field(..., description="Обозначение типа субъекта")
    created_dt: Optional[datetime] = Field(None, description="Время создания")
    updated_dt: Optional[datetime] = Field(None, description="Время обновления")
    deleted_dt: Optional[datetime] = Field(None, description="Время удаления")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Школа",
                "slug": "school",
                "created_dt": "2024-01-01T00:00:00",
                "updated_dt": "2024-01-01T00:00:00",
                "deleted_dt": None
            }
        } 