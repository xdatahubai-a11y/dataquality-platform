#!/usr/bin/env python3
"""Run full DQ checks against test datasets and validate expected results.

Reads generated CSVs, applies DQ dimension checks, and compares
actual scores against expected thresholds.
"""

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"

# Expected results: (dataset, dimension, column, threshold, expected_pass)
EXPECTATIONS: list[tuple[str, str, str, float, bool]] = [
    # customers — mixed
    ("customers", "completeness", "email", 0.95, False),
    ("customers", "uniqueness", "customer_id", 1.0, False),
    ("customers", "validity", "email", 0.90, True),
    ("customers", "accuracy", "age", 0.95, True),
    # orders — clean
    ("orders", "completeness", "order_id", 1.0, True),
    ("orders", "uniqueness", "order_id", 1.0, True),
    ("orders", "accuracy", "amount", 0.99, True),
    # products — perfect
    ("products", "completeness", "product_id", 1.0, True),
    ("products", "uniqueness", "product_id", 1.0, True),
    # corrupted — all fail
    ("corrupted", "completeness", "email", 0.90, False),
    ("corrupted", "uniqueness", "id", 0.90, False),
    ("corrupted", "completeness", "value", 0.90, False),
]


def check_completeness(df: pd.DataFrame, column: str) -> float:
    """Return fraction of non-null values."""
    return float(df[column].notna().mean())


def check_uniqueness(df: pd.DataFrame, column: str) -> float:
    """Return fraction of unique values."""
    total = len(df)
    return float(df[column].nunique() / total) if total > 0 else 1.0


def check_accuracy_numeric(df: pd.DataFrame, column: str, lo: float = 0, hi: float = 150) -> float:
    """Return fraction of values within [lo, hi]."""
    s = pd.to_numeric(df[column], errors="coerce")
    valid = s.between(lo, hi)
    return float(valid.mean())


def evaluate(dataset: str, dimension: str, column: str) -> float:
    """Evaluate a single DQ dimension on a dataset column."""
    csv_path = DATA_DIR / f"{dataset}.csv"
    df = pd.read_csv(csv_path)
    if dimension == "completeness":
        return check_completeness(df, column)
    elif dimension == "uniqueness":
        return check_uniqueness(df, column)
    elif dimension == "accuracy":
        if dataset == "orders":
            return check_accuracy_numeric(df, column, lo=0, hi=10000)
        return check_accuracy_numeric(df, column)
    elif dimension == "validity":
        # Simplified: check email-like pattern
        valid = df[column].dropna().str.match(r"^[^@]+@[^@]+\.[^@]+$")
        return float(valid.mean()) if len(valid) > 0 else 0.0
    return 1.0


def main() -> int:
    """Run all checks and print results matrix."""
    print(f"{'Dataset':<12} {'Dimension':<14} {'Column':<14} {'Threshold':<10} {'Score':<8} {'Pass':<6} {'Expected':<10} {'Match'}")
    print("-" * 100)

    mismatches = 0
    for dataset, dimension, column, threshold, expected_pass in EXPECTATIONS:
        score = evaluate(dataset, dimension, column)
        actual_pass = score >= threshold
        match = actual_pass == expected_pass
        if not match:
            mismatches += 1
        status = "✓" if match else "✗ MISMATCH"

        print(f"{dataset:<12} {dimension:<14} {column:<14} {threshold:<10.2f} {score:<8.4f} {str(actual_pass):<6} {str(expected_pass):<10} {status}")

    print(f"\n{'='*100}")
    print(f"Total: {len(EXPECTATIONS)} checks, {mismatches} mismatches")

    if mismatches > 0:
        print("FAIL: Some expected results did not match.")
        return 1
    print("PASS: All expected results matched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
