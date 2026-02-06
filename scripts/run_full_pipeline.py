#!/usr/bin/env python3
"""End-to-end DQ pipeline: create DB, run checks, generate reports.

Usage:
    python3 scripts/run_full_pipeline.py                              # Local only
    python3 scripts/run_full_pipeline.py --upload s3 --bucket my-bucket
    python3 scripts/run_full_pipeline.py --upload azure --account acct --container rpts
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from connectors.sqlite import SQLiteConnector
from engine.report_generator import generate_html_report
from engine.report_uploader import save_report_local
from engine.rule_engine import DQCheckResult, RuleDefinition, run_checks
from scripts.create_test_db import create_database

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def get_rules_for_table(table: str) -> list[RuleDefinition]:
    """Return DQ rules appropriate for each test table."""
    if table == "customers":
        return [
            RuleDefinition("email_completeness", "completeness", "email", threshold=95.0, severity="critical"),
            RuleDefinition("id_uniqueness", "uniqueness", "customer_id", threshold=99.0, severity="critical"),
            RuleDefinition("email_validity", "validity", "email",
                           config={"format": "email"}, threshold=90.0, severity="warning"),
            RuleDefinition("age_accuracy", "accuracy", "age",
                           config={"min_value": 0, "max_value": 150}, threshold=95.0, severity="warning"),
            RuleDefinition("date_consistency", "consistency", "created_at",
                           config={"column_a": "created_at", "column_b": "updated_at", "operator": "lte"},
                           threshold=90.0, severity="warning"),
        ]
    if table == "orders":
        return [
            RuleDefinition("order_id_unique", "uniqueness", "order_id", threshold=99.0, severity="critical"),
            RuleDefinition("amount_completeness", "completeness", "amount", threshold=99.0),
            RuleDefinition("amount_range", "accuracy", "amount",
                           config={"min_value": 0, "max_value": 10000}, threshold=99.0),
        ]
    if table == "products":
        return [
            RuleDefinition("product_id_unique", "uniqueness", "product_id", threshold=99.0),
            RuleDefinition("name_completeness", "completeness", "name", threshold=99.0),
            RuleDefinition("price_range", "accuracy", "price",
                           config={"min_value": 0, "max_value": 10000}, threshold=99.0),
        ]
    # corrupted
    return [
        RuleDefinition("id_uniqueness", "uniqueness", "id", threshold=90.0, severity="critical"),
        RuleDefinition("email_completeness", "completeness", "email", threshold=80.0, severity="critical"),
        RuleDefinition("value_completeness", "completeness", "value", threshold=80.0, severity="warning"),
    ]


def run_pipeline(upload: str | None = None, **upload_kwargs: str) -> None:
    """Execute the full DQ pipeline."""
    print("=" * 60)
    print("  DataQuality Platform — Full Pipeline")
    print("=" * 60)

    # 1. Create test database
    print("\n📦 Creating test database...")
    db_path = create_database()

    # 2. Connect
    connector = SQLiteConnector()
    connector.connect({"database": str(db_path)})
    tables = connector.list_tables()
    print(f"\n📋 Tables found: {tables}")

    # 3. Run checks per table and generate reports
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    all_table_results: dict[str, list[dict]] = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for table in tables:
        print(f"\n🔍 Checking: {table}")
        data = connector.read_data(table)
        rules = get_rules_for_table(table)
        results = run_checks(rules, data)

        result_dicts = []
        for r in results:
            result_dicts.append({
                "rule_name": r.rule_name, "dimension": r.dimension,
                "column": r.column, "metric_value": r.metric_value,
                "threshold": r.threshold, "passed": r.passed,
                "severity": next(
                    (rule.severity for rule in rules if rule.name == r.rule_name),
                    "warning",
                ),
            })

        passed = sum(1 for r in results if r.passed)
        print(f"   {passed}/{len(results)} rules passed")
        all_table_results[table] = result_dicts

        # Generate per-table report
        html = generate_html_report({
            "project": "DataQuality Platform",
            "source": f"SQLite — {table}",
            "timestamp": timestamp,
            "results": result_dicts,
        })
        path = save_report_local(html, str(REPORTS_DIR / f"{table}_report.html"))
        print(f"   📄 Report: {path}")

    # 4. Combined summary report
    all_results = []
    for table, results in all_table_results.items():
        for r in results:
            r_copy = dict(r)
            r_copy["rule_name"] = f"[{table}] {r_copy['rule_name']}"
            all_results.append(r_copy)

    combined_html = generate_html_report({
        "project": "DataQuality Platform — Combined",
        "source": f"SQLite ({len(tables)} tables)",
        "timestamp": timestamp,
        "results": all_results,
    })
    combined_path = save_report_local(combined_html, str(REPORTS_DIR / "combined_report.html"))
    print(f"\n📊 Combined report: {combined_path}")

    # 5. Upload if requested
    if upload == "s3":
        from engine.report_uploader import upload_report_to_s3
        url = upload_report_to_s3(combined_html, upload_kwargs["bucket"], "dq/combined.html")
        print(f"☁️  Uploaded to S3: {url}")
    elif upload == "azure":
        from engine.report_uploader import upload_report_to_azure_blob
        url = upload_report_to_azure_blob(
            combined_html, upload_kwargs["account"], upload_kwargs["container"], "dq/combined.html"
        )
        print(f"☁️  Uploaded to Azure: {url}")

    # 6. Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for table, results in all_table_results.items():
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        icon = "✅" if passed == total else "⚠️"
        print(f"  {icon} {table}: {passed}/{total} passed")

    total_p = sum(1 for r in all_results if r["passed"])
    total_r = len(all_results)
    print(f"\n  Total: {total_p}/{total_r} rules passed")
    print("=" * 60)

    connector.close()


def main() -> None:
    """Parse args and run pipeline."""
    parser = argparse.ArgumentParser(description="Run DQ pipeline")
    parser.add_argument("--upload", choices=["s3", "azure"], default=None)
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--account", default=None)
    parser.add_argument("--container", default=None)
    args = parser.parse_args()

    run_pipeline(
        upload=args.upload,
        bucket=args.bucket or "",
        account=args.account or "",
        container=args.container or "",
    )


if __name__ == "__main__":
    main()
