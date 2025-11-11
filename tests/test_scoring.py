"""Tests for scoring module."""

import tempfile
from pathlib import Path

from code_atlas.scoring import ScoringEngine


def test_scoring_engine_init() -> None:
    """Test scoring engine initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        rules_file = tmppath / "rules.yaml"

        rules_file.write_text(
            """
weights:
  complexity: 0.6
  size: 0.3
  coupling: 0.1
""",
            encoding="utf-8",
        )

        se = ScoringEngine(rules_file)

        assert se.weights["complexity"] == 0.6
        assert se.weights["size"] == 0.3
        assert se.weights["coupling"] == 0.1


def test_scoring_engine_default_weights() -> None:
    """Test scoring engine uses defaults when no weights specified."""
    se = ScoringEngine("nonexistent.yaml")

    assert se.weights["complexity"] == 0.5
    assert se.weights["size"] == 0.3
    assert se.weights["coupling"] == 0.2


def test_score_file() -> None:
    """Test file scoring."""
    se = ScoringEngine("nonexistent.yaml")

    file_data = {
        "path": "test.py",
        "complexity": [
            {"function": "func1", "complexity": 10},
            {"function": "func2", "complexity": 20},
        ],
        "raw": {"loc": 100, "sloc": 80, "comments": 10, "blank": 10},
    }

    dependencies = {
        "test.py": {
            "imports": ["os", "sys", "json"],
            "imported_by": [],
        }
    }

    result = se.score_file(file_data, dependencies)

    assert result["file"] == "test.py"
    assert result["complexity"] == 15.0  # Average of 10 and 20
    assert result["loc"] == 100
    assert result["coupling"] == 3  # 3 imports
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0


def test_rank() -> None:
    """Test ranking files by score."""
    se = ScoringEngine("nonexistent.yaml")

    index = {
        "files": [
            {
                "path": "simple.py",
                "complexity": [{"function": "f1", "complexity": 5}],
                "raw": {"loc": 50},
            },
            {
                "path": "complex.py",
                "complexity": [
                    {"function": "f1", "complexity": 20},
                    {"function": "f2", "complexity": 30},
                ],
                "raw": {"loc": 500},
            },
            {
                "path": "medium.py",
                "complexity": [{"function": "f1", "complexity": 12}],
                "raw": {"loc": 200},
            },
        ],
        "dependencies": {
            "simple.py": {"imports": ["os"]},
            "complex.py": {"imports": ["os", "sys", "json", "typing", "pathlib"]},
            "medium.py": {"imports": ["os", "sys"]},
        },
    }

    results = se.rank(index)

    assert len(results) == 3
    # complex.py should rank highest (high complexity, high LOC, high coupling)
    assert results[0]["file"] == "complex.py"
    assert results[0]["score"] > results[1]["score"]
    assert results[1]["score"] > results[2]["score"]
