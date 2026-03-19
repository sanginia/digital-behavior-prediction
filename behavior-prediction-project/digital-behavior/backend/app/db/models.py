from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Assuming a simple single-user mode for MVP, or basic user identification
    username = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user")


class BrowserEvent(Base):
    __tablename__ = "browser_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String, index=True, nullable=False)  # e.g., "tab_focus", "tab_open", "tab_close", "url_change"
    url = Column(String, index=True)
    domain = Column(String, index=True)
    title = Column(String)
    window_id = Column(Integer)
    tab_id = Column(Integer)
    is_active = Column(Boolean, default=False) # Whether the tab was active at the time of the event

    # Relationships
    session = relationship("Session", back_populates="events")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    active_duration_seconds = Column(Float, default=0.0)
    switch_count = Column(Integer, default=0)
    domain_diversity = Column(Float, default=0.0) # e.g., number of unique domains visited
    inactivity_gap_seconds = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="sessions")
    events = relationship("BrowserEvent", back_populates="session")
    features = relationship("FeatureSnapshot", back_populates="session")
    predictions = relationship("Prediction", back_populates="session")


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # Feature engineering outputs
    session_length_minutes = Column(Float)
    avg_time_per_tab_seconds = Column(Float)
    tab_switch_frequency = Column(Float) # switches per minute
    repeated_revisits = Column(Integer)
    unique_domains_count = Column(Integer)
    inactivity_gap_detected = Column(Boolean, default=False)
    late_night_behavior = Column(Boolean, default=False)
    volatility_score = Column(Float) # based on frequent switching
    task_continuity_estimate = Column(Float)

    # Relationships
    session = relationship("Session", back_populates="features")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    abandonment_risk_score = Column(Float, nullable=False) # 0.0 to 1.0
    context_switch_likelihood = Column(Float, nullable=False) # 0.0 to 1.0
    explanation = Column(Text) # Human-readable explanation
    contributing_factors = Column(String) # e.g., "switch_frequency,avg_tab_duration"

    # Relationships
    session = relationship("Session", back_populates="predictions")
    interventions = relationship("Intervention", back_populates="prediction")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    suggested_intervention = Column(String, nullable=False) # e.g., "reduce task scope", "take a short break"
    rule_triggered = Column(String) # Which rule resulted in this intervention
    is_displayed = Column(Boolean, default=False)
    displayed_at = Column(DateTime(timezone=True))

    # Relationships
    prediction = relationship("Prediction", back_populates="interventions")
