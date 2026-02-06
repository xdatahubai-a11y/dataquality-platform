"""DQ Rule Engine — parses, loads, and evaluates data quality rules."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from engine.dimensions.accuracy import AccuracyCalculator
from engine.dimensions.completeness import CompletenessCalculator
from engine.dimensions.consistency import ConsistencyCalculator
from engine.dimensions.timeliness import TimelinessCalculator
from engine.dimensions.uniqueness import UniquenessCalculator
from engine.dimensions.validity import ValidityCalculator


@dataclass
class RuleDefinition:
    """Parsed rule definition."""

    name: str
    dimension: str
    column: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    config: dict = field(default_factory=dict)
    severity: str = "warning"


@dataclass
class DQCheckResult:
    """Result of a single DQ check."""

    rule_name: str
    dimension: str
    column: Optional[str]
    metric_value: float
    threshold: Optional[float]
    passed: bool
    details: dict = field(default_factory=dict)


DIMENSION_CALCULATORS = {
    "completeness": CompletenessCalculator(),
    "uniqueness": UniquenessCalculator(),
    "accuracy": AccuracyCalculator(),
    "consistency": ConsistencyCalculator(),
    "timeliness": TimelinessCalculator(),
    "validity": ValidityCalculator(),
}


def load_rules_from_yaml(path: str | Path) -> list[RuleDefinition]:
    """Load rule definitions from a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        List of parsed RuleDefinition objects.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    rules: list[RuleDefinition] = []
    for check in data.get("checks", []):
        rules.append(
            RuleDefinition(
                name=check.get("name", "unnamed"),
                dimension=check["dimension"],
                column=check.get("column"),
                operator=check.get("operator", "gte"),
                threshold=check.get("threshold"),
                config=check.get("config", {}),
                severity=check.get("severity", "warning"),
            )
        )
    return rules


def evaluate_rule(rule: RuleDefinition, data: Any) -> DQCheckResult:
    """Evaluate a single rule against a dataset.

    Args:
        rule: The rule definition to evaluate.
        data: The dataset (list of dicts for non-Spark, DataFrame for Spark).

    Returns:
        DQCheckResult with metric value and pass/fail status.
    """
    calculator = DIMENSION_CALCULATORS.get(rule.dimension)
    if not calculator:
        return DQCheckResult(
            rule_name=rule.name,
            dimension=rule.dimension,
            column=rule.column,
            metric_value=0.0,
            threshold=rule.threshold,
            passed=False,
            details={"error": f"Unknown dimension: {rule.dimension}"},
        )

    metric_value = calculator.calculate(data, rule.column, rule.config)

    passed = True
    if rule.threshold is not None:
        op = rule.operator or "gte"
        if op == "gte":
            passed = metric_value >= rule.threshold
        elif op == "lte":
            passed = metric_value <= rule.threshold
        elif op == "eq":
            passed = abs(metric_value - rule.threshold) < 0.001
        elif op == "gt":
            passed = metric_value > rule.threshold
        elif op == "lt":
            passed = metric_value < rule.threshold

    return DQCheckResult(
        rule_name=rule.name,
        dimension=rule.dimension,
        column=rule.column,
        metric_value=round(metric_value, 4),
        threshold=rule.threshold,
        passed=passed,
    )


def run_checks(rules: list[RuleDefinition], data: Any) -> list[DQCheckResult]:
    """Run all rules against a dataset and return results.

    Args:
        rules: List of rules to evaluate.
        data: The dataset.

    Returns:
        List of DQCheckResult objects.
    """
    return [evaluate_rule(rule, data) for rule in rules]
