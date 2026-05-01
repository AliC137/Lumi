from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SubjectOut(BaseModel):
    """
    Схема для вывода субъекта
    """
    id: int = Field(..., description="Идентификатор субъекта")
    name: str = Field(..., description="Наименование субъекта")
    type_id: int = Field(..., description="Ссылка на тип субъекта")
    parent_id: Optional[int] = Field(None, description="Ссылка на родительский субъект")
    created_dt: Optional[datetime] = Field(None, description="Время создания")
    updated_dt: Optional[datetime] = Field(None, description="Время обновления")
    deleted_dt: Optional[datetime] = Field(None, description="Время удаления")
    
    # Дополнительные поля для иерархии
    subject_type_name: Optional[str] = Field(None, description="Наименование типа субъекта")
    parent_name: Optional[str] = Field(None, description="Наименование родительского субъекта")
    children_count: Optional[int] = Field(0, description="Количество дочерних субъектов")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Московская школа №1",
                "type_id": 1,
                "parent_id": None,
                "created_dt": "2024-01-01T00:00:00",
                "updated_dt": "2024-01-01T00:00:00",
                "deleted_dt": None,
                "subject_type_name": "Школа",
                "parent_name": None,
                "children_count": 5
            }
        } 