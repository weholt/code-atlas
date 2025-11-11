"""Tests for query module."""

import json
import tempfile
from pathlib import Path

from code_atlas.query import CodeIndex


def test_code_index_find() -> None:
    """Test finding entities by name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        index_file = tmppath / "index.json"

        index_data = {
            "scanned_root": "/tmp",
            "scanned_at": "2025-11-11T00:00:00",
            "version": "0.1.0",
            "files": [
                {
                    "path": "test.py",
                    "entities": [
                        {
                            "type": "function",
                            "name": "hello",
                            "lineno": 1,
                            "end_lineno": 2,
                            "docstring": "Say hello",
                        }
                    ],
                    "complexity": [],
                    "raw": {"loc": 10, "sloc": 8, "comments": 1, "multi": 0, "blank": 1},
                }
            ],
            "dependencies": {},
        }
        index_file.write_text(json.dumps(index_data), encoding="utf-8")

        ci = CodeIndex(index_file)
        result = ci.find("hello")

        assert result is not None
        assert result["type"] == "function"
        assert result["file"] == "test.py"


def test_code_index_complex() -> None:
    """Test finding complex functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        index_file = tmppath / "index.json"

        index_data = {
            "scanned_root": "/tmp",
            "scanned_at": "2025-11-11T00:00:00",
            "version": "0.1.0",
            "files": [
                {
                    "path": "test.py",
                    "entities": [],
                    "complexity": [{"function": "complex_func", "complexity": 15, "lineno": 10}],
                    "raw": {"loc": 50, "sloc": 40, "comments": 5, "multi": 0, "blank": 5},
                }
            ],
            "dependencies": {},
        }
        index_file.write_text(json.dumps(index_data), encoding="utf-8")

        ci = CodeIndex(index_file)
        results = ci.complex(threshold=10)

        assert len(results) == 1
        assert results[0]["function"] == "complex_func"
        assert results[0]["complexity"] == 15


def test_code_index_dependencies() -> None:
    """Test getting file dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        index_file = tmppath / "index.json"

        index_data = {
            "scanned_root": "/tmp",
            "scanned_at": "2025-11-11T00:00:00",
            "version": "0.1.0",
            "files": [],
            "dependencies": {
                "test.py": {
                    "imports": ["os", "sys"],
                    "imported_by": ["main.py"],
                }
            },
        }
        index_file.write_text(json.dumps(index_data), encoding="utf-8")

        ci = CodeIndex(index_file)
        deps = ci.dependencies("test.py")

        assert deps["imports"] == ["os", "sys"]
        assert deps["imported_by"] == ["main.py"]


def test_code_index_top_complex() -> None:
    """Test getting top N most complex functions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        index_file = tmppath / "index.json"

        index_data = {
            "scanned_root": "/tmp",
            "scanned_at": "2025-11-11T00:00:00",
            "version": "0.1.0",
            "files": [
                {
                    "path": "test1.py",
                    "entities": [],
                    "complexity": [
                        {"function": "func_a", "complexity": 20, "lineno": 1},
                        {"function": "func_b", "complexity": 5, "lineno": 10},
                    ],
                    "raw": {"loc": 50, "sloc": 40, "comments": 5, "multi": 0, "blank": 5},
                },
                {
                    "path": "test2.py",
                    "entities": [],
                    "complexity": [
                        {"function": "func_c", "complexity": 15, "lineno": 1},
                        {"function": "func_d", "complexity": 25, "lineno": 20},
                    ],
                    "raw": {"loc": 60, "sloc": 50, "comments": 5, "multi": 0, "blank": 5},
                },
            ],
            "dependencies": {},
        }
        index_file.write_text(json.dumps(index_data), encoding="utf-8")

        ci = CodeIndex(index_file)
        results = ci.top_complex(n=3)

        assert len(results) == 3
        assert results[0]["function"] == "func_d"
        assert results[0]["complexity"] == 25
        assert results[1]["function"] == "func_a"
        assert results[1]["complexity"] == 20
        assert results[2]["function"] == "func_c"
        assert results[2]["complexity"] == 15
