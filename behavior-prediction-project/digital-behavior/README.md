# Digital Behavior Prediction

A full-stack behavioral modeling system that predicts task abandonment using real-time browser activity data and provides actionable interventions.

![Project Status](https://img.shields.io/badge/status-MVP-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

Digital Behavior Prediction observes browser behavior patterns (tab switches, session duration, domain diversity) and converts them into structured behavioral sessions. It extracts time-series and aggregate features, predicts when a user is likely to abandon a task, and surfaces explanations with lightweight interventions.

### Key Features

- **Real-time Behavior Tracking**: Chrome extension tracks tab activity, switches, and navigation patterns
- **Intelligent Session Management**: Automatically groups events into meaningful sessions
- **Feature Engineering**: Extracts 10+ behavioral features including switching frequency, volatility, and task continuity
- **Abandonment Prediction**: Weighted scoring model predicts task abandonment risk (0.0-1.0)
- **Explainable Predictions**: Human-readable explanations for every prediction
- **Intervention System**: Rule-based suggestions (take breaks, reduce scope, etc.)
- **Modern Dashboard**: Real-time analytics with charts and insights

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Chrome         │  HTTP   │  FastAPI         │  SQL    │  PostgreSQL     │
│  Extension      ├────────▶│  Backend         ├────────▶│  Database       │
│  (TypeScript)   │  REST   │  (Python)        │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ JSON
                                     ▼
                            ┌──────────────────┐
                            │  Next.js         │
                            │  Dashboard       │
                            │  (React/TS)      │
                            └──────────────────┘
```

### Data Flow

1. **Extension** captures browser events (tab open/close/switch)
2. **Backend** ingests events and groups them into sessions
3. **Feature Pipeline** computes behavioral metrics
4. **Prediction Model** generates risk scores
5. **Dashboard** visualizes sessions, features, and predictions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| **Backend** | FastAPI, Python 3.12, Pydantic |
| **Database** | PostgreSQL 15, SQLAlchemy, Alembic |
| **Extension** | Chrome Extension Manifest V3, TypeScript, Webpack |
| **Infrastructure** | Docker, Docker Compose |

## Project Structure

```
digital-behavior/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── db/             # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── migrations/         # Alembic migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js dashboard
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── lib/           # API client, utils
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── extension/             # Chrome extension
│   ├── src/
│   │   ├── background.ts  # Service worker
│   │   ├── popup.ts       # Popup UI
│   │   └── popup.html
│   ├── manifest.json
│   └── webpack.config.js
├── scripts/               # Utility scripts
│   ├── seed_data.py      # Generate demo data
│   ├── setup.sh          # Setup script
│   └── run_dev.sh        # Dev runner
├── docs/                  # Documentation
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR manually:
  - Python 3.12+
  - Node.js 20+
  - PostgreSQL 15+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd digital-behavior

# Start all services
docker-compose up

# In another terminal, seed demo data
docker-compose exec backend python /app/scripts/seed_data.py --sessions 15
```

### Option 2: Manual Setup

```bash
# Run setup script
./scripts/setup.sh

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Start frontend (new terminal)
cd frontend
npm run dev

# Build extension (new terminal)
cd extension
npm run build
```

### Load Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select `extension/dist` folder

## Usage

### Backend API

The API is available at `http://localhost:8000`

**Key Endpoints:**
- `POST /api/v1/events` - Ingest browser events
- `GET /api/v1/sessions` - List user sessions
- `GET /api/v1/sessions/{id}/analysis` - Get session analysis
- `POST /api/v1/predictions/session/{id}` - Generate prediction
- API Documentation: `http://localhost:8000/api/docs`

### Frontend Dashboard

Access at `http://localhost:3000`

**Features:**
- Overview stats (sessions, risk scores, time)
- Risk trend chart
- Session timeline
- Prediction cards with explanations
- Behavioral insights

### Chrome Extension

Click the extension icon to:
- View tracking status
- See events captured today
- Manually sync data
- Toggle tracking on/off
- Open dashboard

## Demo Data

Generate realistic demo data for testing:

```bash
# Generate 10 sessions (default)
python scripts/seed_data.py

# Generate 50 sessions
python scripts/seed_data.py --sessions 50

# With Docker
docker-compose exec backend python scripts/seed_data.py --sessions 20
```

## Development

### Backend

```bash
cd backend
source venv/bin/activate

# Run tests
pytest

# Run linter
flake8 app/

# Format code
black app/
isort app/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Development mode
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Extension

```bash
cd extension

# Development build (watch mode)
npm run dev

# Production build
npm run build
```

## Configuration

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/digital_behavior_prediction
# OR for SQLite:
# DATABASE_URL=sqlite:///./digital_behavior.db

API_HOST=0.0.0.0
API_PORT=8000
SESSION_TIMEOUT_MINUTES=30
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USER_ID=1
```

## Features Explained

### Feature Engineering

The system computes these behavioral features:

- **Session Length**: Total duration of browsing session
- **Tab Switch Frequency**: Switches per minute
- **Average Tab Dwell Time**: Mean time spent per tab
- **Volatility Score**: Combination of switching and time variance
- **Task Continuity**: Inverse measure of switching rate
- **Domain Diversity**: Ratio of unique domains to total events
- **Late Night Indicator**: Sessions between 11 PM - 5 AM
- **Inactivity Gaps**: Longest gap between events

### Prediction Model

MVP uses a **weighted scoring model**:

| Factor | Weight | Threshold |
|--------|--------|-----------|
| High switching frequency | 0.30 | >3 switches/min |
| Elevated volatility | 0.25 | >5.0 score |
| Short tab duration | 0.20 | <10 seconds |
| Late night behavior | 0.15 | 11 PM - 5 AM |
| Inactivity gaps | 0.10 | >5 minutes |

**Risk Levels:**
- **High** (>0.6): Likely to abandon task soon
- **Medium** (0.3-0.6): Some distraction indicators
- **Low** (<0.3): Stable focus patterns

### Interventions

Rule-based suggestions triggered by risk score:

- **>0.8**: Switch to lower-cognitive-load task
- **0.6-0.8**: Take a 5-minute break
- **0.5-0.6**: Continue 10 more minutes, then reassess

## API Examples

### Ingest Event

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "event_type": "tab_activated",
    "url": "https://github.com",
    "domain": "github.com",
    "title": "GitHub",
    "tab_id": 123,
    "is_active": true
  }'
```

### Get Session Analysis

```bash
curl http://localhost:8000/api/v1/sessions/1/analysis \
  -H "X-User-ID: 1"
```

### Generate Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predictions/session/1 \
  -H "X-User-ID: 1"
```

## Deployment

### Production Build

```bash
# Build and start production services
docker-compose -f docker-compose.yml -f infra/docker-compose.prod.yml up --build
```

### Environment Variables

Set these for production:
- `DATABASE_URL`: Production PostgreSQL URL
- `API_HOST`: Backend host (0.0.0.0 for Docker)
- `NEXT_PUBLIC_API_URL`: Public backend URL
- `LOG_LEVEL`: WARNING or ERROR for production

## Future Enhancements

- [ ] Machine learning model (logistic regression → neural network)
- [ ] Multi-user support with authentication
- [ ] Real-time WebSocket updates
- [ ] Mobile app for iOS/Android
- [ ] Advanced interventions (Pomodoro timer, focus mode)
- [ ] Team analytics and aggregated insights
- [ ] Export reports (PDF, CSV)
- [ ] Browser history analysis
- [ ] Productivity scoring
- [ ] Integration with calendar/task managers

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built as an MVP for a portfolio project demonstrating:
- Full-stack development
- Real-time data pipelines
- Behavioral modeling
- System design
- Production-ready architecture

---

**Note**: This is an MVP focused on demonstrating clean architecture and systems thinking. The prediction model is intentionally simple and can be enhanced with proper ML infrastructure in production.
