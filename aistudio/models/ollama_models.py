from pydantic import BaseModel
from typing import List


class ModelListResponse(BaseModel):
    models: List[str]


class MessageResponse(BaseModel):
    message: str
