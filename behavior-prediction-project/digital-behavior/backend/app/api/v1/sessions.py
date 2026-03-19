"""
Sessions API endpoints for browsing session management and analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.database import get_db
from ...db.models import Session as DBSession, BrowserEvent, FeatureSnapshot, Prediction
from ...schemas.session import Session as SessionSchema, SessionWithDetails
from ...services.behavior_service import BehaviorService


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


@router.get("/", response_model=List[SessionSchema])
def get_sessions(
    limit: int = 20,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Retrieves recent sessions for a user.

    Args:
        limit: Maximum number of sessions to return (default 20)
        db: Database session
        user_id: User ID from header (defaults to 1 for MVP)

    Returns:
        List of recent sessions
    """
    try:
        if user_id is None:
            user_id = 1

        service = BehaviorService(db)
        sessions = service.get_recent_sessions(user_id, limit)

        return [SessionSchema.model_validate(session) for session in sessions]

    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionSchema)
def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific session by ID.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Session details
    """
    try:
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return SessionSchema.model_validate(session)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@router.get("/{session_id}/analysis")
def get_session_analysis(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves comprehensive analysis for a session including:
    - Session metadata
    - Browser events
    - Feature snapshot
    - Predictions

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Dictionary with session analysis data
    """
    try:
        service = BehaviorService(db)
        analysis = service.get_session_with_analysis(session_id)

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Convert SQLAlchemy objects to dicts for JSON serialization
        return {
            "session": SessionSchema.model_validate(analysis["session"]).model_dump(),
            "events_count": len(analysis["events"]),
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "domain": e.domain,
                    "timestamp": e.timestamp.isoformat(),
                    "tab_id": e.tab_id
                } for e in analysis["events"]
            ],
            "features": {
                "session_length_minutes": analysis["features"].session_length_minutes,
                "tab_switch_frequency": analysis["features"].tab_switch_frequency,
                "avg_time_per_tab_seconds": analysis["features"].avg_time_per_tab_seconds,
                "volatility_score": analysis["features"].volatility_score,
                "task_continuity_estimate": analysis["features"].task_continuity_estimate,
                "unique_domains_count": analysis["features"].unique_domains_count,
                "late_night_behavior": analysis["features"].late_night_behavior
            } if analysis["features"] else None,
            "predictions": [
                {
                    "id": p.id,
                    "abandonment_risk_score": p.abandonment_risk_score,
                    "context_switch_likelihood": p.context_switch_likelihood,
                    "explanation": p.explanation,
                    "timestamp": p.timestamp.isoformat()
                } for p in analysis["predictions"]
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving session analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session analysis: {str(e)}"
        )


@router.post("/{session_id}/compute-features", status_code=status.HTTP_201_CREATED)
def compute_session_features(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually triggers feature computation for a session.

    This is typically done automatically, but can be triggered manually
    for testing or recomputation.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Computed feature snapshot
    """
    try:
        service = BehaviorService(db)
        snapshot = service.compute_features(session_id)

        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found or has no events"
            )

        return {
            "id": snapshot.id,
            "session_id": snapshot.session_id,
            "session_length_minutes": snapshot.session_length_minutes,
            "tab_switch_frequency": snapshot.tab_switch_frequency,
            "avg_time_per_tab_seconds": snapshot.avg_time_per_tab_seconds,
            "volatility_score": snapshot.volatility_score,
            "task_continuity_estimate": snapshot.task_continuity_estimate,
            "unique_domains_count": snapshot.unique_domains_count,
            "late_night_behavior": snapshot.late_night_behavior
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error computing features for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute features: {str(e)}"
        )
