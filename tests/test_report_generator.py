"""Tests for HTML report generation."""

import pytest

from engine.report_generator import generate_html_report, _compute_dimension_scores


@pytest.fixture
def sample_results() -> dict:
    """Sample run results for testing."""
    return {
        "project": "Test Project",
        "source": "test_db",
        "timestamp": "2026-01-01 00:00:00",
        "results": [
            {"rule_name": "completeness_check", "dimension": "completeness",
             "column": "email", "metric_value": 95.0, "threshold": 90.0,
             "passed": True, "severity": "warning"},
            {"rule_name": "uniqueness_check", "dimension": "uniqueness",
             "column": "id", "metric_value": 80.0, "threshold": 99.0,
             "passed": False, "severity": "critical"},
            {"rule_name": "validity_check", "dimension": "validity",
             "column": "email", "metric_value": 92.0, "threshold": 90.0,
             "passed": True, "severity": "info"},
        ],
    }


def test_generates_valid_html(sample_results: dict) -> None:
    """Test that output is valid HTML."""
    html = generate_html_report(sample_results)
    assert "<!DOCTYPE html>" in html
    assert "</html>" in html
    assert "<style>" in html


def test_contains_project_name(sample_results: dict) -> None:
    """Test project name appears in report."""
    html = generate_html_report(sample_results)
    assert "Test Project" in html


def test_contains_all_rules(sample_results: dict) -> None:
    """Test all rule names appear in summary table."""
    html = generate_html_report(sample_results)
    assert "completeness_check" in html
    assert "uniqueness_check" in html
    assert "validity_check" in html


def test_pass_fail_badges(sample_results: dict) -> None:
    """Test pass/fail badges are present."""
    html = generate_html_report(sample_results)
    assert "✅ Pass" in html
    assert "❌ Fail" in html


def test_issues_section_shows_failures(sample_results: dict) -> None:
    """Test issues section lists failed rules."""
    html = generate_html_report(sample_results)
    assert "uniqueness_check" in html
    assert "CRITICAL" in html


def test_color_coding_green() -> None:
    """Test green color for high scores."""
    results = {
        "results": [
            {"rule_name": "r1", "dimension": "completeness", "column": "x",
             "metric_value": 99.0, "threshold": 90.0, "passed": True, "severity": "warning"},
        ]
    }
    html = generate_html_report(results)
    assert "green" in html


def test_color_coding_red() -> None:
    """Test red color for low scores."""
    results = {
        "results": [
            {"rule_name": "r1", "dimension": "completeness", "column": "x",
             "metric_value": 50.0, "threshold": 90.0, "passed": False, "severity": "critical"},
        ]
    }
    html = generate_html_report(results)
    assert "red" in html


def test_dimension_scores_calculation() -> None:
    """Test dimension score aggregation."""
    results = [
        {"dimension": "completeness", "metric_value": 80.0, "passed": True},
        {"dimension": "completeness", "metric_value": 60.0, "passed": False},
    ]
    scores = _compute_dimension_scores(results)
    assert scores["completeness"]["score"] == 70.0
    assert scores["completeness"]["passed"] == 1
    assert scores["completeness"]["total"] == 2


def test_empty_results() -> None:
    """Test report generation with no results."""
    html = generate_html_report({"results": []})
    assert "<!DOCTYPE html>" in html
    assert "No issues found" in html
