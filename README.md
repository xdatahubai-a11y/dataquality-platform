# DataQuality Platform

Enterprise data quality platform with configurable rule engine, Spark-based profiling, and Azure-native deployment.

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-blue)
![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen)

## Features

- **6 DQ Dimensions**: Completeness, Uniqueness, Accuracy, Consistency, Timeliness, Validity
- **Rule Engine**: YAML-based declarative rules with configurable thresholds and operators
- **Data Sources**: ADLS Gen2, Delta Tables, SQL Server
- **Spark Jobs**: PySpark-based large-scale DQ profiling
- **REST API**: Full CRUD for rules, sources, jobs, and metrics (auto-generated OpenAPI docs)
- **Dashboard**: React/TypeScript UI with score cards, dimension charts, and run history
- **Azure Deployment**: Container Apps, Key Vault, Managed Identity (Bicep templates)

## Quick Start

### API Server
```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### Docker Compose (Full Stack)
```bash
cd infra
docker-compose up --build
# API: http://localhost:8000
# Dashboard: http://localhost:3000
```

## Project Structure

```
api/          — FastAPI backend (routers, models, schemas)
engine/       — DQ rule engine + dimension calculators
connectors/   — Data source connectors (ADLS Gen2, Delta, SQL Server)
spark/        — Spark job definitions and submission
dashboard/    — React/TypeScript frontend
infra/        — Docker, Nginx, Azure Bicep deployment
tests/        — Pytest test suite (43 tests)
rules/        — Example YAML rule definitions
docs/         — Architecture and design documentation
```

## Example Rule (YAML)

```yaml
checks:
  - name: email_completeness
    dimension: completeness
    column: email
    operator: gte
    threshold: 95.0
    severity: critical
    config:
      treat_empty_as_null: true

  - name: customer_id_uniqueness
    dimension: uniqueness
    column: customer_id
    threshold: 100.0
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST/GET/PUT/DELETE | `/api/rules` | Rule CRUD |
| POST/GET/PUT/DELETE | `/api/sources` | Data source CRUD |
| POST/GET | `/api/jobs` | Job submission & monitoring |
| GET | `/api/metrics/summary` | Overall DQ scores |
| GET | `/api/metrics/dimensions` | Per-dimension scores |

## Running Tests

```bash
python -m pytest tests/ -v
```

## Documentation

- [Research Report](docs/01-research.md)
- [Requirements](docs/02-requirements.md)
- [Architecture](docs/03-architecture.md)
- [Implementation](docs/04-implementation.md)
- [Test Report](docs/05-test-report.md)
- [Project Overview](docs/06-project-overview.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT
