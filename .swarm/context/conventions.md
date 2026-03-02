# Coding Conventions

## Architecture patterns
- Routers in `api/routers/`, one file per resource
- Schemas in `api/schemas/`, Pydantic models
- DB models in `api/models/database.py`
- Connectors in `connectors/`, inherit from `base.py`

## Testing conventions
- Tests in `tests/test_*.py`
- Use httpx TestClient for API tests
- SQLite in-memory for test database
- Every new endpoint needs tests

## Things agents should always do
- Run `source .venv/bin/activate && python -m pytest tests/ -v` before committing
- Check for deprecation warnings with `-W error::DeprecationWarning`

## Things agents should never do
- Don't modify `spark/` directory (Spark code is separate)
- Don't add new dependencies without checking requirements.txt first
