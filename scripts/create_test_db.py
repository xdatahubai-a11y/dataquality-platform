#!/usr/bin/env python3
"""Create a SQLite test database with quality issues for DQ testing.

Reuses generation logic from generate_test_data.py but writes to SQLite.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_test_data import (
    generate_corrupted,
    generate_customers,
    generate_orders,
    generate_products,
)

DB_PATH = Path(__file__).resolve().parent.parent / "test_dq.db"


def create_database(db_path: Path | None = None) -> Path:
    """Create SQLite database with all test tables.

    Args:
        db_path: Path for the database file. Defaults to project root.

    Returns:
        Path to the created database.
    """
    path = db_path or DB_PATH
    path.unlink(missing_ok=True)

    conn = sqlite3.connect(str(path))

    datasets = {
        "customers": generate_customers(),
        "orders": generate_orders(),
        "products": generate_products(),
        "corrupted": generate_corrupted(),
    }

    for name, df in datasets.items():
        df.to_sql(name, conn, index=False, if_exists="replace")
        print(f"  {name}: {len(df)} rows")

    conn.close()
    print(f"\nDatabase created: {path}")
    return path


if __name__ == "__main__":
    create_database()
