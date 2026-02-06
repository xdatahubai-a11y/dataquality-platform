# Contributing to DataQuality Platform

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for local stack)

### Backend Setup
```bash
cd dataquality-tool
pip install -r requirements.txt
# Start API server
uvicorn api.main:app --reload --port 8000
```

### Dashboard Setup
```bash
cd dashboard
npm install
npm run dev
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Docker Compose (Full Stack)
```bash
cd infra
docker-compose up --build
```
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Project Structure
```
api/         — FastAPI backend
engine/      — DQ rule engine + dimension calculators
connectors/  — Data source connectors (ADLS, Delta, SQL Server)
spark/       — Spark job definitions
dashboard/   — React frontend
infra/       — Docker + Azure deployment configs
tests/       — Test suite
rules/       — Example YAML rule definitions
docs/        — Documentation
```

### Code Standards
- Python: Type hints everywhere, docstrings, max 200 lines per file
- TypeScript: Strict mode, functional components
- Tests: pytest for backend, cover all dimensions and API endpoints
