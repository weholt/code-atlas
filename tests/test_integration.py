"""Integration tests for scanner + query pipeline."""

import tempfile
from pathlib import Path

from code_atlas.query import CodeIndex
from code_atlas.scanner import ASTScanner


def test_scan_and_query_integration() -> None:
    """Test full pipeline: scan directory, load index, query results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create sample Python files
        (tmppath / "module1.py").write_text(
            '''"""Sample module."""

def simple_function():
    """A simple function."""
    return 42

class SampleClass:
    """A sample class."""
    
    def method_one(self):
        """Method one."""
        if True:
            if True:
                if True:
                    return "nested"
        return "deep"
''',
            encoding="utf-8",
        )

        (tmppath / "module2.py").write_text(
            '''"""Another module."""
import os
from pathlib import Path

def complex_function(x, y, z):
    """Complex function."""
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(10):
                    if i % 2 == 0:
                        return i
    return 0
''',
            encoding="utf-8",
        )

        # Scan the directory
        scanner = ASTScanner(tmppath)
        index_data = scanner.scan_directory()

        # Verify scan results
        assert index_data["scanned_root"] == str(tmppath)
        assert index_data["version"] == "0.1.0"
        assert len(index_data["files"]) == 2

        # Write index to file
        index_file = tmppath / "code_index.json"
        import json

        index_file.write_text(json.dumps(index_data, indent=2), encoding="utf-8")

        # Load with CodeIndex
        ci = CodeIndex(index_file)

        # Test find()
        simple_func = ci.find("simple_function")
        assert simple_func is not None
        assert simple_func["type"] == "function"
        assert "module1.py" in simple_func["file"]

        sample_class = ci.find("SampleClass")
        assert sample_class is not None
        assert sample_class["type"] == "class"

        # Test complex()
        complex_funcs = ci.complex(threshold=5)
        assert len(complex_funcs) >= 1

        # Test top_complex()
        top_funcs = ci.top_complex(n=2)
        assert len(top_funcs) <= 2
        assert all("complexity" in f for f in top_funcs)

        # Test dependencies()
        for file_info in index_data["files"]:
            deps = ci.dependencies(file_info["path"])
            assert "imports" in deps
            assert "imported_by" in deps
