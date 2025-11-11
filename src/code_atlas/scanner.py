"""AST-based code scanner for extracting structure and metrics."""

import ast
import json
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from radon.complexity import cc_visit
from radon.raw import analyze

# Import optional dependencies for deep analysis
try:
    import mypy.api

    MYPY_AVAILABLE = True
except ImportError:
    MYPY_AVAILABLE = False


def extract_entities(tree: ast.AST) -> list[dict[str, Any]]:
    """Extract all classes and functions from AST.

    Args:
        tree: Parsed AST tree

    Returns:
        List of entity dicts with type, name, lineno, end_lineno, docstring
    """
    entities: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            bases = [ast.unparse(base) for base in node.bases]
            entities.append(
                {
                    "type": "class",
                    "name": node.name,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno or node.lineno,
                    "docstring": ast.get_docstring(node),
                    "methods": methods,
                    "bases": bases,
                }
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Only capture top-level functions, not methods
            entity_type = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            entities.append(
                {
                    "type": entity_type,
                    "name": node.name,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno or node.lineno,
                    "docstring": ast.get_docstring(node),
                }
            )

    return entities


def compute_metrics(source: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Compute complexity and raw metrics.

    Args:
        source: Python source code

    Returns:
        Tuple of (complexity list, raw metrics dict)
    """
    try:
        complexity = cc_visit(source)
        complexity_data = [
            {
                "function": item.name,
                "complexity": item.complexity,
                "lineno": item.lineno,
            }
            for item in complexity
        ]
    except Exception:  # noqa: S112
        complexity_data = []

    try:
        raw_metrics = analyze(source)
        raw = {
            "loc": raw_metrics.loc,
            "sloc": raw_metrics.sloc,
            "comments": raw_metrics.comments,
            "multi": raw_metrics.multi,
            "blank": raw_metrics.blank,
        }
    except Exception:  # noqa: S112
        raw = {"loc": 0, "sloc": 0, "comments": 0, "multi": 0, "blank": 0}

    return complexity_data, raw


def extract_git_metadata(path: Path) -> dict[str, Any]:
    """Extract commit count, last author, last date.

    Args:
        path: Path to file

    Returns:
        Dict with commits, last_author, last_commit
    """
    try:
        # Get commit count
        result = subprocess.run(  # noqa: S603
            ["git", "rev-list", "--count", "HEAD", "--", str(path)],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        commits = int(result.stdout.strip()) if result.returncode == 0 and result.stdout.strip() else 0

        # Get last author
        result = subprocess.run(  # noqa: S603
            ["git", "log", "-1", "--pretty=%an", "--", str(path)],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        last_author = result.stdout.strip() if result.returncode == 0 else ""

        # Get last commit date
        result = subprocess.run(  # noqa: S603
            ["git", "log", "-1", "--pretty=%ad", "--date=short", "--", str(path)],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else ""

        return {
            "commits": commits,
            "last_author": last_author,
            "last_commit": last_commit,
        }
    except Exception:  # noqa: S112
        return {"commits": 0, "last_author": "", "last_commit": ""}


def build_dependency_graph(files_data: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    """Build dependency graph showing imports and imported_by relationships.

    Args:
        files_data: List of file analysis dicts

    Returns:
        Dict mapping file paths to their dependencies
    """
    dependencies: dict[str, dict[str, list[str]]] = {}
    imports_map: dict[str, list[str]] = {}

    # First pass: extract all imports
    for file_data in files_data:
        file_path = file_data["path"]
        imports: list[str] = []

        try:
            # Re-read file to parse imports
            tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:  # noqa: S110, S112
            pass

        imports_map[file_path] = imports

    # Second pass: build imported_by relationships
    for file_path, imports in imports_map.items():
        dependencies[file_path] = {
            "imports": imports,
            "imported_by": [],
        }

    # Fill in imported_by
    for file_path, file_deps in dependencies.items():
        for imported_module in file_deps["imports"]:
            # Find files that match this module
            for other_path in dependencies:
                if imported_module in other_path or other_path.endswith(f"{imported_module.replace('.', '/')}.py"):
                    dependencies[other_path]["imported_by"].append(file_path)

    return dependencies


class ASTScanner:
    """Handles the scanning process for Python files."""

    def __init__(self, root: Path):
        """Initialize scanner with root directory.

        Args:
            root: Root directory to scan
        """
        self.root = root

    def scan_file(self, path: Path) -> dict[str, Any]:
        """Scan a single Python file and extract structure and metrics.

        Args:
            path: Path to Python file to scan

        Returns:
            Dictionary containing file analysis data
        """
        try:
            with open(path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(path))
            entities = extract_entities(tree)
            complexity_data, raw = compute_metrics(source)
            git_meta = extract_git_metadata(path)

            # Calculate comment ratio
            comment_ratio = raw["comments"] / raw["loc"] if raw["loc"] > 0 else 0.0

            # Check for test file
            test_path = str(path).replace("src/", "tests/test_").replace("\\", "/")
            has_tests = Path(test_path).exists()

            return {
                "path": str(path.relative_to(self.root) if path.is_relative_to(self.root) else path),
                "entities": entities,
                "complexity": complexity_data,
                "raw": raw,
                "comment_ratio": round(comment_ratio, 3),
                "git": git_meta,
                "has_tests": has_tests,
            }
        except SyntaxError as e:
            return {
                "path": str(path.relative_to(self.root) if path.is_relative_to(self.root) else path),
                "entities": [],
                "complexity": [],
                "raw": {"loc": 0, "sloc": 0, "comments": 0, "multi": 0, "blank": 0},
                "comment_ratio": 0.0,
                "git": {"commits": 0, "last_author": "", "last_commit": ""},
                "has_tests": False,
                "error": f"SyntaxError: {e.msg} at line {e.lineno}",
            }
        except Exception as e:  # noqa: S112
            return {
                "path": str(path.relative_to(self.root) if path.is_relative_to(self.root) else path),
                "entities": [],
                "complexity": [],
                "raw": {"loc": 0, "sloc": 0, "comments": 0, "multi": 0, "blank": 0},
                "comment_ratio": 0.0,
                "git": {"commits": 0, "last_author": "", "last_commit": ""},
                "has_tests": False,
                "error": str(e),
            }

    def _deep_analysis(self, path: Path) -> dict[str, Any]:
        """Perform deep analysis on a Python file.

        Args:
            path: Path to Python file

        Returns:
            Deep analysis results including type coverage and call graph
        """
        result: dict[str, Any] = {
            "type_coverage": 0.0,
            "type_errors": 0,
            "call_graph": {},
        }

        # Type coverage analysis with mypy
        if MYPY_AVAILABLE:
            try:
                # Run mypy on single file
                stdout, stderr, exit_code = mypy.api.run([str(path), "--show-error-codes", "--no-error-summary"])

                # Count errors
                error_count = stdout.count("error:")

                # Estimate type coverage (rough heuristic)
                # If no errors and exit_code == 0, assume good coverage
                if exit_code == 0:
                    result["type_coverage"] = 1.0
                else:
                    # Estimate based on error density
                    source = path.read_text(encoding="utf-8")
                    loc = len([line for line in source.splitlines() if line.strip()])
                    if loc > 0:
                        error_ratio = min(error_count / loc, 1.0)
                        result["type_coverage"] = max(0.0, 1.0 - error_ratio)

                result["type_errors"] = error_count

            except Exception:  # noqa: S110, S112
                pass

        # Call graph analysis (simple version - track function calls)
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            calls: dict[str, list[str]] = {}

            class CallVisitor(ast.NodeVisitor):
                """Visit function definitions and track their calls."""

                def __init__(self) -> None:
                    self.current_func: str | None = None

                def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                    """Visit function definition."""
                    self.current_func = node.name
                    calls[node.name] = []
                    self.generic_visit(node)
                    self.current_func = None

                def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                    """Visit async function definition."""
                    self.current_func = node.name
                    calls[node.name] = []
                    self.generic_visit(node)
                    self.current_func = None

                def visit_Call(self, node: ast.Call) -> None:
                    """Visit function call."""
                    if self.current_func:
                        # Extract called function name
                        if isinstance(node.func, ast.Name):
                            called = node.func.id
                            if called not in calls[self.current_func]:
                                calls[self.current_func].append(called)
                        elif isinstance(node.func, ast.Attribute):
                            called = node.func.attr
                            if called not in calls[self.current_func]:
                                calls[self.current_func].append(called)
                    self.generic_visit(node)

            visitor = CallVisitor()
            visitor.visit(tree)

            result["call_graph"] = calls

        except Exception:  # noqa: S110, S112
            pass

        return result

    def scan_directory(
        self,
        incremental: bool = False,
        deep: bool = False,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> dict[str, Any]:
        """Scan all Python files in directory recursively.

        Args:
            incremental: Use incremental caching to skip unchanged files
            deep: Enable deep analysis (call graphs, type coverage)
            progress_callback: Optional callback(file_path, current, total) for progress updates

        Returns:
            Complete code_index dict
        """
        from code_atlas.cache import FileCache

        files: list[dict[str, Any]] = []
        cache = FileCache() if incremental else None
        skipped_count = 0
        scanned_count = 0

        # Load existing index if incremental
        existing_data: dict[str, Any] = {}
        if incremental and cache:
            index_file = Path("code_index.json")
            if index_file.exists():
                try:
                    existing_data = json.loads(index_file.read_text(encoding="utf-8"))
                    # Build lookup for existing file data
                    existing_files = {f["path"]: f for f in existing_data.get("files", [])}
                except (json.JSONDecodeError, OSError):
                    existing_files = {}
            else:
                existing_files = {}

        # Collect all Python files first to know total count (skip common ignore patterns)
        ignore_patterns = {".venv", "venv", "__pycache__", ".git", "node_modules", ".pytest_cache", ".mypy_cache"}
        all_py_files = [
            f for f in self.root.rglob("*.py") if not any(ignored in f.parts for ignored in ignore_patterns)
        ]
        total_files = len(all_py_files)

        for idx, py_file in enumerate(all_py_files, 1):
            try:
                # Report progress
                if progress_callback:
                    rel_path = str(py_file.relative_to(self.root) if py_file.is_relative_to(self.root) else py_file)
                    progress_callback(rel_path, idx, total_files)

                # Check if file is unchanged (incremental mode)
                if cache and cache.is_unchanged(py_file):
                    # Reuse existing data
                    rel_path = str(py_file.relative_to(self.root) if py_file.is_relative_to(self.root) else py_file)
                    if rel_path in existing_files:
                        files.append(existing_files[rel_path])
                        skipped_count += 1
                        continue

                file_data = self.scan_file(py_file)

                # Add deep analysis if requested
                if deep:
                    file_data["deep"] = self._deep_analysis(py_file)

                files.append(file_data)
                scanned_count += 1

                # Update cache
                if cache:
                    cache.update_file(py_file)

            except Exception:  # noqa: S112
                # Skip files that cannot be parsed
                continue

        # Save cache
        if cache:
            # Cleanup stale entries
            existing_paths = {str(py_file) for py_file in self.root.rglob("*.py")}
            cache.cleanup(existing_paths)
            cache.save()

        # Build dependency graph
        dependencies = build_dependency_graph(files)

        # Build symbol index
        symbol_index: dict[str, str] = {}
        for file_data in files:
            for entity in file_data.get("entities", []):
                symbol_index[entity["name"]] = f"{file_data['path']}:{entity['lineno']}"

        index = {
            "scanned_root": str(self.root),
            "scanned_at": datetime.now().isoformat(),
            "version": "0.1.0",
            "total_files": len(files),
            "files": files,
            "dependencies": dependencies,
            "symbol_index": symbol_index,
        }

        return index


def scan_directory(
    root_path: Path,
    output_path: Path,
    incremental: bool = False,
    deep: bool = False,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> None:
    """Scan a directory of Python files and write index.

    Args:
        root_path: Root directory to scan
        output_path: Path to write code_index.json
        incremental: Use incremental caching to skip unchanged files
        deep: Enable deep analysis (call graphs, type coverage)
        progress_callback: Optional callback(file_path, current, total) for progress updates
    """
    scanner = ASTScanner(root_path)
    index = scanner.scan_directory(incremental=incremental, deep=deep, progress_callback=progress_callback)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
