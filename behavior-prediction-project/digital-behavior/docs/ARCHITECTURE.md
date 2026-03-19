# Digital Behavior Prediction - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [API Design](#api-design)
7. [Prediction Pipeline](#prediction-pipeline)
8. [Scaling Considerations](#scaling-considerations)

## System Overview

Digital Behavior Prediction is a behavioral modeling system that consists of four main components:

1. **Chrome Extension**: Captures browser events
2. **FastAPI Backend**: Processes events, computes features, generates predictions
3. **PostgreSQL Database**: Stores events, sessions, features, predictions
4. **Next.js Frontend**: Visualizes data and insights

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        User's Browser                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Chrome Extension (Service Worker + Popup)               │ │
│  │  - Event Capture                                          │ │
│  │  - Event Batching                                         │ │
│  │  - Local Storage                                          │ │
│  └───────────────────────┬──────────────────────────────────┘ │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTP POST (batched events)
                             ▼
          ┌──────────────────────────────────────────┐
          │       FastAPI Backend (Python)           │
          │                                          │
          │  ┌────────────────────────────────────┐ │
          │  │  API Layer (routes/)               │ │
          │  │  - Event ingestion                 │ │
          │  │  - Session queries                 │ │
          │  │  - Prediction requests             │ │
          │  └──────────┬─────────────────────────┘ │
          │             ▼                            │
          │  ┌────────────────────────────────────┐ │
          │  │  Service Layer                     │ │
          │  │  - BehaviorService                 │ │
          │  │    * Session management            │ │
          │  │    * Feature computation           │ │
          │  │    * Prediction generation         │ │
          │  │    * Intervention logic            │ │
          │  └──────────┬─────────────────────────┘ │
          │             ▼                            │
          │  ┌────────────────────────────────────┐ │
          │  │  ORM Layer (SQLAlchemy)            │ │
          │  │  - User, Session, Event models     │ │
          │  │  - FeatureSnapshot, Prediction     │ │
          │  └──────────┬─────────────────────────┘ │
          └─────────────┼──────────────────────────┘
                        │ SQL
                        ▼
          ┌──────────────────────────────────────────┐
          │       PostgreSQL Database                │
          │  - Events (raw data)                     │
          │  - Sessions (aggregated)                 │
          │  - Features (engineered)                 │
          │  - Predictions (model outputs)           │
          │  - Interventions (suggestions)           │
          └──────────────────────────────────────────┘
                        ▲
                        │ SQL Queries
                        │
          ┌─────────────┴──────────────────────────┐
          │    Next.js Frontend (React/TypeScript)  │
          │                                         │
          │  ┌─────────────────────────────────┐   │
          │  │  Pages (app/)                   │   │
          │  │  - Dashboard                    │   │
          │  │  - Session details              │   │
          │  └──────────┬──────────────────────┘   │
          │             ▼                           │
          │  ┌─────────────────────────────────┐   │
          │  │  Components                     │   │
          │  │  - StatCard, SessionCard        │   │
          │  │  - RiskBadge, PredictionCard    │   │
          │  │  - Charts (Recharts)            │   │
          │  └──────────┬──────────────────────┘   │
          │             ▼                           │
          │  ┌─────────────────────────────────┐   │
          │  │  API Client (lib/api.ts)        │   │
          │  │  - sessionsAPI                  │   │
          │  │  - predictionsAPI               │   │
          │  │  - eventsAPI                    │   │
          │  └─────────────────────────────────┘   │
          └─────────────────────────────────────────┘
```

## Architecture Principles

### 1. Separation of Concerns

Each component has a clear, single responsibility:
- **Extension**: Data collection only
- **Backend**: Business logic and data processing
- **Database**: Data persistence
- **Frontend**: Presentation and user interaction

### 2. Layered Architecture

The backend follows a clean layered architecture:

```
API Layer (FastAPI routes)
    ↓
Service Layer (BehaviorService)
    ↓
ORM Layer (SQLAlchemy models)
    ↓
Database (PostgreSQL)
```

### 3. Data Pipeline

Events flow through distinct stages:

```
Raw Events → Sessions → Features → Predictions → Interventions
```

Each stage is idempotent and can be recomputed independently.

### 4. Stateless API

The backend API is stateless. All state is stored in the database, enabling:
- Horizontal scaling
- Load balancing
- Service restarts without data loss

### 5. Client-Side Batching

The extension batches events locally before sending to reduce network overhead and API load.

## Component Design

### Chrome Extension

**Architecture**: Manifest V3 Service Worker

**Key Responsibilities:**
- Listen to Chrome tab/window events
- Batch events into local queue
- Periodic sync to backend (30s interval or 10 events)
- Manage tracking state (on/off)
- Display status in popup

**Design Decisions:**
- **Why Service Worker?** Manifest V3 requirement, always-on background capability
- **Why Batching?** Reduces API calls, network usage, and backend load
- **Why TypeScript?** Type safety for Chrome APIs, better developer experience

### FastAPI Backend

**Architecture**: Layered REST API

**Key Responsibilities:**
- Event ingestion and validation
- Session management (30-minute timeout)
- Feature engineering
- Prediction generation
- Intervention rules

**Service Layer Design:**

```python
class BehaviorService:
    def ingest_event(user_id, event)
        # 1. Find or create session
        # 2. Save event
        # 3. Update session metadata
        # 4. Return event

    def compute_features(session_id)
        # 1. Fetch all session events
        # 2. Calculate time-series features
        # 3. Calculate aggregate features
        # 4. Save FeatureSnapshot
        # 5. Return snapshot

    def predict_abandonment(session_id)
        # 1. Get or compute features
        # 2. Apply weighted scoring model
        # 3. Generate explanation
        # 4. Save Prediction
        # 5. Generate intervention if needed
        # 6. Return prediction
```

**Design Decisions:**
- **Why FastAPI?** Modern, async, automatic OpenAPI docs, Pydantic validation
- **Why Service Layer?** Separates business logic from routes, enables testing
- **Why SQLAlchemy?** ORM provides abstraction, supports multiple databases

### Database Schema

**Entity-Relationship Model:**

```
User (1) ──┬──< Session (N)
           │
Session ───┼──< BrowserEvent (N)
           │
Session ───┼──< FeatureSnapshot (N)
           │
Session ───┼──< Prediction (N)
           │
Prediction ─┴──< Intervention (N)
```

**Key Tables:**

1. **users**: User accounts (MVP: single user)
2. **browser_events**: Raw event data
3. **sessions**: Aggregated browsing sessions
4. **feature_snapshots**: Computed features
5. **predictions**: Model outputs
6. **interventions**: Suggested actions

**Design Decisions:**
- **Why Separate Features Table?** Enables feature versioning, recomputation
- **Why Keep Raw Events?** Supports model retraining, debugging, feature engineering iterations
- **Why Predictions Table?** Tracks model evolution, enables A/B testing

### Next.js Frontend

**Architecture**: React Server Components + Client Components

**Key Responsibilities:**
- Fetch data from backend API
- Render dashboard with charts
- Display sessions, features, predictions
- Provide insights and recommendations

**Component Hierarchy:**

```
Page (Server Component)
  ↓
StatCard (Client Component)
SessionCard (Client Component)
PredictionCard (Client Component)
RiskTrendChart (Client Component)
  ↓
Recharts (Library)
```

**Design Decisions:**
- **Why Next.js 14?** App Router, React Server Components, built-in optimization
- **Why Client Components for Charts?** Interactivity requires client-side JavaScript
- **Why Tailwind CSS?** Utility-first, rapid development, consistent styling

## Data Flow

### Event Ingestion Flow

```
1. User switches tab in Chrome
   ↓
2. Extension captures tab event
   ↓
3. Event added to local queue
   ↓
4. Queue reaches batch size (10) or timeout (30s)
   ↓
5. POST /api/v1/events/batch
   ↓
6. Backend validates event data (Pydantic)
   ↓
7. BehaviorService.ingest_event()
   ↓
8. Find or create session (30min timeout)
   ↓
9. Create BrowserEvent record
   ↓
10. Update Session metadata (switches, domains, duration)
    ↓
11. Commit to database
    ↓
12. Return success to extension
```

### Prediction Generation Flow

```
1. Frontend requests prediction
   ↓
2. POST /api/v1/predictions/session/{id}
   ↓
3. BehaviorService.predict_abandonment(session_id)
   ↓
4. Check for existing FeatureSnapshot
   ↓
5. If not exists: compute_features(session_id)
   ↓
6. Fetch all events for session
   ↓
7. Calculate features:
   - Session length
   - Switch frequency
   - Volatility
   - Task continuity
   - Domain diversity
   ↓
8. Apply weighted scoring model:
   risk_score = Σ(factor_weight * factor_triggered)
   ↓
9. Generate human-readable explanation
   ↓
10. Create Prediction record
    ↓
11. If risk_score > 0.5: generate Intervention
    ↓
12. Commit to database
    ↓
13. Return prediction with explanation
```

## Database Schema

### Detailed Table Definitions

#### users

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | User identifier |
| username | String (unique) | Username |
| created_at | DateTime | Account creation timestamp |

#### browser_events

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Event identifier |
| session_id | Integer (FK) | Parent session |
| timestamp | DateTime | Event occurrence time |
| event_type | String | Type: tab_activated, tab_created, etc. |
| url | String | Full URL (nullable) |
| domain | String | Domain extracted from URL |
| title | String | Page title |
| tab_id | Integer | Chrome tab ID |
| window_id | Integer | Chrome window ID |
| is_active | Boolean | Whether tab was active |

**Indexes:**
- `session_id` (foreign key)
- `event_type`
- `domain`
- `timestamp`

#### sessions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Session identifier |
| user_id | Integer (FK) | Parent user |
| start_time | DateTime | Session start |
| end_time | DateTime | Session end (updated continuously) |
| active_duration_seconds | Float | Total active time |
| switch_count | Integer | Number of tab switches |
| domain_diversity | Float | Unique domains / total events |
| inactivity_gap_seconds | Float | Longest gap between events |

**Indexes:**
- `user_id` (foreign key)
- `start_time`

#### feature_snapshots

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Snapshot identifier |
| session_id | Integer (FK) | Parent session |
| timestamp | DateTime | Computation time |
| session_length_minutes | Float | Session duration |
| avg_time_per_tab_seconds | Float | Mean tab dwell time |
| tab_switch_frequency | Float | Switches per minute |
| repeated_revisits | Integer | Domains visited >1 time |
| unique_domains_count | Integer | Distinct domains |
| inactivity_gap_detected | Boolean | Gap >5 minutes |
| late_night_behavior | Boolean | Session 11PM-5AM |
| volatility_score | Float | Switching + variance metric |
| task_continuity_estimate | Float | Inverse of switch frequency |

**Indexes:**
- `session_id` (foreign key)
- `timestamp`

#### predictions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Prediction identifier |
| session_id | Integer (FK) | Parent session |
| timestamp | DateTime | Prediction time |
| abandonment_risk_score | Float | Risk score (0.0-1.0) |
| context_switch_likelihood | Float | Switch likelihood (0.0-1.0) |
| explanation | Text | Human-readable explanation |
| contributing_factors | String | Comma-separated factor list |

**Indexes:**
- `session_id` (foreign key)
- `timestamp`

#### interventions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Intervention identifier |
| prediction_id | Integer (FK) | Parent prediction |
| suggested_intervention | String | Recommended action |
| rule_triggered | String | Which rule fired |
| is_displayed | Boolean | Shown to user? |
| displayed_at | DateTime | When shown (nullable) |

**Indexes:**
- `prediction_id` (foreign key)

## API Design

### REST Principles

- **Resource-based URLs**: `/api/v1/sessions`, `/api/v1/predictions`
- **HTTP Methods**: GET (read), POST (create), PUT (update)
- **Status Codes**: 200 OK, 201 Created, 404 Not Found, 500 Error
- **JSON Payloads**: Request/response in JSON format

### API Versioning

All routes prefixed with `/api/v1` to support future versions without breaking changes.

### Authentication

MVP: Simple `X-User-ID` header (single-user mode)

Future: JWT tokens with OAuth2

### Rate Limiting

Not implemented in MVP. For production:
- Use SlowAPI or similar
- Limit: 100 requests/minute per user
- 429 Too Many Requests response

## Prediction Pipeline

### Current Model: Weighted Scoring

**Input Features:**
- tab_switch_frequency
- volatility_score
- avg_time_per_tab_seconds
- late_night_behavior
- inactivity_gap_detected

**Scoring Logic:**

```python
risk_score = 0.0

if tab_switch_frequency > 3.0:
    risk_score += 0.30  # High switching
elif tab_switch_frequency > 1.5:
    risk_score += 0.15  # Moderate switching

if volatility_score > 5.0:
    risk_score += 0.25  # High volatility
elif volatility_score > 3.0:
    risk_score += 0.15  # Moderate volatility

if avg_time_per_tab_seconds < 10:
    risk_score += 0.20  # Very short dwell
elif avg_time_per_tab_seconds < 30:
    risk_score += 0.10  # Short dwell

if late_night_behavior:
    risk_score += 0.15  # Late night session

if inactivity_gap_detected:
    risk_score += 0.10  # Long gaps

risk_score = min(risk_score, 1.0)  # Cap at 1.0
```

**Advantages:**
- Interpretable
- No training data required
- Fast inference
- Easy to tune

**Limitations:**
- No personalization
- Fixed thresholds
- Cannot learn from data

### Future Model: Machine Learning

**Approach:**

1. **Data Collection**: Accumulate labeled data (abandoned vs. continued sessions)
2. **Feature Engineering**: Expand to 20+ features
3. **Model Selection**: Logistic Regression → Random Forest → Neural Network
4. **Training Pipeline**: Offline batch training, periodic retraining
5. **Deployment**: Model serving with FastAPI
6. **Monitoring**: Track prediction accuracy, drift

**Features to Add:**
- Time of day patterns
- Day of week patterns
- Historical abandonment rate
- Domain categories (work, social, news)
- Sequence patterns (tab navigation graph)

## Scaling Considerations

### Current Limitations (MVP)

- Single user only
- No authentication
- In-memory session management
- Synchronous processing
- No caching
- No horizontal scaling

### Scaling Path

**Phase 1: Multi-User (1K users)**
- Add authentication (JWT)
- User management
- Per-user rate limiting
- Database indexing

**Phase 2: Horizontal Scaling (10K users)**
- Load balancer
- Multiple backend instances
- Redis cache for sessions
- CDN for frontend
- Database read replicas

**Phase 3: Real-Time Processing (100K users)**
- Message queue (RabbitMQ/Kafka)
- Background workers (Celery)
- WebSocket connections
- Real-time dashboard updates
- Event streaming architecture

**Phase 4: Advanced Analytics (1M users)**
- Data warehouse (Snowflake/BigQuery)
- Batch processing (Spark)
- ML training pipeline (MLflow)
- Model serving (TensorFlow Serving)
- A/B testing framework

### Database Scaling

**Indexes:**
- Already indexed on foreign keys
- Add composite indexes for common queries:
  - `(user_id, start_time)` on sessions
  - `(session_id, timestamp)` on events

**Partitioning:**
- Partition events table by month
- Partition sessions table by user_id ranges

**Archival:**
- Move events >6 months to cold storage
- Keep only aggregated data for old sessions

### Caching Strategy

**Redis Caching:**
- Session metadata (TTL: 30 minutes)
- Feature snapshots (TTL: 1 hour)
- Recent predictions (TTL: 15 minutes)
- User profiles (TTL: 24 hours)

**Cache Invalidation:**
- Invalidate on new events
- Invalidate on prediction generation
- Use cache-aside pattern

## Security Considerations

### Current MVP

- No authentication (demo only)
- No encryption
- No input sanitization (beyond Pydantic validation)
- CORS allows all origins

### Production Requirements

1. **Authentication**: JWT with refresh tokens
2. **Authorization**: Role-based access control
3. **Encryption**: HTTPS only, TLS 1.3
4. **Input Validation**: Strict Pydantic schemas
5. **SQL Injection**: Parameterized queries (SQLAlchemy ORM)
6. **XSS Prevention**: React escapes by default
7. **CORS**: Whitelist specific origins
8. **Rate Limiting**: Prevent abuse
9. **Data Privacy**: GDPR compliance, data retention policies

## Conclusion

The Digital Behavior Prediction architecture is designed for:
- **Modularity**: Each component is independent and replaceable
- **Scalability**: Clear path from MVP to production scale
- **Maintainability**: Clean separation of concerns, well-documented
- **Extensibility**: Easy to add features, improve model, scale infrastructure

The MVP demonstrates strong systems thinking with production-ready patterns, making it suitable for a portfolio and real-world deployment with appropriate enhancements.
