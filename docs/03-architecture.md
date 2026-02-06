# Architecture

## Tech Stack
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | Python 3.11 + FastAPI | Async, auto docs, Spark ecosystem alignment |
| Frontend | React 18 + TypeScript + Recharts | Mature, good charting, type-safe |
| Database | PostgreSQL 15 | Reliable, JSON support, good ORM support |
| Spark | PySpark 3.5 + Delta Lake 3.0 | Python-first, Delta native support |
| Cloud | Azure Container Apps | Simpler than AKS, built-in scaling |

## System Architecture
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Dashboard   │────▶│  FastAPI     │────▶│  PostgreSQL  │
│  (React)     │     │  (API)       │     │  (Metadata)  │
└─────────────┘     └──────┬──────┘     └──────────────┘
                           │
                    ┌──────▼──────┐
                    │  DQ Engine   │
                    │  (Rules +    │
                    │  Dimensions) │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼───┐  ┌────▼────┐  ┌───▼──────┐
        │ ADLS    │  │ Delta   │  │ SQL      │
        │ Gen2    │  │ Tables  │  │ Server   │
        └─────────┘  └─────────┘  └──────────┘
```

## Database Schema
- **rules**: id, name, dimension, column_name, operator, threshold, config, severity
- **data_sources**: id, name, type, connection_config, is_active
- **dq_runs**: id, source_id, status, started_at, completed_at, total/passed/failed rules
- **dq_results**: id, run_id, rule_id, dimension, metric_value, threshold, passed
- **dq_scores**: id, run_id, source_id, dimension, score
- **schedules**: id, name, source_id, cron_expression, rule_ids

## API Endpoints
- `GET /api/health` — Health check
- `POST/GET/PUT/DELETE /api/rules` — Rule CRUD
- `POST/GET/PUT/DELETE /api/sources` — Source CRUD
- `POST/GET /api/jobs` — Job submission and monitoring
- `GET /api/metrics/summary|dimensions|sources/{id}` — DQ metrics
