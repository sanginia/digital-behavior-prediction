"""
Seed script for generating demo data for Digital Behavior Twin

This script generates realistic browsing sessions, events, features, and predictions
for testing and demonstration purposes.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta, timezone
import random
from app.db.database import SessionLocal, engine
from app.db.models import Base, User, BrowserEvent, Session, FeatureSnapshot, Prediction, Intervention
from app.services.behavior_service import BehaviorService


# Demo browsing patterns
DOMAINS = [
    'github.com', 'stackoverflow.com', 'docs.python.org', 'medium.com',
    'twitter.com', 'youtube.com', 'reddit.com', 'news.ycombinator.com',
    'linkedin.com', 'google.com', 'wikipedia.org', 'dev.to',
]

EVENT_TYPES = ['tab_activated', 'tab_created', 'tab_updated', 'tab_closed', 'window_focused']

TITLES = [
    'Python Tutorial - Documentation',
    'How to build a web application',
    'Latest tech news',
    'Stack Overflow - Python question',
    'GitHub Repository',
    'YouTube - Programming tutorial',
    'Reddit - Programming discussion',
    'LinkedIn Feed',
    'Google Search Results',
]


def create_demo_user(db: SessionLocal) -> User:
    """Create or get demo user"""
    user = db.query(User).filter(User.username == 'demo_user').first()
    if not user:
        user = User(username='demo_user')
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created demo user (ID: {user.id})")
    else:
        print(f"✓ Demo user exists (ID: {user.id})")
    return user


def generate_session_events(
    db: SessionLocal,
    user_id: int,
    start_time: datetime,
    duration_minutes: int,
    num_events: int,
    risk_profile: str = 'normal'
) -> Session:
    """Generate a realistic browsing session with events"""

    # Adjust behavior based on risk profile
    if risk_profile == 'high_risk':
        # More frequent switching, shorter dwell times
        switch_probability = 0.7
        avg_dwell_time = 20  # seconds
    elif risk_profile == 'low_risk':
        # Less switching, longer dwell times
        switch_probability = 0.2
        avg_dwell_time = 180  # seconds
    else:  # normal
        switch_probability = 0.4
        avg_dwell_time = 90  # seconds

    service = BehaviorService(db)

    current_time = start_time
    current_domain = random.choice(DOMAINS)
    current_tab_id = 1000
    current_window_id = 1

    # Create events
    for i in range(num_events):
        # Decide if we switch tabs
        if random.random() < switch_probability:
            current_domain = random.choice(DOMAINS)
            current_tab_id += 1
            event_type = 'tab_activated'
        else:
            event_type = random.choice(['tab_updated', 'tab_activated'])

        # Create event
        event_data = type('EventData', (), {
            'event_type': event_type,
            'url': f'https://{current_domain}/page{random.randint(1, 100)}',
            'domain': current_domain,
            'title': random.choice(TITLES),
            'tab_id': current_tab_id,
            'window_id': current_window_id,
            'is_active': True,
            'timestamp': current_time
        })()

        service.ingest_event(user_id, event_data)

        # Advance time
        time_advance = random.expovariate(1.0 / avg_dwell_time)
        current_time += timedelta(seconds=max(5, min(300, time_advance)))

        # Stop if we've exceeded duration
        if (current_time - start_time).total_seconds() > duration_minutes * 60:
            break

    # Get the created session
    session = db.query(Session).filter(
        Session.user_id == user_id
    ).order_by(Session.start_time.desc()).first()

    return session


def generate_demo_data(num_sessions: int = 10):
    """Generate demo data"""

    print("\n" + "="*60)
    print("Digital Behavior Twin - Demo Data Generator")
    print("="*60 + "\n")

    # Initialize database
    db = SessionLocal()

    try:
        # Drop and recreate tables (WARNING: This deletes all existing data)
        print("⚠ Recreating database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created\n")

        # Create demo user
        user = create_demo_user(db)

        # Generate sessions
        print(f"\nGenerating {num_sessions} demo sessions...")
        print("-" * 60)

        now = datetime.now(timezone.utc)
        service = BehaviorService(db)

        for i in range(num_sessions):
            # Vary session parameters
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            start_time = now - timedelta(days=days_ago, hours=hours_ago)

            duration_minutes = random.randint(5, 60)
            num_events = random.randint(10, 100)

            # Mix of risk profiles
            if i < num_sessions // 3:
                risk_profile = 'high_risk'
            elif i < 2 * num_sessions // 3:
                risk_profile = 'normal'
            else:
                risk_profile = 'low_risk'

            print(f"\nSession {i+1}/{num_sessions}: {risk_profile}")
            print(f"  Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Duration: {duration_minutes}min, Events: {num_events}")

            # Generate session
            session = generate_session_events(
                db, user.id, start_time, duration_minutes, num_events, risk_profile
            )

            if session:
                # Compute features
                features = service.compute_features(session.id)
                print(f"  ✓ Features computed")

                # Generate prediction
                prediction = service.predict_abandonment(session.id)
                if prediction:
                    print(f"  ✓ Prediction created (risk: {prediction.abandonment_risk_score:.2f})")

        print("\n" + "="*60)
        print("✓ Demo data generation completed!")
        print("="*60)

        # Print summary
        total_sessions = db.query(Session).count()
        total_events = db.query(BrowserEvent).count()
        total_predictions = db.query(Prediction).count()
        total_interventions = db.query(Intervention).count()

        print("\nSummary:")
        print(f"  Users: 1")
        print(f"  Sessions: {total_sessions}")
        print(f"  Events: {total_events}")
        print(f"  Predictions: {total_predictions}")
        print(f"  Interventions: {total_interventions}")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate demo data for Digital Behavior Twin')
    parser.add_argument(
        '--sessions',
        type=int,
        default=10,
        help='Number of sessions to generate (default: 10)'
    )
    args = parser.parse_args()

    generate_demo_data(num_sessions=args.sessions)
