from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.event import BrowserEventCreate, BrowserEvent
from schemas.session import Session as SessionSchema
from schemas.prediction import Prediction as PredictionSchema, Intervention as InterventionSchema
from services.behavior_service import BehaviorService
from typing import List

router = APIRouter(prefix="/behavior", tags=["Behavior Modeling"])

# Mock User ID for MVP demo
MOCK_USER_ID = 1

@router.post("/events", response_model=BrowserEvent)
def create_event(event: BrowserEventCreate, db: Session = Depends(get_db)):
    """
    Ingest a new browser event.
    """
    service = BehaviorService(db)
    return service.ingest_event(MOCK_USER_ID, event)

@router.get("/sessions", response_model=List[SessionSchema])
def list_sessions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    List behavioral sessions.
    """
    from db.models import Session as SessionModel
    return db.query(SessionModel).filter(SessionModel.user_id == MOCK_USER_ID).offset(skip).limit(limit).all()

@router.post("/sessions/{session_id}/process", response_model=PredictionSchema)
def process_session(session_id: int, db: Session = Depends(get_db)):
    """
    Compute features and run prediction for a session.
    """
    service = BehaviorService(db)
    snapshot = service.compute_features(session_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Session not found or has no events")
    
    prediction = service.predict_abandonment(snapshot.id)
    return prediction

@router.get("/predictions/latest", response_model=PredictionSchema)
def get_latest_prediction(db: Session = Depends(get_db)):
    """
    Get the most recent behavior prediction.
    """
    from db.models import Prediction as PredictionModel
    prediction = db.query(PredictionModel).order_by(PredictionModel.timestamp.desc()).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions found")
    return prediction

@router.get("/interventions", response_model=List[InterventionSchema])
def list_interventions(db: Session = Depends(get_db)):
    """
    List generated interventions.
    """
    from db.models import Intervention as InterventionModel
    return db.query(InterventionModel).order_by(InterventionModel.timestamp.desc()).all()
