# DevOps Monitoring Dashboard

A real-time DevOps monitoring dashboard with a FastAPI backend and Streamlit frontend.

## Features

- **Live system metrics** (CPU, memory, disk) via REST and WebSocket
- **Server registry** — register, list, and remove monitored servers
- **Background health polling** — automatically checks server health every 10s
- **API key authentication** on write endpoints
- **Streamlit dashboard** with real-time charts and server management

## Project Structure

```
devops-monitor/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── models.py        # Pydantic schemas + Server dataclass
│   ├── auth.py          # API key dependency
│   ├── metrics.py       # psutil helper
│   └── poller.py        # Background health-check logic
├── dashboard/
│   └── app.py           # Streamlit frontend
├── tests/
│   ├── test_metrics.py
│   └── test_routes.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Install dependencies

```bash
cd devops-monitor
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn api.main:app --reload --port 8000
```

### 3. Start the Streamlit dashboard

In a second terminal:

```bash
streamlit run dashboard/app.py
```

### 4. Run tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=api -v
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `dev-secret-key` | API key for protected endpoints |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | Public | Health check |
| GET | `/metrics` | Public | System metrics snapshot |
| WebSocket | `/ws/metrics` | Public | Live metrics stream (1s interval) |
| POST | `/servers` | API Key | Register a server |
| GET | `/servers` | Public | List servers (optional `?status=` filter) |
| GET | `/servers/{id}` | Public | Get one server |
| DELETE | `/servers/{id}` | API Key | Remove a server |
| POST | `/servers/{id}/check` | Public | Trigger immediate health check |
