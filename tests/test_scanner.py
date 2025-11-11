"""Tests for scanner module."""

import tempfile
from pathlib import Path

from code_atlas.scanner import ASTScanner, scan_directory


def test_scan_file_basic() -> None:
    """Test scanning a simple Python file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        test_file = tmppath / "test.py"
        test_file.write_text(
            '''def hello() -> str:
    """Say hello."""
    return "hello"

class Greeter:
    """A greeter class."""
    
    def greet(self, name: str) -> str:
        """Greet someone."""
        return f"Hello, {name}"
''',
            encoding="utf-8",
        )

        scanner = ASTScanner(tmppath)
        result = scanner.scan_file(test_file)

        assert "path" in result
        assert "entities" in result
        assert len(result["entities"]) >= 2


def test_scan_directory() -> None:
    """Test scanning a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        test_file = tmppath / "test.py"
        test_file.write_text("def foo() -> None:\n    pass\n", encoding="utf-8")

        output_file = tmppath / "index.json"
        scan_directory(tmppath, output_file)

        assert output_file.exists()
