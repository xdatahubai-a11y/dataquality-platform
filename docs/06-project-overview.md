# DataQuality Platform — Project Overview

## What Is It?
An enterprise-grade data quality platform that provides configurable DQ checks across Azure data sources with Spark-based profiling, a rule engine, and an interactive dashboard.

## Key Features
- **6 DQ Dimensions**: Completeness, Uniqueness, Accuracy, Consistency, Timeliness, Validity
- **Rule Engine**: YAML-based declarative rules with threshold operators
- **Multi-Source**: ADLS Gen2, Delta Tables, SQL Server connectors
- **Spark Integration**: PySpark-based job execution for large-scale profiling
- **REST API**: Full CRUD for rules, sources, jobs, and metrics
- **Dashboard**: React-based UI with score cards, dimension charts, run history
- **Azure-Native**: Container Apps deployment with Managed Identity support

## Tech Stack
Python 3.11 · FastAPI · PySpark · SQLAlchemy · PostgreSQL · React · TypeScript · Recharts · Docker · Azure Container Apps · Bicep

## Quick Start
```bash
# API
pip install -r requirements.txt
uvicorn api.main:app --reload

# Dashboard
cd dashboard && npm install && npm run dev

# Full stack
cd infra && docker-compose up --build
```

## Project Status
- ✅ Research & competitor analysis complete
- ✅ Product requirements defined (MVP + 4 future phases)
- ✅ Architecture designed and documented
- ✅ Backend implemented (API, engine, connectors, Spark jobs)
- ✅ Dashboard scaffolded (3 pages, 2 components)
- ✅ 43 tests passing
- ✅ CI/CD pipelines configured
- ✅ Azure deployment templates ready
