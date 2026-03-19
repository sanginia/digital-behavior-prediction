"""
Predictions API endpoints for abandonment risk predictions and interventions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.database import get_db
from ...db.models import Prediction as DBPrediction, Intervention as DBIntervention
from ...schemas.prediction import Prediction as PredictionSchema
from ...services.behavior_service import BehaviorService


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.post("/session/{session_id}", response_model=PredictionSchema, status_code=status.HTTP_201_CREATED)
def create_prediction(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Generates an abandonment risk prediction for a session.

    This runs the prediction model and generates:
    - Abandonment risk score (0.0 to 1.0)
    - Context switch likelihood (0.0 to 1.0)
    - Human-readable explanation
    - Suggested interventions (if risk is high)

    Args:
        session_id: Session ID to predict for
        db: Database session

    Returns:
        Prediction with risk scores and explanation
    """
    try:
        service = BehaviorService(db)
        prediction = service.predict_abandonment(session_id)

        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found or has no data to analyze"
            )

        return PredictionSchema.model_validate(prediction)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating prediction for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prediction: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=List[PredictionSchema])
def get_session_predictions(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves all predictions for a session.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        List of predictions for the session
    """
    try:
        predictions = db.query(DBPrediction).filter(
            DBPrediction.session_id == session_id
        ).order_by(DBPrediction.timestamp.desc()).all()

        return [PredictionSchema.model_validate(p) for p in predictions]

    except Exception as e:
        print(f"Error retrieving predictions for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )


@router.get("/recent", response_model=List[PredictionSchema])
def get_recent_predictions(
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Retrieves recent predictions for a user.

    Args:
        limit: Maximum number of predictions to return (default 20)
        db: Database session
        user_id: User ID from header (defaults to 1 for MVP)

    Returns:
        List of recent predictions
    """
    try:
        if user_id is None:
            user_id = 1

        predictions = db.query(DBPrediction).join(
            DBPrediction.session
        ).filter(
            DBPrediction.session.has(user_id=user_id)
        ).order_by(
            DBPrediction.timestamp.desc()
        ).limit(limit).all()

        return [PredictionSchema.model_validate(p) for p in predictions]

    except Exception as e:
        print(f"Error retrieving recent predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )


@router.get("/{prediction_id}/interventions")
def get_prediction_interventions(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves suggested interventions for a prediction.

    Args:
        prediction_id: Prediction ID
        db: Database session

    Returns:
        List of intervention suggestions
    """
    try:
        interventions = db.query(DBIntervention).filter(
            DBIntervention.prediction_id == prediction_id
        ).all()

        return [
            {
                "id": i.id,
                "suggested_intervention": i.suggested_intervention,
                "rule_triggered": i.rule_triggered,
                "is_displayed": i.is_displayed,
                "displayed_at": i.displayed_at.isoformat() if i.displayed_at else None
            } for i in interventions
        ]

    except Exception as e:
        print(f"Error retrieving interventions for prediction {prediction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interventions: {str(e)}"
        )


@router.put("/interventions/{intervention_id}/mark-displayed", status_code=status.HTTP_200_OK)
def mark_intervention_displayed(
    intervention_id: int,
    db: Session = Depends(get_db)
):
    """
    Marks an intervention as displayed to the user.

    Args:
        intervention_id: Intervention ID
        db: Database session

    Returns:
        Success message
    """
    try:
        from datetime import datetime

        intervention = db.query(DBIntervention).filter(
            DBIntervention.id == intervention_id
        ).first()

        if not intervention:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intervention {intervention_id} not found"
            )

        intervention.is_displayed = True
        intervention.displayed_at = datetime.utcnow()
        db.commit()

        return {"message": "Intervention marked as displayed", "intervention_id": intervention_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error marking intervention {intervention_id} as displayed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark intervention as displayed: {str(e)}"
        )
