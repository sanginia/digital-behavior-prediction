from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- Pydantic Schemas for Predictions ---

class PredictionBase(BaseModel):
    session_id: int
    abandonment_risk_score: float = Field(..., ge=0.0, le=1.0) # Score between 0.0 and 1.0
    context_switch_likelihood: float = Field(..., ge=0.0, le=1.0) # Score between 0.0 and 1.0
    explanation: Optional[str] = None
    contributing_factors: Optional[str] = None

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int
    timestamp: datetime
    session_id: int # Explicitly include foreign key

    class Config:
        from_attributes = True
