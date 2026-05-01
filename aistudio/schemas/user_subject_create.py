from pydantic import BaseModel, Field


class UserSubjectCreate(BaseModel):
    """
    Схема для создания связи пользователь-субъект
    """
    subject_id: int = Field(..., description="Ссылка на субъекта")
    user_id: int = Field(..., description="Ссылка на пользователя")
    role_id: int = Field(..., description="Ссылка на роль")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_id": 1,
                "user_id": 1,
                "role_id": 1
            }
        } 