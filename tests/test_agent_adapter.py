"""Tests for agent adapter convenience API."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from code_atlas.agent_adapter import AgentAdapter


@pytest.fixture
def mock_index_data():
    """Sample index data for testing."""
    return {
        "scanned_at": "2024-01-01T12:00:00",
        "files": [
            {
                "path": "module_a.py",
                "entities": [{"name": "ClassA", "type": "class", "lineno": 10}],
                "raw": {"loc": 100, "lloc": 80, "sloc": 90, "comments": 10, "blank": 0},
                "comment_ratio": 0.1,
                "functions": [{"name": "func_a", "complexity": 15}],
            },
            {
                "path": "module_b.py",
                "entities": [],
                "raw": {"loc": 50, "lloc": 40, "sloc": 45, "comments": 5, "blank": 0},
                "comment_ratio": 0.1,
                "functions": [],
            },
            {
                "path": "module_c.py",
                "entities": [],
                "raw": {"loc": 200, "lloc": 180, "sloc": 190, "comments": 5, "blank": 0},
                "comment_ratio": 0.025,
                "functions": [],
            },
        ],
        "dependencies": {
            "module_a.py": {"imports": ["os", "sys"], "imported_by": ["module_b.py", "module_c.py", "module_d.py"]},
            "module_b.py": {"imports": ["module_a"], "imported_by": []},
        },
    }


@pytest.fixture
def adapter_with_mocks(tmp_path, mock_index_data):
    """Create adapter with mocked components."""
    index_file = tmp_path / "code_index.json"
    rules_file = tmp_path / "rules.yaml"

    # Create empty files
    index_file.write_text("{}")
    rules_file.write_text("metrics: {}\nweights: {}\nrules: []")

    with (
        patch("code_atlas.agent_adapter.CodeIndex") as mock_code_index,
        patch("code_atlas.agent_adapter.RuleEngine") as mock_rule_engine,
        patch("code_atlas.agent_adapter.ScoringEngine") as mock_scoring_engine,
    ):
        # Configure CodeIndex mock
        mock_ci_instance = MagicMock()
        mock_ci_instance.data = mock_index_data
        mock_ci_instance.find.return_value = {"name": "ClassA", "file": "module_a.py", "lineno": 10}
        mock_ci_instance.complex.return_value = [{"name": "func_a", "complexity": 15}]
        mock_code_index.return_value = mock_ci_instance

        # Configure RuleEngine mock
        mock_re_instance = MagicMock()
        mock_re_instance.evaluate.return_value = [{"rule_id": "RULE-001", "file": "module_a.py"}]
        mock_rule_engine.return_value = mock_re_instance

        # Configure ScoringEngine mock
        mock_se_instance = MagicMock()
        mock_se_instance.rank.return_value = [{"file": "module_a.py", "score": 85.0}]
        mock_scoring_engine.return_value = mock_se_instance

        adapter = AgentAdapter(tmp_path, str(index_file), str(rules_file))
        adapter.index.data = mock_index_data  # Ensure data is accessible

        yield adapter


def test_agent_adapter_init(tmp_path):
    """Test adapter initialization."""
    index_file = tmp_path / "code_index.json"
    rules_file = tmp_path / "rules.yaml"

    index_file.write_text("{}")
    rules_file.write_text("metrics: {}\nweights: {}\nrules: []")

    with (
        patch("code_atlas.agent_adapter.CodeIndex"),
        patch("code_atlas.agent_adapter.RuleEngine"),
        patch("code_atlas.agent_adapter.ScoringEngine"),
    ):
        adapter = AgentAdapter(tmp_path, str(index_file), str(rules_file))

        assert adapter.root == tmp_path
        assert adapter.index_path == index_file
        assert adapter.rules_path == rules_file


def test_get_symbol_location(adapter_with_mocks):
    """Test symbol location lookup."""
    result = adapter_with_mocks.get_symbol_location("ClassA")

    assert result is not None
    assert result["name"] == "ClassA"
    assert result["file"] == "module_a.py"


def test_get_top_refactors(adapter_with_mocks):
    """Test top refactor targets."""
    results = adapter_with_mocks.get_top_refactors(limit=5)

    assert len(results) == 1
    assert results[0]["file"] == "module_a.py"
    assert results[0]["score"] == 85.0


def test_get_rule_violations(adapter_with_mocks):
    """Test rule violation collection."""
    violations = adapter_with_mocks.get_rule_violations()

    # Should have violations from all files (3 files in mock data)
    assert len(violations) >= 3
    assert violations[0]["rule_id"] == "RULE-001"


def test_get_complex_functions(adapter_with_mocks):
    """Test complex function discovery."""
    results = adapter_with_mocks.get_complex_functions(threshold=10)

    assert len(results) == 1
    assert results[0]["name"] == "func_a"
    assert results[0]["complexity"] == 15


def test_get_dependency_hotspots(adapter_with_mocks):
    """Test dependency hotspot detection."""
    hotspots = adapter_with_mocks.get_dependency_hotspots(min_edges=3)

    assert len(hotspots) == 1
    assert hotspots[0]["file"] == "module_a.py"
    assert hotspots[0]["total_coupling"] == 5  # 2 imports + 3 imported_by


def test_get_untyped_or_poor_docs(adapter_with_mocks):
    """Test poor documentation detection."""
    poor_docs = adapter_with_mocks.get_untyped_or_poor_docs(min_comment_ratio=0.05)

    # module_c.py has 0.025 comment ratio (< 0.05 threshold)
    assert len(poor_docs) == 1
    assert poor_docs[0]["file"] == "module_c.py"
    assert poor_docs[0]["comment_ratio"] == 0.025


def test_summarize_state(adapter_with_mocks):
    """Test state summary generation."""
    summary = adapter_with_mocks.summarize_state()

    assert summary["total_files"] == 3
    assert summary["total_loc"] == 350  # 100 + 50 + 200
    assert summary["complex_functions"] == 1
    assert summary["rule_violations"] >= 3
    assert summary["dependency_hotspots"] == 1
    assert summary["scanned_at"] == "2024-01-01T12:00:00"


def test_adapter_without_rules(tmp_path):
    """Test adapter when rules file doesn't exist."""
    index_file = tmp_path / "code_index.json"
    index_file.write_text("{}")

    with patch("code_atlas.agent_adapter.CodeIndex"):
        adapter = AgentAdapter(tmp_path, str(index_file), "nonexistent_rules.yaml")

        assert adapter.rules is None
        assert adapter.scoring is None

        # Should return empty lists when rules/scoring unavailable
        assert adapter.get_top_refactors() == []
        assert adapter.get_rule_violations() == []
