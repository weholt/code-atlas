"""Tests for rules module."""

import tempfile
from pathlib import Path

from code_atlas.rules import RuleEngine


def test_rule_engine_init() -> None:
    """Test rule engine initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        rules_file = tmppath / "rules.yaml"

        rules_file.write_text(
            """
metrics:
  max_complexity: 10

actions:
  - id: R001
    condition: "complexity > max_complexity"
    message: "Too complex"
    action: "Refactor"
""",
            encoding="utf-8",
        )

        re = RuleEngine(rules_file)

        assert "metrics" in re.config
        assert "actions" in re.config
        assert len(re.config["actions"]) == 1


def test_rule_engine_evaluate() -> None:
    """Test rule evaluation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        rules_file = tmppath / "rules.yaml"

        rules_file.write_text(
            """
metrics:
  max_complexity: 10

actions:
  - id: R001
    condition: "complexity > max_complexity"
    message: "Too complex"
    action: "Refactor"
""",
            encoding="utf-8",
        )

        re = RuleEngine(rules_file)
        file_data = {"path": "test.py", "complexity": 15}

        issues = re.evaluate(file_data)

        assert isinstance(issues, list)
