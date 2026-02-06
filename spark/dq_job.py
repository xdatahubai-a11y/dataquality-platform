"""Main Spark job for executing DQ checks at scale.

This is the entry point for spark-submit. It reads job config,
loads data via the appropriate connector, runs DQ checks, and
writes results back.
"""

import json
import sys
from datetime import datetime
from typing import Any


def run_dq_checks(job_config: dict) -> dict:
    """Execute DQ checks based on job configuration.

    Args:
        job_config: Dict with keys: source_type, source_config, rules, output_path.

    Returns:
        Dict with run results summary.
    """
    from engine.rule_engine import RuleDefinition, run_checks

    # Load data via connector
    data = _load_data(job_config)

    # Parse rules
    rules = [
        RuleDefinition(
            name=r["name"],
            dimension=r["dimension"],
            column=r.get("column"),
            operator=r.get("operator", "gte"),
            threshold=r.get("threshold"),
            config=r.get("config", {}),
            severity=r.get("severity", "warning"),
        )
        for r in job_config.get("rules", [])
    ]

    # Run checks
    results = run_checks(rules, data)

    # Summarize
    passed = sum(1 for r in results if r.passed)
    summary = {
        "total_rules": len(results),
        "passed_rules": passed,
        "failed_rules": len(results) - passed,
        "results": [
            {
                "rule_name": r.rule_name,
                "dimension": r.dimension,
                "column": r.column,
                "metric_value": r.metric_value,
                "threshold": r.threshold,
                "passed": r.passed,
            }
            for r in results
        ],
        "completed_at": datetime.utcnow().isoformat(),
    }

    return summary


def _load_data(job_config: dict) -> list[dict]:
    """Load data from the configured source."""
    source_type = job_config.get("source_type", "")
    source_config = job_config.get("source_config", {})
    path = job_config.get("data_path", "")

    if source_type == "adls_gen2":
        from connectors.adls_gen2 import ADLSGen2Connector
        connector = ADLSGen2Connector()
    elif source_type == "delta_table":
        from connectors.delta_table import DeltaTableConnector
        connector = DeltaTableConnector()
    elif source_type == "sql_server":
        from connectors.sql_server import SQLServerConnector
        connector = SQLServerConnector()
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    connector.connect(source_config)
    return connector.read_data(path, limit=job_config.get("sample_limit"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: spark-submit dq_job.py <config.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        config = json.load(f)

    result = run_dq_checks(config)
    print(json.dumps(result, indent=2))
