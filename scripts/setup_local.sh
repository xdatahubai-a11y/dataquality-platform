#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== DataQuality Platform — Local Setup ==="

# 1. Start services
echo "[1/5] Starting Docker Compose..."
cd "$PROJECT_DIR/infra"
docker compose up -d postgres
cd "$PROJECT_DIR"

# 2. Wait for DB
echo "[2/5] Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U dq -d dataquality >/dev/null 2>&1; then
        echo "  PostgreSQL is ready."
        break
    fi
    sleep 1
done

# 3. Generate test data
echo "[3/5] Generating test data..."
python3 scripts/generate_test_data.py

# 4. Seed database
echo "[4/5] Seeding database..."
DQ_DATABASE_URL="postgresql://dq:dqpass@localhost:5432/dataquality" python3 scripts/seed_database.py

# 5. Run DQ checks
echo "[5/5] Running DQ checks..."
python3 scripts/run_test_suite.py
EXIT_CODE=$?

echo ""
echo "=== Setup complete ==="
exit $EXIT_CODE
