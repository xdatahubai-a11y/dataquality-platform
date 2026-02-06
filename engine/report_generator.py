"""HTML report generator for data quality results.

Produces a self-contained HTML file with inline CSS — no external dependencies.
"""

from datetime import datetime
from typing import Any

from engine.report_sections import (
    build_dimension_breakdown,
    build_footer,
    build_header,
    build_issues_section,
    build_score_cards,
    build_summary_table,
)
from engine.report_styles import get_report_css


def _compute_dimension_scores(results: list[dict]) -> dict[str, dict]:
    """Aggregate pass/fail counts and scores per dimension."""
    dims: dict[str, dict] = {}
    for r in results:
        dim = r["dimension"]
        if dim not in dims:
            dims[dim] = {"passed": 0, "total": 0, "sum": 0.0}
        dims[dim]["total"] += 1
        dims[dim]["sum"] += r["metric_value"]
        if r["passed"]:
            dims[dim]["passed"] += 1

    for dim, info in dims.items():
        info["score"] = info["sum"] / info["total"] if info["total"] else 0.0
    return dims


def generate_html_report(run_results: dict) -> str:
    """Generate a self-contained HTML data quality report.

    Args:
        run_results: Dict with keys:
            - project: str (project name)
            - source: str (data source name)
            - timestamp: str (ISO timestamp)
            - results: list[dict] with keys:
                rule_name, dimension, column, metric_value,
                threshold, passed, severity

    Returns:
        Complete HTML string.
    """
    project = run_results.get("project", "Data Quality Report")
    source = run_results.get("source", "Unknown")
    timestamp = run_results.get("timestamp", datetime.now().isoformat())
    results = run_results.get("results", [])

    dim_scores = _compute_dimension_scores(results)

    total_score = 0.0
    if dim_scores:
        total_score = sum(d["score"] for d in dim_scores.values()) / len(dim_scores)

    css = get_report_css()
    header = build_header(project, source, total_score, timestamp)
    cards = build_score_cards(dim_scores)
    table = build_summary_table(results)
    breakdown = build_dimension_breakdown(dim_scores, results)
    issues = build_issues_section(results)
    footer = build_footer()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project} - DQ Report</title>
  <style>{css}</style>
</head>
<body>
  {header}
  <div class="container">
    {cards}
    {table}
    {breakdown}
    {issues}
  </div>
  {footer}
</body>
</html>"""
