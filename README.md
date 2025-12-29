# FleetPulse - Real-Time Fleet Monitoring System

A production-grade full-stack platform for monitoring and managing fleets of GPS-enabled devices in real-time. FleetPulse provides comprehensive tracking of device status, locations, telemetry data, and critical events.

![FleetPulse](https://img.shields.io/badge/status-production-green) 

## Features
[View detailed user stories →](docs/USER_STORIES.md)


### Dashboard & Fleet Overview
- **Real-Time Metrics**: Monitor total devices, online status, critical events, and warnings at a glance
- **Interactive Map**: Visualize device locations with real-time updates
- **Fleet Overview Table**: Detailed device list with status, location, and last seen timestamps
- **Live Updates**: WebSocket-powered real-time data refresh (5-10 second intervals)
- **Smart Navigation**: Click metric cards to navigate to relevant sections


### Events & Alerts Management
- **Comprehensive Event Feed**: Monitor LOW_BATTERY, STALE, IMPACT, and GEOFENCE events
- **Advanced Filtering**: Filter by event type, severity (critical/warning/info), and acknowledgment status
- **Event Management**: Acknowledge events to track which incidents have been addressed
- **Auto-Refresh**: Events update every 5 seconds automatically


## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **PostgreSQL 15+** - Relational database with TimescaleDB extensions
- **Redis** - Caching and pub/sub for real-time updates
- **Celery** - Background task processing
- **WebSocket** - Real-time bidirectional communication
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **TanStack Query (React Query)** - Data fetching and caching
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **Leaflet** - Interactive maps
- **date-fns** - Modern date formatting

### Infrastructure
- **Alembic** - Database migrations
- **Asyncpg** - Async PostgreSQL driver

## Quick Start

### Prerequisites

Ensure you have the following installed:
- **Python 3.11+**
- **PostgreSQL 15+**
- **Redis**
- **Node.js 18+** and npm/yarn

### Installation

```bash
# Install dependencies (macOS)
brew install postgresql@15 redis python@3.11

# Start services
brew services start postgresql@15
brew services start redis
```

### Setup Database

```bash
# Create database and user
psql postgres -c "CREATE DATABASE fleetpulse;"
psql postgres -c "CREATE USER fleetpulse WITH PASSWORD 'fleetpulse';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE fleetpulse TO fleetpulse;"
```

### Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Seed initial data
python -m app.db.init_db
```

### Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file (if needed)
cp .env.example .env
```

## Running the Application

You'll need **5 terminal windows** to run the complete application:

### Terminal 1: Backend API Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Backend API:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### Terminal 2: Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info
```

Processes background tasks including event detection and data processing.

### Terminal 3: Celery Beat Scheduler

```bash
cd backend
source venv/bin/activate
celery -A app.worker.celery_app beat --loglevel=info
```

Schedules periodic tasks like stale device checks.

### Terminal 4: Device Simulator

```bash
cd backend
source venv/bin/activate
python ../scripts/simulate_devices.py --devices 5 --speed 2
```

Generates realistic telemetry data for testing. Adjust `--devices` and `--speed` as needed.

### Terminal 5: Frontend Development Server

```bash
cd frontend
npm run dev
```

**Frontend Application:** http://localhost:5174

## API Endpoints

### Devices
- `POST /api/v1/devices` - Create a new device
- `GET /api/v1/devices` - List all devices
- `GET /api/v1/devices/{id}` - Get device details
- `PATCH /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device

### Telemetry
- `POST /api/v1/ingest` - Ingest telemetry data
- `GET /api/v1/devices/{id}/telemetry` - Get device telemetry history
- `GET /api/v1/devices/{id}/latest` - Get latest telemetry reading

### Events
- `GET /api/v1/events` - List events (supports filtering)
- `GET /api/v1/events/{id}` - Get event details
- `POST /api/v1/events/{id}/acknowledge` - Acknowledge an event

### WebSocket
- `WS /api/v1/ws` - WebSocket endpoint for real-time updates

## Project Structure

```
FleetPulse/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes and endpoints
│   │   │   └── v1/        # API v1 routes
│   │   ├── core/          # Configuration, logging, dependencies
│   │   ├── domain/        # Domain models and schemas
│   │   │   ├── models/    # SQLAlchemy models
│   │   │   └── schemas/   # Pydantic schemas
│   │   ├── services/      # Business logic layer
│   │   ├── db/            # Database configuration and initialization
│   │   └── worker/        # Celery tasks and workers
│   ├── tests/             # Backend tests
│   ├── alembic/           # Database migrations
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
│
├── frontend/              # React frontend
│   ├── src/
│   │   ├── api/          # API client and WebSocket
│   │   ├── components/   # React components
│   │   │   ├── DeviceList.tsx
│   │   │   ├── EventFeed.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── StatsCards.tsx
│   │   │   └── ...
│   │   ├── pages/        # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   └── Events.tsx
│   │   ├── types/        # TypeScript type definitions
│   │   ├── App.tsx       # Root component
│   │   ├── App.css       # Global styles
│   │   └── main.tsx      # Entry point
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── vite.config.ts    # Vite configuration
│
├── scripts/              # Utility scripts
│   └── simulate_devices.py  # Device simulator
│
├── USER_STORIES.md       # Complete user stories documentation
├── UI.md                 # UI design specifications
└── README.md            # This file
```

## Configuration

### Backend Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://fleetpulse:fleetpulse@localhost:5432/fleetpulse

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Event Thresholds
LOW_BATTERY_THRESHOLD=20
STALE_DEVICE_THRESHOLD_MINUTES=15
IMPACT_THRESHOLD_G_FORCE=3.0

# JWT (if using authentication)
SECRET_KEY=your-secret-key-here
```

### Frontend Environment Variables (.env)

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Event Detection

FleetPulse automatically detects and creates events based on configurable thresholds:

- **LOW_BATTERY**: Triggered when battery level falls below 20% (configurable)
- **STALE**: Triggered when device hasn't reported data for 15+ minutes (configurable)
- **IMPACT**: Triggered on sudden acceleration/deceleration above 3.0 G-force (configurable)
- **GEOFENCE**: Triggered when device enters/exits virtual boundaries

Event severities:
- **Critical**: Immediate attention required (e.g., impacts, critical battery)
- **Warning**: Important but not urgent (e.g., low battery, stale devices)
- **Info**: Informational events (e.g., geofence transitions)

## Development

### Create a Database Migration

```bash
cd backend
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

### Reset Database

```bash
psql postgres -c "DROP DATABASE fleetpulse;"
psql postgres -c "CREATE DATABASE fleetpulse;"
cd backend && alembic upgrade head && python -m app.db.init_db
```

### Run Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Build Frontend for Production

```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`.

## Troubleshooting

### WebSocket Connection Issues

If the LIVE indicator shows OFFLINE:
1. Ensure the backend is running on port 8000
2. Check CORS settings in backend `.env`
3. Verify WebSocket URL in frontend configuration

### No Devices Showing

1. Ensure the device simulator is running (Terminal 4)
2. Check that initial data was seeded: `python -m app.db.init_db`
3. Verify database connection in backend `.env`

### Events Not Appearing

1. Ensure Celery worker is running (Terminal 2)
2. Ensure Celery beat is running (Terminal 3)
3. Check event detection thresholds in `.env`

### Port Already in Use

If ports 8000 or 5174 are in use:
- Backend: Change Uvicorn port with `--port 8001`
- Frontend: Vite will automatically try the next available port

## User Stories & Documentation

For complete feature documentation, user stories, and acceptance criteria, see:
- [USER_STORIES.md](USER_STORIES.md) - Comprehensive user stories covering all features
- [UI.md](UI.md) - UI design specifications and guidelines

## Performance

- **Dashboard Load Time**: < 2 seconds
- **Real-time Update Latency**: < 1 second
- **Concurrent Users**: Supports 100+ simultaneous connections
- **Map Performance**: Smooth rendering with 100+ device markers

## Browser Compatibility

Tested and optimized for:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Potential features for future development:
- Device command & control
- Historical analytics and trends
- Custom geofencing with visual editor
- Personalized dashboards
- PDF/CSV report generation
- Multi-user authentication and roles
- Email/SMS notifications
- Device grouping and organization
- Maintenance scheduling
- Route optimization


---

