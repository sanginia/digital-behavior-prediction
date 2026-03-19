from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- Pydantic Schemas for Users ---

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
