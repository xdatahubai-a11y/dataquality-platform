"""Tests for test data generation scripts."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.generate_test_data import (
    generate_corrupted,
    generate_customers,
    generate_orders,
    generate_products,
)


class TestCustomers:
    """Tests for the customers dataset."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.df = generate_customers()

    def test_row_count(self) -> None:
        assert len(self.df) == 10_000

    def test_null_emails_around_5_percent(self) -> None:
        null_pct = self.df["email"].isna().mean()
        assert 0.03 <= null_pct <= 0.08, f"Null email pct: {null_pct:.3f}"

    def test_duplicate_ids_around_2_percent(self) -> None:
        dup_pct = 1.0 - self.df["customer_id"].nunique() / len(self.df)
        assert 0.01 <= dup_pct <= 0.04, f"Dup pct: {dup_pct:.3f}"

    def test_has_invalid_ages(self) -> None:
        bad = ((self.df["age"] < 0) | (self.df["age"] > 150)).sum()
        assert bad > 0, "Expected some invalid ages"

    def test_columns(self) -> None:
        expected = {"customer_id", "email", "name", "age", "status", "created_at", "updated_at"}
        assert set(self.df.columns) == expected


class TestOrders:
    """Tests for the orders dataset."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.df = generate_orders()

    def test_row_count(self) -> None:
        assert len(self.df) == 50_000

    def test_all_unique_ids(self) -> None:
        assert self.df["order_id"].nunique() == len(self.df)

    def test_no_null_amounts(self) -> None:
        assert self.df["amount"].notna().all()

    def test_positive_amounts(self) -> None:
        assert (self.df["amount"] > 0).all()


class TestProducts:
    """Tests for the products dataset (clean control)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.df = generate_products()

    def test_row_count(self) -> None:
        assert len(self.df) == 1_000

    def test_all_unique_ids(self) -> None:
        assert self.df["product_id"].nunique() == len(self.df)

    def test_no_nulls(self) -> None:
        assert self.df.notna().all().all()


class TestCorrupted:
    """Tests for the corrupted dataset (negative control)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.df = generate_corrupted()

    def test_row_count(self) -> None:
        assert len(self.df) == 500

    def test_high_null_rate(self) -> None:
        null_pct = self.df["email"].isna().mean()
        assert null_pct >= 0.30, f"Expected >=30% nulls, got {null_pct:.3f}"

    def test_high_duplicate_rate(self) -> None:
        unique_pct = self.df["id"].nunique() / len(self.df)
        assert unique_pct < 0.50, f"Expected <50% unique IDs, got {unique_pct:.3f}"
