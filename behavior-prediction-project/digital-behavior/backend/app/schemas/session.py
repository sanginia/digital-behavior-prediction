from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Import specific schemas from other files if needed for nested structures
from .event import BrowserEvent as BrowserEventSchema

# --- Pydantic Schemas for Sessions ---

class SessionBase(BaseModel):
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    active_duration_seconds: float = 0.0
    switch_count: int = 0
    domain_diversity: float = 0.0
    inactivity_gap_seconds: float = 0.0

class SessionCreate(SessionBase):
    # For MVP, we might create a session implicitly when the first event arrives,
    # or require it to be explicit. Assuming explicit creation for now.
    pass

class Session(SessionBase):
    id: int
    user_id: int # Explicitly include foreign key in the schema

    # Optional: include nested schemas if you want to embed related data
    # events: List[BrowserEventSchema] = []

    class Config:
        from_attributes = True

# Schema to represent session data with computed features and predictions (for dashboard)
class SessionWithDetails(Session):
    # Placeholder for features and predictions. These will be joined or fetched separately.
    # features: Optional[List[FeatureSnapshotSchema]] = None # Example if FeatureSnapshotSchema exists
    # predictions: Optional[List[PredictionSchema]] = None # Example if PredictionSchema exists
    pass
