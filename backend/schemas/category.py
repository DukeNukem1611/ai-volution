from pydantic import BaseModel
from datetime import datetime

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True 