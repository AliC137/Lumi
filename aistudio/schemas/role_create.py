from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    """
    Схема для создания роли
    """
    name: str = Field(..., min_length=1, max_length=50, description="Наименование роли")
    slug: str = Field(..., min_length=1, max_length=10, description="Обозначение роли")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Владелец",
                "slug": "owner"
            }
        } 