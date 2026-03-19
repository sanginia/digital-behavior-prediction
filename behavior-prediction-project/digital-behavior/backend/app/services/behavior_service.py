"""
BehaviorService: Core business logic for behavioral analysis and predictions.

This service handles:
- Event ingestion and session management
- Feature engineering from raw browser events
- Abandonment risk prediction
- Intervention generation
"""

from sqlalchemy.orm import Session as DBSession
from ..db.models import BrowserEvent, Session, FeatureSnapshot, Prediction, Intervention, User
from ..schemas.event import BrowserEventCreate
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from collections import Counter


class BehaviorService:
    """Service layer for behavioral modeling and prediction."""

    def __init__(self, db: DBSession):
        self.db = db
        self.session_timeout_minutes = 30  # Time gap to consider a new session

    @staticmethod
    def _ensure_timezone_aware(dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware (UTC)."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def ingest_event(self, user_id: int, event_in: BrowserEventCreate) -> BrowserEvent:
        """
        Ingests a new browser event and assigns it to a session.

        Args:
            user_id: ID of the user generating the event
            event_in: Browser event data from the extension

        Returns:
            The created BrowserEvent database object
        """
        # Find or create a session for this event
        session = self._get_or_create_session(user_id, event_in.timestamp or datetime.now(timezone.utc))

        # Create the event linked to the session
        db_event = BrowserEvent(
            session_id=session.id,
            event_type=event_in.event_type,
            url=event_in.url,
            domain=event_in.domain,
            title=event_in.title,
            tab_id=event_in.tab_id,
            window_id=event_in.window_id,
            is_active=event_in.is_active,
            timestamp=event_in.timestamp or datetime.now(timezone.utc)
        )
        self.db.add(db_event)
        self.db.flush()

        # Update session metadata with this new event
        self._update_session_metadata(session)

        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def _get_or_create_session(self, user_id: int, event_time: datetime) -> Session:
        """
        Finds the most recent active session or creates a new one.

        Sessions are considered separate if more than session_timeout_minutes
        have elapsed since the last event.

        Args:
            user_id: User ID
            event_time: Timestamp of the current event

        Returns:
            Active or newly created Session object
        """
        # Look for the most recent session for this user
        latest_session = self.db.query(Session).filter(
            Session.user_id == user_id
        ).order_by(Session.start_time.desc()).first()

        # If session exists and within timeout window, reuse it
        if latest_session and latest_session.end_time:
            # Ensure both datetimes are timezone-aware for comparison
            event_time_aware = self._ensure_timezone_aware(event_time)
            end_time_aware = self._ensure_timezone_aware(latest_session.end_time)

            time_since_last_event = event_time_aware - end_time_aware
            if time_since_last_event < timedelta(minutes=self.session_timeout_minutes):
                # Update end time
                latest_session.end_time = event_time_aware
                return latest_session

        # Create a new session
        new_session = Session(
            user_id=user_id,
            start_time=event_time,
            end_time=event_time,
            active_duration_seconds=0.0,
            switch_count=0,
            domain_diversity=0.0,
            inactivity_gap_seconds=0.0
        )
        self.db.add(new_session)
        self.db.flush()
        return new_session

    def _update_session_metadata(self, session: Session):
        """
        Updates session-level aggregate statistics.

        Args:
            session: Session to update
        """
        events = self.db.query(BrowserEvent).filter(
            BrowserEvent.session_id == session.id
        ).order_by(BrowserEvent.timestamp.asc()).all()

        if not events:
            return

        # Update session time boundaries
        session.end_time = events[-1].timestamp
        duration_seconds = (session.end_time - session.start_time).total_seconds()
        session.active_duration_seconds = duration_seconds

        # Count tab switches: when tab_id changes between consecutive events
        switch_count = 0
        last_tab_id = None
        unique_domains = set()

        for event in events:
            if last_tab_id is not None and event.tab_id != last_tab_id:
                switch_count += 1
            last_tab_id = event.tab_id
            if event.domain:
                unique_domains.add(event.domain)

        session.switch_count = switch_count

        # Domain diversity: ratio of unique domains to total events
        if len(events) > 0:
            session.domain_diversity = len(unique_domains) / len(events)

        # Detect inactivity gaps: longest gap between consecutive events
        max_gap = 0.0
        for i in range(1, len(events)):
            gap = (events[i].timestamp - events[i-1].timestamp).total_seconds()
            if gap > max_gap:
                max_gap = gap
        session.inactivity_gap_seconds = max_gap

    def compute_features(self, session_id: int) -> Optional[FeatureSnapshot]:
        """
        Generates a comprehensive feature snapshot for a session.

        This extracts time-series and aggregate features that feed into
        the prediction model.

        Args:
            session_id: ID of the session to analyze

        Returns:
            FeatureSnapshot object or None if session not found
        """
        session = self.db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return None

        events = self.db.query(BrowserEvent).filter(
            BrowserEvent.session_id == session_id
        ).order_by(BrowserEvent.timestamp.asc()).all()

        if not events:
            return None

        # Calculate session length in minutes
        duration_seconds = session.active_duration_seconds or 1.0
        session_length_minutes = duration_seconds / 60.0

        # Tab switch frequency (switches per minute)
        tab_switch_frequency = session.switch_count / max(session_length_minutes, 0.1)

        # Average time per tab
        avg_time_per_tab_seconds = 0.0
        if len(events) > 1:
            time_diffs = []
            for i in range(len(events) - 1):
                diff = (events[i+1].timestamp - events[i].timestamp).total_seconds()
                time_diffs.append(diff)
            if time_diffs:
                avg_time_per_tab_seconds = sum(time_diffs) / len(time_diffs)

        # Repeated revisits: how many domains were visited more than once
        domain_counts = Counter(e.domain for e in events if e.domain)
        repeated_revisits = sum(1 for count in domain_counts.values() if count > 1)

        # Unique domains count
        unique_domains_count = len(domain_counts)

        # Inactivity gap detection (boolean)
        inactivity_gap_detected = session.inactivity_gap_seconds > 300  # 5 minutes

        # Late night behavior: between 11 PM and 5 AM
        hour = session.start_time.hour
        late_night_behavior = (hour >= 23 or hour <= 5)

        # Volatility score: combination of switch frequency and time variance
        volatility_score = tab_switch_frequency
        if len(events) > 2 and avg_time_per_tab_seconds > 0:
            time_diffs = [(events[i+1].timestamp - events[i].timestamp).total_seconds()
                         for i in range(len(events) - 1)]
            std_dev = (sum((x - avg_time_per_tab_seconds) ** 2 for x in time_diffs) / len(time_diffs)) ** 0.5
            volatility_score += std_dev / (avg_time_per_tab_seconds + 1)

        # Task continuity estimate: inverse of switching rate
        task_continuity_estimate = 1.0 / (1.0 + tab_switch_frequency)

        # Create feature snapshot
        snapshot = FeatureSnapshot(
            session_id=session_id,
            session_length_minutes=session_length_minutes,
            avg_time_per_tab_seconds=avg_time_per_tab_seconds,
            tab_switch_frequency=tab_switch_frequency,
            repeated_revisits=repeated_revisits,
            unique_domains_count=unique_domains_count,
            inactivity_gap_detected=inactivity_gap_detected,
            late_night_behavior=late_night_behavior,
            volatility_score=volatility_score,
            task_continuity_estimate=task_continuity_estimate
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def predict_abandonment(self, session_id: int) -> Optional[Prediction]:
        """
        Generates an abandonment risk prediction for a session.

        Uses a weighted scoring model to predict:
        - Abandonment risk score (0.0 to 1.0)
        - Context switch likelihood (0.0 to 1.0)
        - Human-readable explanation

        Args:
            session_id: Session to predict for

        Returns:
            Prediction object or None if session not found
        """
        # Get or compute features
        snapshot = self.db.query(FeatureSnapshot).filter(
            FeatureSnapshot.session_id == session_id
        ).order_by(FeatureSnapshot.timestamp.desc()).first()

        if not snapshot:
            snapshot = self.compute_features(session_id)

        if not snapshot:
            return None

        # Weighted scoring model for abandonment risk
        risk_score = 0.0
        factors = []

        # Factor 1: High switching frequency (weight: 0.3)
        if snapshot.tab_switch_frequency > 3.0:  # More than 3 switches/min
            risk_score += 0.3
            factors.append("high_switching_frequency")
        elif snapshot.tab_switch_frequency > 1.5:  # Moderate switching
            risk_score += 0.15
            factors.append("moderate_switching_frequency")

        # Factor 2: Volatility score (weight: 0.25)
        if snapshot.volatility_score > 5.0:
            risk_score += 0.25
            factors.append("elevated_volatility")
        elif snapshot.volatility_score > 3.0:
            risk_score += 0.15
            factors.append("moderate_volatility")

        # Factor 3: Short tab dwell time (weight: 0.2)
        if snapshot.avg_time_per_tab_seconds < 10:
            risk_score += 0.2
            factors.append("very_short_tab_duration")
        elif snapshot.avg_time_per_tab_seconds < 30:
            risk_score += 0.1
            factors.append("short_tab_duration")

        # Factor 4: Late night behavior (weight: 0.15)
        if snapshot.late_night_behavior:
            risk_score += 0.15
            factors.append("late_night_session")

        # Factor 5: Inactivity gaps (weight: 0.1)
        if snapshot.inactivity_gap_detected:
            risk_score += 0.1
            factors.append("inactivity_gap")

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        # Context switch likelihood based on switch frequency
        context_switch_likelihood = min(snapshot.tab_switch_frequency / 10.0, 1.0)

        # Generate human-readable explanation
        if risk_score > 0.6:
            explanation = (
                f"High abandonment risk detected. "
                f"Contributing factors: {', '.join(factors)}. "
                f"Your attention patterns suggest frequent task switching and fragmented focus."
            )
        elif risk_score > 0.3:
            explanation = (
                f"Moderate abandonment risk. "
                f"Factors: {', '.join(factors)}. "
                f"Some signs of distraction, but task continuity is maintained."
            )
        else:
            explanation = "Behavior appears stable with good task continuity."

        # Create prediction record
        prediction = Prediction(
            session_id=session_id,
            abandonment_risk_score=risk_score,
            context_switch_likelihood=context_switch_likelihood,
            explanation=explanation,
            contributing_factors=','.join(factors)
        )

        self.db.add(prediction)
        self.db.flush()

        # Generate intervention if risk is significant
        if risk_score > 0.5:
            self._generate_intervention(prediction)

        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def _generate_intervention(self, prediction: Prediction):
        """
        Generates rule-based interventions based on prediction risk.

        Args:
            prediction: Prediction object to generate intervention for
        """
        risk_score = prediction.abandonment_risk_score

        # Select intervention based on risk level
        if risk_score > 0.8:
            suggested_intervention = "Switch to a lower-cognitive-load task or take a break"
            rule_triggered = "high_risk_threshold"
        elif risk_score > 0.6:
            suggested_intervention = "Take a 5-minute break to reset your focus"
            rule_triggered = "moderate_risk_threshold"
        else:
            suggested_intervention = "Continue for 10 more minutes, then reassess"
            rule_triggered = "low_risk_threshold"

        intervention = Intervention(
            prediction_id=prediction.id,
            suggested_intervention=suggested_intervention,
            rule_triggered=rule_triggered,
            is_displayed=False
        )

        self.db.add(intervention)
        return intervention

    def get_session_with_analysis(self, session_id: int) -> Optional[Dict]:
        """
        Retrieves a session with its events, features, and predictions.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session data and analysis, or None
        """
        session = self.db.query(Session).filter(Session.id == session_id).first()
        if not session:
            return None

        events = self.db.query(BrowserEvent).filter(
            BrowserEvent.session_id == session_id
        ).order_by(BrowserEvent.timestamp.asc()).all()

        features = self.db.query(FeatureSnapshot).filter(
            FeatureSnapshot.session_id == session_id
        ).order_by(FeatureSnapshot.timestamp.desc()).first()

        predictions = self.db.query(Prediction).filter(
            Prediction.session_id == session_id
        ).order_by(Prediction.timestamp.desc()).all()

        return {
            "session": session,
            "events": events,
            "features": features,
            "predictions": predictions
        }

    def get_recent_sessions(self, user_id: int, limit: int = 10) -> List[Session]:
        """
        Retrieves recent sessions for a user.

        Args:
            user_id: User ID
            limit: Maximum number of sessions to return

        Returns:
            List of Session objects
        """
        return self.db.query(Session).filter(
            Session.user_id == user_id
        ).order_by(Session.start_time.desc()).limit(limit).all()

    def ensure_user_exists(self, username: str = "demo_user") -> User:
        """
        Ensures a user exists in the database (for MVP single-user mode).

        Args:
            username: Username to find or create

        Returns:
            User object
        """
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user
