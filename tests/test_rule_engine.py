"""Tests for the DQ rule engine."""

from engine.rule_engine import RuleDefinition, evaluate_rule, load_rules_from_yaml, run_checks


def test_load_rules_from_yaml(sample_rules_yaml):
    """Test loading rules from YAML file."""
    rules = load_rules_from_yaml(sample_rules_yaml)
    assert len(rules) == 3
    assert rules[0].name == "name_completeness"
    assert rules[0].dimension == "completeness"
    assert rules[1].dimension == "uniqueness"
    assert rules[2].dimension == "validity"


def test_evaluate_rule_completeness(sample_data):
    """Test evaluating a completeness rule."""
    rule = RuleDefinition(name="test", dimension="completeness", column="name", threshold=80.0, operator="gte")
    result = evaluate_rule(rule, sample_data)
    assert result.metric_value == 80.0  # 4 out of 5 non-null
    assert result.passed is True


def test_evaluate_rule_fails(sample_data):
    """Test a rule that should fail."""
    rule = RuleDefinition(name="test", dimension="completeness", column="email", threshold=95.0, operator="gte")
    result = evaluate_rule(rule, sample_data)
    assert result.passed is False


def test_evaluate_unknown_dimension(sample_data):
    """Test evaluating a rule with unknown dimension."""
    rule = RuleDefinition(name="test", dimension="nonexistent", column="name")
    result = evaluate_rule(rule, sample_data)
    assert result.passed is False
    assert "error" in result.details


def test_run_checks_batch(sample_data):
    """Test running multiple checks at once."""
    rules = [
        RuleDefinition(name="r1", dimension="completeness", column="name", threshold=50.0, operator="gte"),
        RuleDefinition(name="r2", dimension="uniqueness", column="id", threshold=100.0, operator="gte"),
    ]
    results = run_checks(rules, sample_data)
    assert len(results) == 2
    assert results[0].passed is True  # 80% >= 50%


def test_evaluate_operators(sample_data):
    """Test different comparison operators."""
    rule_lte = RuleDefinition(name="test", dimension="completeness", column="name", threshold=90.0, operator="lte")
    assert evaluate_rule(rule_lte, sample_data).passed is True  # 80 <= 90

    rule_eq = RuleDefinition(name="test", dimension="completeness", column="name", threshold=80.0, operator="eq")
    assert evaluate_rule(rule_eq, sample_data).passed is True
