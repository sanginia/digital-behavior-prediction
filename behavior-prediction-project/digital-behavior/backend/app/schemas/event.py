from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

# --- Pydantic Schemas for Browser Events ---

class BrowserEventBase(BaseModel):
    event_type: str
    url: Optional[str] = None
    domain: Optional[str] = None
    title: Optional[str] = None
    window_id: Optional[int] = None
    tab_id: Optional[int] = None
    is_active: Optional[bool] = False

class BrowserEventCreate(BrowserEventBase):
    # We expect the client to send most of this data. Timestamp can be generated server-side if missing.
    # session_id is determined server-side, not provided by client
    timestamp: Optional[datetime] = None

class BrowserEvent(BrowserEventBase):
    id: int
    session_id: int
    timestamp: datetime

    class Config:
        from_attributes = True # For Pydantic v2+, equivalent to orm_mode = True
