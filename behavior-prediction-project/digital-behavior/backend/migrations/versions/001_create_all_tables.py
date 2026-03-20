"""Create all database tables

Revision ID: 001_create_all_tables
Revises: fb579249baa1
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_create_all_tables'
down_revision = 'fb579249baa1'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('active_duration_seconds', sa.Float(), server_default='0', nullable=True),
        sa.Column('switch_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('domain_diversity', sa.Float(), server_default='0', nullable=True),
        sa.Column('inactivity_gap_seconds', sa.Float(), server_default='0', nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_start_time'), 'sessions', ['start_time'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # Create browser_events table
    op.create_table('browser_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('tab_id', sa.Integer(), nullable=True),
        sa.Column('window_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_browser_events_domain'), 'browser_events', ['domain'], unique=False)
    op.create_index(op.f('ix_browser_events_event_type'), 'browser_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_browser_events_session_id'), 'browser_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_browser_events_timestamp'), 'browser_events', ['timestamp'], unique=False)

    # Create feature_snapshots table
    op.create_table('feature_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('session_length_minutes', sa.Float(), nullable=True),
        sa.Column('avg_time_per_tab_seconds', sa.Float(), nullable=True),
        sa.Column('tab_switch_frequency', sa.Float(), nullable=True),
        sa.Column('repeated_revisits', sa.Integer(), nullable=True),
        sa.Column('unique_domains_count', sa.Integer(), nullable=True),
        sa.Column('inactivity_gap_detected', sa.Boolean(), nullable=True),
        sa.Column('late_night_behavior', sa.Boolean(), nullable=True),
        sa.Column('volatility_score', sa.Float(), nullable=True),
        sa.Column('task_continuity_estimate', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feature_snapshots_session_id'), 'feature_snapshots', ['session_id'], unique=False)

    # Create predictions table
    op.create_table('predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('abandonment_risk_score', sa.Float(), nullable=False),
        sa.Column('context_switch_likelihood', sa.Float(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('contributing_factors', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_session_id'), 'predictions', ['session_id'], unique=False)

    # Create interventions table
    op.create_table('interventions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_id', sa.Integer(), nullable=False),
        sa.Column('suggested_intervention', sa.String(length=500), nullable=False),
        sa.Column('rule_triggered', sa.String(length=100), nullable=True),
        sa.Column('is_displayed', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('displayed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interventions_prediction_id'), 'interventions', ['prediction_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interventions_prediction_id'), table_name='interventions')
    op.drop_table('interventions')
    op.drop_index(op.f('ix_predictions_session_id'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_feature_snapshots_session_id'), table_name='feature_snapshots')
    op.drop_table('feature_snapshots')
    op.drop_index(op.f('ix_browser_events_timestamp'), table_name='browser_events')
    op.drop_index(op.f('ix_browser_events_session_id'), table_name='browser_events')
    op.drop_index(op.f('ix_browser_events_event_type'), table_name='browser_events')
    op.drop_index(op.f('ix_browser_events_domain'), table_name='browser_events')
    op.drop_table('browser_events')
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_start_time'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_table('users')
