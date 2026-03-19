"""
Events API endpoints for browser event ingestion and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.database import get_db
from ...db.models import BrowserEvent as DBBrowserEvent
from ...schemas.event import BrowserEventCreate, BrowserEvent as BrowserEventSchema
from ...services.behavior_service import BehaviorService


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.post("/", response_model=BrowserEventSchema, status_code=status.HTTP_201_CREATED)
def create_browser_event(
    event: BrowserEventCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Ingests a new browser event from the Chrome extension.

    The event is automatically assigned to a session (either existing or new).
    Sessions are determined by a 30-minute timeout window.

    Args:
        event: Browser event data (event_type, url, domain, title, tab_id, etc.)
        db: Database session
        user_id: User ID from header (defaults to 1 for MVP single-user mode)

    Returns:
        The created browser event with session assignment
    """
    try:
        # For MVP, use user_id 1 if not provided (single-user mode)
        if user_id is None:
            user_id = 1

        # Initialize behavior service
        service = BehaviorService(db)

        # Ensure user exists (for MVP)
        service.ensure_user_exists("demo_user")

        # Ingest the event (service handles session assignment)
        db_event = service.ingest_event(user_id, event)

        return BrowserEventSchema.model_validate(db_event)

    except Exception as e:
        db.rollback()
        print(f"Error ingesting event: {e}")  # Replace with proper logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest browser event: {str(e)}"
        )


@router.post("/batch", response_model=List[BrowserEventSchema], status_code=status.HTTP_201_CREATED)
def create_browser_events_batch(
    events: List[BrowserEventCreate],
    db: Session = Depends(get_db),
    user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Batch ingests multiple browser events.

    Useful for the extension to send accumulated events at intervals.

    Args:
        events: List of browser events
        db: Database session
        user_id: User ID from header

    Returns:
        List of created browser events
    """
    try:
        if user_id is None:
            user_id = 1

        service = BehaviorService(db)
        service.ensure_user_exists("demo_user")

        created_events = []
        for event in events:
            db_event = service.ingest_event(user_id, event)
            created_events.append(BrowserEventSchema.model_validate(db_event))

        return created_events

    except Exception as e:
        db.rollback()
        print(f"Error ingesting batch events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest browser events: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=List[BrowserEventSchema])
def get_events_for_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves all browser events for a given session.

    Args:
        session_id: The ID of the session
        db: Database session

    Returns:
        List of browser events for the session
    """
    try:
        events = db.query(DBBrowserEvent).filter(
            DBBrowserEvent.session_id == session_id
        ).order_by(DBBrowserEvent.timestamp.asc()).all()

        return [BrowserEventSchema.model_validate(event) for event in events]

    except Exception as e:
        print(f"Error retrieving events for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve browser events: {str(e)}"
        )


@router.get("/recent", response_model=List[BrowserEventSchema])
def get_recent_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Header(None, alias="X-User-ID")
):
    """
    Retrieves recent browser events for a user.

    Args:
        limit: Maximum number of events to return (default 50)
        db: Database session
        user_id: User ID from header

    Returns:
        List of recent browser events
    """
    try:
        if user_id is None:
            user_id = 1

        events = db.query(DBBrowserEvent).join(
            DBBrowserEvent.session
        ).filter(
            DBBrowserEvent.session.has(user_id=user_id)
        ).order_by(
            DBBrowserEvent.timestamp.desc()
        ).limit(limit).all()

        return [BrowserEventSchema.model_validate(event) for event in events]

    except Exception as e:
        print(f"Error retrieving recent events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent events: {str(e)}"
        )
