#!/usr/bin/env python3
"""Generate test datasets with intentional data quality issues.

Produces CSV and Parquet files for testing DQ rule evaluation:
- customers.csv: Mixed quality (some dimensions fail)
- orders.csv: Clean dataset (all pass)
- products.csv: Perfect dataset (positive control)
- corrupted.csv: Severely degraded (everything fails)
"""

import os
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "test_data"


def random_email(valid: bool = True) -> str:
    """Generate a random email address."""
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    if not valid:
        return random.choice([name, f"{name}@", f"@{name}.com", name + "@.com"])
    return f"{name}@example.com"


def generate_customers(n: int = 10_000) -> pd.DataFrame:
    """Generate customers dataset with ~5% null emails, 2% dup IDs, etc."""
    random.seed(SEED)
    base_ids = list(range(1, n + 1))
    # 2% duplicate IDs
    dup_count = int(n * 0.02)
    for i in random.sample(range(n), dup_count):
        base_ids[i] = base_ids[(i + 1) % n]

    emails: list[str | None] = []
    for i in range(n):
        r = random.random()
        if r < 0.05:
            emails.append(None)  # 5% null
        elif r < 0.08:
            emails.append(random_email(valid=False))  # 3% invalid
        else:
            emails.append(random_email(valid=True))

    ages: list[int] = []
    for _ in range(n):
        r = random.random()
        if r < 0.01:
            ages.append(random.randint(-10, -1))  # negative
        elif r < 0.02:
            ages.append(random.randint(151, 200))  # unrealistic
        else:
            ages.append(random.randint(18, 85))

    valid_statuses = ["active", "inactive", "suspended"]
    statuses = [
        random.choice(valid_statuses + ["unknown"]) if random.random() < 0.03
        else random.choice(valid_statuses)
        for _ in range(n)
    ]

    now = datetime.now()
    created = [now - timedelta(days=random.randint(1, 1000)) for _ in range(n)]
    updated = []
    for i, c in enumerate(created):
        if random.random() < 0.05:
            updated.append(c - timedelta(days=random.randint(1, 30)))  # inconsistent
        else:
            updated.append(c + timedelta(days=random.randint(0, 100)))

    return pd.DataFrame({
        "customer_id": base_ids,
        "email": emails,
        "name": [f"Customer_{i}" for i in range(n)],
        "age": ages,
        "status": statuses,
        "created_at": created,
        "updated_at": updated,
    })


def generate_orders(n: int = 50_000) -> pd.DataFrame:
    """Generate clean orders dataset — all checks should pass."""
    random.seed(SEED + 1)
    now = datetime.now()
    dates = [now - timedelta(days=random.randint(0, 365)) for _ in range(n)]
    return pd.DataFrame({
        "order_id": list(range(1, n + 1)),
        "customer_id": [random.randint(1, 10_000) for _ in range(n)],
        "amount": [round(random.uniform(1.0, 999.99), 2) for _ in range(n)],
        "currency": ["USD"] * n,
        "status": [random.choice(["completed", "pending", "shipped"]) for _ in range(n)],
        "order_date": dates,
    })


def generate_products(n: int = 1_000) -> pd.DataFrame:
    """Generate perfectly clean products dataset."""
    random.seed(SEED + 2)
    return pd.DataFrame({
        "product_id": list(range(1, n + 1)),
        "name": [f"Product_{i}" for i in range(1, n + 1)],
        "category": [random.choice(["Electronics", "Books", "Clothing"]) for _ in range(n)],
        "price": [round(random.uniform(5.0, 500.0), 2) for _ in range(n)],
        "in_stock": [True] * n,
        "created_at": [datetime.now() - timedelta(days=random.randint(1, 500)) for _ in range(n)],
    })


def generate_corrupted(n: int = 500) -> pd.DataFrame:
    """Generate severely corrupted dataset — everything should fail."""
    random.seed(SEED + 3)
    ids = [random.randint(1, 50) for _ in range(n)]  # massive duplicates
    emails = [None if random.random() < 0.4 else "garbage" for _ in range(n)]
    ages = [random.randint(-100, 300) for _ in range(n)]
    return pd.DataFrame({
        "id": ids,
        "email": emails,
        "value": [None if random.random() < 0.4 else "x" for _ in range(n)],
        "age": ages,
        "status": ["???"] * n,
    })


def main() -> None:
    """Generate all test datasets and write to OUTPUT_DIR."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "customers": generate_customers(),
        "orders": generate_orders(),
        "products": generate_products(),
        "corrupted": generate_corrupted(),
    }

    for name, df in datasets.items():
        csv_path = OUTPUT_DIR / f"{name}.csv"
        parquet_path = OUTPUT_DIR / f"{name}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        print(f"  {name}: {len(df)} rows → {csv_path.name}, {parquet_path.name}")

    print(f"\nAll datasets written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
