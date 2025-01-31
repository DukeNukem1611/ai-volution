from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KFileResponse(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    highlighted_filename: Optional[str]
    summary: Optional[str]
    category_id: Optional[str]
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True 