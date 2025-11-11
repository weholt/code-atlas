# PyStructMap - Critical Priority Tasks

## Group 1: Core Scanner Infrastructure (Tasks 1-10)

---
id: "PSM-CRIT-001"
title: "Create package structure and core imports"
description: "Set up src/pystructmap package with __init__.py and __version__"
priority: critical
status: ⏸️ proposed
---

**Context**:
Initialize the pystructmap package structure with proper Python package layout. This is the foundation for all other modules.

**Files**:
- `src/pystructmap/__init__.py` - Package initialization with __version__ = "0.1.0"
- Verify imports work: `from pystructmap import __version__`

**Acceptance Criteria**:
- [ ] Package can be imported: `import pystructmap`
- [ ] Version accessible: `pystructmap.__version__ == "0.1.0"`
- [ ] `uv sync` installs package successfully
- [ ] `uv run python -c "import pystructmap; print(pystructmap.__version__)"` outputs "0.1.0"
- [ ] Run `uv run python scripts/build.py --verbose` - should pass or show expected failures for missing code

**Dependencies**: None (starting point)

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4

---

---
id: "PSM-CRIT-002"
title: "Implement AST-based entity extraction"
description: "Create extract_entities() function to extract classes, functions, methods from AST"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build the core AST parsing functionality that walks Python abstract syntax trees and extracts structural elements (classes, functions, async functions) with metadata (line numbers, docstrings, methods, bases).

**Files**:
- `src/pystructmap/scanner.py` - Create extract_entities(tree: ast.AST) function
- `tests/test_scanner.py` - Unit tests for entity extraction

**Acceptance Criteria**:
- [ ] Function extracts ClassDef nodes with name, lineno, end_lineno, docstring, methods, bases
- [ ] Function extracts FunctionDef and AsyncFunctionDef nodes with name, lineno, end_lineno, docstring
- [ ] Handles nested classes and methods correctly
- [ ] Returns list[dict[str, Any]] with type, name, lineno, end_lineno, docstring
- [ ] Unit tests cover classes, functions, async functions, nested structures
- [ ] Tests use fixture Python files with known structure
- [ ] Run `uv run pytest tests/test_scanner.py -v` - all tests pass
- [ ] Coverage for scanner.py >= 70%

**Dependencies**: PSM-CRIT-001

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.1.2

---

---
id: "PSM-CRIT-003"
title: "Integrate radon metrics collection"
description: "Implement compute_metrics() using radon.complexity and radon.raw"
priority: critical
status: ⏸️ proposed
---

**Context**:
Integrate radon library to compute cyclomatic complexity and raw metrics (LOC, SLOC, comments, blanks) for Python source files. These metrics are essential for refactor prioritization.

**Files**:
- `src/pystructmap/scanner.py` - Add compute_metrics(source: str) function
- `tests/test_scanner.py` - Add tests for metrics computation

**Acceptance Criteria**:
- [ ] Function uses radon.complexity.cc_visit() to get complexity list
- [ ] Function uses radon.raw.analyze() to get raw metrics (loc, sloc, comments, blank)
- [ ] Returns tuple[list[dict], dict] (complexity list, raw dict)
- [ ] Complexity list includes function name, complexity, lineno
- [ ] Raw dict includes loc, sloc, comments, multi, blank
- [ ] Unit tests verify correct metric values for known Python code
- [ ] Handle syntax errors gracefully (return empty metrics, don't crash)
- [ ] Run `uv run pytest tests/test_scanner.py::test_compute_metrics -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-002

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.1.3

---

---
id: "PSM-CRIT-004"
title: "Implement git metadata extraction"
description: "Create extract_git_metadata() to get commit count, last author, last date"
priority: critical
status: ⏸️ proposed
---

**Context**:
Extract git history metadata for files using subprocess git commands. This provides insight into file churn and ownership, helping agents identify hotspots.

**Files**:
- `src/pystructmap/scanner.py` - Add extract_git_metadata(path: Path) function
- `tests/test_scanner.py` - Add tests for git metadata extraction

**Acceptance Criteria**:
- [ ] Function uses subprocess to run git commands: rev-list, log
- [ ] Extracts commit count via `git rev-list --count HEAD -- <path>`
- [ ] Extracts last author via `git log -1 --pretty=%an -- <path>`
- [ ] Extracts last commit date via `git log -1 --pretty=%ad --date=short -- <path>`
- [ ] Returns dict with commits (int), last_author (str), last_commit (str)
- [ ] Gracefully handles non-git directories (returns empty dict)
- [ ] Gracefully handles files not in git (returns empty dict)
- [ ] Unit tests mock subprocess calls for deterministic results
- [ ] Run `uv run pytest tests/test_scanner.py::test_extract_git_metadata -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-003

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.1.4

---

---
id: "PSM-CRIT-005"
title: "Create ASTScanner class with scan_file() method"
description: "Build main scanner class that orchestrates entity extraction and metrics"
priority: critical
status: ⏸️ proposed
---

**Context**:
Create the ASTScanner class that combines all parsing components (entity extraction, metrics, git metadata) to analyze a single Python file and return complete metadata dict.

**Files**:
- `src/pystructmap/scanner.py` - Create ASTScanner class
- `tests/test_scanner.py` - Add tests for ASTScanner.scan_file()

**Acceptance Criteria**:
- [ ] Class has __init__(root: Path) accepting root directory
- [ ] scan_file(path: Path) method analyzes single file
- [ ] Returns dict with: path, entities, complexity, raw, comment_ratio, git, maintainability_index, has_tests
- [ ] Calculates comment_ratio = comments / loc if loc > 0
- [ ] Uses radon.metrics.mi_visit() for maintainability index
- [ ] Checks for test file existence (path.replace("src/", "tests/test_"))
- [ ] Handles parsing errors gracefully (returns error field, doesn't crash)
- [ ] Unit tests verify complete output structure
- [ ] Run `uv run pytest tests/test_scanner.py::TestASTScanner -v` - passes
- [ ] Coverage for ASTScanner >= 90%

**Dependencies**: PSM-CRIT-004

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.1.1

---

---
id: "PSM-CRIT-006"
title: "Implement scan_directory() with basic file walking"
description: "Add directory scanning that recursively processes all *.py files"
priority: critical
status: ⏸️ proposed
---

**Context**:
Extend ASTScanner with scan_directory() method that walks the directory tree, finds all Python files, and processes them. This is the core of the scan command.

**Files**:
- `src/pystructmap/scanner.py` - Add scan_directory() method to ASTScanner
- `tests/test_scanner.py` - Add integration test for directory scanning

**Acceptance Criteria**:
- [ ] Method uses Path.rglob("*.py") to find Python files recursively
- [ ] Processes each file with scan_file()
- [ ] Builds dependencies dict (imports and imported_by)
- [ ] Builds symbol_index dict (name -> "file:lineno")
- [ ] Returns complete code_index dict with: scanned_root, scanned_at, version, total_files, files, dependencies, symbol_index
- [ ] Sets scanned_at to ISO 8601 timestamp
- [ ] Sets version to "0.1.0"
- [ ] Integration test with temporary directory and sample Python files
- [ ] Run `uv run pytest tests/test_scanner.py::test_scan_directory -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-005

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.1.1

---

---
id: "PSM-CRIT-007"
title: "Implement dependency extraction"
description: "Build dependency graph showing imports and imported_by relationships"
priority: critical
status: ⏸️ proposed
---

**Context**:
Parse import statements from Python files to build a dependency graph. This enables agents to understand coupling and find dependency hotspots.

**Files**:
- `src/pystructmap/scanner.py` - Add build_dependency_graph() function
- `tests/test_scanner.py` - Add tests for dependency extraction

**Acceptance Criteria**:
- [ ] Function parses source code line by line
- [ ] Detects `import module` and `from module import ...` statements
- [ ] Extracts module names from imports
- [ ] Returns dict mapping file -> list of imported modules
- [ ] Handles relative imports (from . import, from .. import)
- [ ] Handles multi-line imports (parenthesized imports)
- [ ] Unit tests verify correct import extraction
- [ ] Run `uv run pytest tests/test_scanner.py::test_build_dependency_graph -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-006

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 3.2

---

---
id: "PSM-CRIT-008"
title: "Create basic scan CLI command with Typer"
description: "Implement uv run pystructmap scan with output to code_index.json"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build the CLI interface using Typer to expose scanner functionality. This is the primary way agents trigger scans.

**Files**:
- `src/pystructmap/cli.py` - Create Typer app with scan command
- `tests/test_cli.py` - Add CLI tests using typer.testing.CliRunner

**Acceptance Criteria**:
- [ ] Create Typer app: `app = typer.Typer()`
- [ ] Implement scan(root: Path, output: Path) command
- [ ] Default root=".", output="code_index.json"
- [ ] Command creates ASTScanner and calls scan_directory()
- [ ] Writes JSON output to specified path
- [ ] Prints success message with output path
- [ ] CLI tests use CliRunner to invoke command
- [ ] Test verifies JSON file is created with correct structure
- [ ] Run `uv run pystructmap scan .` from project root - creates code_index.json
- [ ] Run `uv run pytest tests/test_cli.py -v` - passes
- [ ] Coverage for cli.py >= 70%

**Dependencies**: PSM-CRIT-007

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 9.1

---

---
id: "PSM-CRIT-009"
title: "Create unit tests for scanner module"
description: "Comprehensive test coverage for all scanner components"
priority: critical
status: ⏸️ proposed
---

**Context**:
Ensure scanner module has robust test coverage with unit tests for all functions and edge cases. This validates correctness and prevents regressions.

**Files**:
- `tests/test_scanner.py` - Complete test suite
- `tests/fixtures/sample_code.py` - Fixture Python files for testing

**Acceptance Criteria**:
- [ ] Tests for extract_entities() covering classes, functions, async, nested, docstrings
- [ ] Tests for compute_metrics() verifying complexity and LOC calculations
- [ ] Tests for extract_git_metadata() mocking subprocess calls
- [ ] Tests for ASTScanner.scan_file() with complete file analysis
- [ ] Tests for scan_directory() with temporary directory fixtures
- [ ] Tests for build_dependency_graph() with various import patterns
- [ ] Edge case tests: syntax errors, empty files, no docstrings, no git
- [ ] All tests complete within 5 seconds (pytest-timeout)
- [ ] Run `uv run pytest tests/test_scanner.py -v --cov=src/pystructmap/scanner` - coverage >= 90%
- [ ] Run `uv run python scripts/build.py` - all checks pass

**Dependencies**: PSM-CRIT-008

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 10.1

---

---
id: "PSM-CRIT-010"
title: "Validate build pipeline and fix any issues"
description: "Run build.py and ensure all quality checks pass for scanner module"
priority: critical
status: ⏸️ proposed
---

**Context**:
Execute full build pipeline to validate code quality, type checking, linting, and test coverage for the scanner module before proceeding to query system.

**Files**:
- Run `scripts/build.py`
- Fix any issues found

**Acceptance Criteria**:
- [ ] `uv sync` completes successfully
- [ ] `uv run ruff format src/pystructmap/` - no changes needed
- [ ] `uv run ruff check src/pystructmap/` - no errors
- [ ] `uv run mypy src/pystructmap/` - no type errors
- [ ] `uv run pytest tests/` - all tests pass
- [ ] Test coverage >= 70% overall
- [ ] Scanner module coverage >= 90%
- [ ] All tests complete within 5 seconds
- [ ] Run `uv run python scripts/build.py --verbose` - BUILD SUCCESSFUL
- [ ] Commit changes: "feat: implement core scanner with AST parsing and metrics"

**Dependencies**: PSM-CRIT-009

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 2.5

---

## Group 2: Query System (Tasks 11-20)

---
id: "PSM-CRIT-011"
title: "Create CodeIndex class with JSON loading"
description: "Implement CodeIndex that loads code_index.json and provides base API"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build the query system foundation by creating CodeIndex class that loads the JSON index and exposes it for querying. This is the primary interface agents use.

**Files**:
- `src/pystructmap/query.py` - Create CodeIndex class
- `tests/test_query.py` - Unit tests for CodeIndex

**Acceptance Criteria**:
- [ ] Class has __init__(index_file: str | Path) accepting path to code_index.json
- [ ] Loads JSON using json.loads(Path(index_file).read_text())
- [ ] Stores data in self.data dict
- [ ] Raises FileNotFoundError if index file doesn't exist
- [ ] Raises json.JSONDecodeError if file is invalid JSON
- [ ] Property method total_files returns len(self.data["files"])
- [ ] Unit tests verify loading and error handling
- [ ] Run `uv run pytest tests/test_query.py::TestCodeIndex -v` - passes
- [ ] Coverage for query.py >= 70%

**Dependencies**: PSM-CRIT-010

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.2.1

---

---
id: "PSM-CRIT-012"
title: "Build in-memory entity_map index"
description: "Create O(1) lookup dict mapping entity names to file locations"
priority: critical
status: ⏸️ proposed
---

**Context**:
Optimize queries by building an in-memory index that maps entity names (classes, functions) to their file locations. This enables instant O(1) lookups.

**Files**:
- `src/pystructmap/query.py` - Add _build_indices() method to CodeIndex
- `tests/test_query.py` - Add tests for entity_map

**Acceptance Criteria**:
- [ ] Method iterates over all files in self.data["files"]
- [ ] For each entity in file["entities"], adds to self.entity_map
- [ ] Key is entity["name"], value is {"file": file["path"], "meta": entity}
- [ ] Called automatically in __init__ after loading JSON
- [ ] entity_map is dict[str, dict[str, Any]]
- [ ] Handle duplicate names (later entries override earlier ones with warning)
- [ ] Unit tests verify correct mapping for known fixtures
- [ ] Run `uv run pytest tests/test_query.py::test_entity_map -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-011

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.2.1

---

---
id: "PSM-CRIT-013"
title: "Build in-memory complexity_map index"
description: "Create O(1) lookup dict for function complexity values"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build second index mapping "file::function" keys to complexity values for instant complexity lookups. Enables fast filtering of complex functions.

**Files**:
- `src/pystructmap/query.py` - Extend _build_indices() in CodeIndex
- `tests/test_query.py` - Add tests for complexity_map

**Acceptance Criteria**:
- [ ] Method iterates over file["complexity"] for each file
- [ ] For each complexity entry, adds to self.complexity_map
- [ ] Key is f"{file['path']}::{comp['name']}"
- [ ] Value is comp["complexity"] (int)
- [ ] complexity_map is dict[str, int]
- [ ] Called in _build_indices() along with entity_map
- [ ] Unit tests verify correct mapping and values
- [ ] Run `uv run pytest tests/test_query.py::test_complexity_map -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-012

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.2.1

---

---
id: "PSM-CRIT-014"
title: "Implement find() method for entity lookup"
description: "Add find(name) method for O(1) entity location lookup"
priority: critical
status: ⏸️ proposed
---

**Context**:
Implement the primary query method that agents use to locate classes and functions instantly. This is the most frequently used query operation.

**Files**:
- `src/pystructmap/query.py` - Add find() method to CodeIndex
- `tests/test_query.py` - Add tests for find()

**Acceptance Criteria**:
- [ ] Method signature: find(self, name: str) -> dict[str, Any] | None
- [ ] Returns self.entity_map.get(name) - O(1) dict lookup
- [ ] Returns None if entity not found
- [ ] Return value includes "file" and "meta" keys
- [ ] "meta" contains type, name, lineno, end_lineno, docstring
- [ ] Unit tests verify correct results for known entities
- [ ] Unit tests verify None for non-existent entities
- [ ] Run `uv run pytest tests/test_query.py::test_find -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-013

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 6.1

---

---
id: "PSM-CRIT-015"
title: "Implement complex() method for complexity filtering"
description: "Add complex(threshold) method to find high-complexity functions"
priority: critical
status: ⏸️ proposed
---

**Context**:
Enable agents to find refactor candidates by filtering functions above a complexity threshold. Critical for prioritizing technical debt.

**Files**:
- `src/pystructmap/query.py` - Add complex() method to CodeIndex
- `tests/test_query.py` - Add tests for complex()

**Acceptance Criteria**:
- [ ] Method signature: complex(self, threshold: int = 10) -> list[dict[str, Any]]
- [ ] Iterates over self.complexity_map items
- [ ] Filters where complexity >= threshold
- [ ] Returns list of dicts with file, function, complexity keys
- [ ] Extracts file and function from "file::function" key
- [ ] Default threshold is 10 (radon's recommendation)
- [ ] Unit tests verify correct filtering for various thresholds
- [ ] Run `uv run pytest tests/test_query.py::test_complex -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-014

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 6.1

---

---
id: "PSM-CRIT-016"
title: "Implement dependencies() method for import lookup"
description: "Add dependencies(file) method to get imports for a file"
priority: critical
status: ⏸️ proposed
---

**Context**:
Allow agents to analyze coupling by looking up a file's import dependencies. Useful for understanding module relationships.

**Files**:
- `src/pystructmap/query.py` - Add dependencies() method to CodeIndex
- `tests/test_query.py` - Add tests for dependencies()

**Acceptance Criteria**:
- [ ] Method signature: dependencies(self, file: str) -> list[str]
- [ ] Returns self.data["dependencies"].get(file, [])
- [ ] Returns empty list if file not found
- [ ] Returns list of module names imported by file
- [ ] Unit tests verify correct results for known files
- [ ] Unit tests verify empty list for files with no imports
- [ ] Run `uv run pytest tests/test_query.py::test_dependencies -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-015

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 6.1

---

---
id: "PSM-CRIT-017"
title: "Implement top_complex() method for ranking"
description: "Add top_complex(n) method to get most complex functions"
priority: critical
status: ⏸️ proposed
---

**Context**:
Provide agents with a quick way to find the top N most complex functions in the codebase for prioritized refactoring.

**Files**:
- `src/pystructmap/query.py` - Add top_complex() method to CodeIndex
- `tests/test_query.py` - Add tests for top_complex()

**Acceptance Criteria**:
- [ ] Method signature: top_complex(self, n: int = 10) -> list[tuple[str, int]]
- [ ] Sorts self.complexity_map.items() by value (complexity) descending
- [ ] Returns top n results as list of (key, complexity) tuples
- [ ] Key format is "file::function"
- [ ] Default n is 10
- [ ] Handles n > total functions (returns all available)
- [ ] Unit tests verify correct sorting and limit
- [ ] Run `uv run pytest tests/test_query.py::test_top_complex -v` - passes
- [ ] Coverage for query.py >= 90%

**Dependencies**: PSM-CRIT-016

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 6.1

---

---
id: "PSM-CRIT-018"
title: "Create unit tests for CodeIndex query methods"
description: "Comprehensive test coverage for all query operations"
priority: critical
status: ⏸️ proposed
---

**Context**:
Ensure query module has robust test coverage with tests for all methods, edge cases, and performance characteristics.

**Files**:
- `tests/test_query.py` - Complete test suite for CodeIndex
- `tests/fixtures/test_code_index.json` - Fixture JSON for testing

**Acceptance Criteria**:
- [ ] Tests for CodeIndex initialization and JSON loading
- [ ] Tests for error handling (missing file, invalid JSON)
- [ ] Tests for _build_indices() with entity_map and complexity_map
- [ ] Tests for find() with existing and non-existing entities
- [ ] Tests for complex() with various thresholds
- [ ] Tests for dependencies() with files having/not having imports
- [ ] Tests for top_complex() with various n values
- [ ] Performance tests verifying O(1) lookups (use pytest-benchmark if needed)
- [ ] All tests use fixture JSON data for consistency
- [ ] Run `uv run pytest tests/test_query.py -v --cov=src/pystructmap/query` - coverage >= 90%
- [ ] All tests complete within 5 seconds

**Dependencies**: PSM-CRIT-017

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 10.1

---

---
id: "PSM-CRIT-019"
title: "Validate integration between scanner and query"
description: "End-to-end test: scan directory, load index, query results"
priority: critical
status: ⏸️ proposed
---

**Context**:
Verify the full pipeline works: scan produces valid JSON, CodeIndex loads it correctly, queries return expected results.

**Files**:
- `tests/test_integration.py` - Integration tests
- `tests/fixtures/sample_project/` - Sample Python project for testing

**Acceptance Criteria**:
- [ ] Create temporary directory with sample Python files (classes, functions, complexity)
- [ ] Run ASTScanner.scan_directory() on temp directory
- [ ] Verify code_index.json is created with expected structure
- [ ] Load JSON with CodeIndex
- [ ] Verify all expected entities are findable via find()
- [ ] Verify complex functions are found via complex()
- [ ] Verify dependencies are correct via dependencies()
- [ ] Clean up temporary files after test
- [ ] Run `uv run pytest tests/test_integration.py -v` - passes
- [ ] Coverage remains >= 70% overall

**Dependencies**: PSM-CRIT-018

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 10.2

---

---
id: "PSM-CRIT-020"
title: "Validate build pipeline for scanner and query modules"
description: "Run build.py and ensure all quality checks pass before rules engine"
priority: critical
status: ⏸️ proposed
---

**Context**:
Execute full build pipeline to validate scanner + query modules are production-ready before implementing rules engine.

**Files**:
- Run `scripts/build.py`
- Fix any issues found

**Acceptance Criteria**:
- [ ] `uv sync` completes successfully
- [ ] `uv run ruff format src/pystructmap/` - no changes needed
- [ ] `uv run ruff check src/pystructmap/` - no errors
- [ ] `uv run mypy src/pystructmap/` - no type errors
- [ ] `uv run pytest tests/` - all tests pass
- [ ] Test coverage >= 70% overall
- [ ] Scanner module coverage >= 90%
- [ ] Query module coverage >= 90%
- [ ] All tests complete within 5 seconds
- [ ] Run `uv run python scripts/build.py --verbose` - BUILD SUCCESSFUL
- [ ] Commit changes: "feat: implement CodeIndex query system with O(1) lookups"

**Dependencies**: PSM-CRIT-019

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 2.5

---

## Group 3: Rules Engine & Scoring (Tasks 21-30)

---
id: "PSM-CRIT-021"
title: "Create RuleEngine class with YAML loading"
description: "Implement RuleEngine that loads rules.yaml and parses metrics/actions"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build rules engine that loads dynamic YAML-based rules defining code quality thresholds and evaluation conditions.

**Files**:
- `src/pystructmap/rules.py` - Create RuleEngine class
- `tests/test_rules.py` - Unit tests for RuleEngine
- `rules.yaml.example` - Example rules file

**Acceptance Criteria**:
- [ ] Class has __init__(rules_file: str | Path) accepting path to rules.yaml
- [ ] Loads YAML using yaml.safe_load(Path(rules_file).read_text())
- [ ] Stores metrics dict in self.metrics
- [ ] Stores actions list in self.actions
- [ ] Handles missing rules file gracefully (use empty dicts)
- [ ] Unit tests verify correct loading of metrics and actions
- [ ] Create rules.yaml.example with sample metrics and actions
- [ ] Run `uv run pytest tests/test_rules.py::TestRuleEngine -v` - passes
- [ ] Coverage for rules.py >= 70%

**Dependencies**: PSM-CRIT-020

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.3.1

---

---
id: "PSM-CRIT-022"
title: "Implement evaluate() method for rule checking"
description: "Add evaluate(file_info) to check metrics against rule conditions"
priority: critical
status: ⏸️ proposed
---

**Context**:
Core rule evaluation logic that checks file metrics against defined conditions and returns violations with recommended actions.

**Files**:
- `src/pystructmap/rules.py` - Add evaluate() method to RuleEngine
- `tests/test_rules.py` - Add tests for evaluate()

**Acceptance Criteria**:
- [ ] Method signature: evaluate(self, file_info: dict) -> list[dict[str, Any]]
- [ ] Iterates over self.actions rules
- [ ] For each entity in file_info["entities"], evaluates rule condition
- [ ] Builds context dict with entity, raw metrics, complexity, metrics thresholds
- [ ] Uses eval(condition, {}, context) for condition evaluation
- [ ] Catches exceptions during eval (invalid conditions don't crash)
- [ ] Returns list of violation dicts with rule, desc, target, file, action
- [ ] Unit tests verify correct evaluation for various conditions
- [ ] Unit tests test edge cases (missing data, syntax errors in conditions)
- [ ] Run `uv run pytest tests/test_rules.py::test_evaluate -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-021

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.3.1

---

---
id: "PSM-CRIT-023"
title: "Create ScoringEngine class with weighted scoring"
description: "Implement ScoringEngine that computes refactor priority scores"
priority: critical
status: ⏸️ proposed
---

**Context**:
Build scoring system that ranks files by refactor priority using weighted combination of complexity, size, and coupling metrics.

**Files**:
- `src/pystructmap/scoring.py` - Create ScoringEngine class
- `tests/test_scoring.py` - Unit tests for ScoringEngine

**Acceptance Criteria**:
- [ ] Class has __init__(rules_file: str | Path) loading rules.yaml
- [ ] Loads weights from rules["weights"] if present
- [ ] Default weights: complexity=0.5, size=0.3, coupling=0.2
- [ ] Method score_file(file_info, deps) computes weighted score
- [ ] Extracts average complexity, LOC, coupling (import count)
- [ ] Normalizes metrics to 0-1 using _scale() helper
- [ ] Computes weighted sum: score = Σ(weight[k] * normalized[k])
- [ ] Returns dict with file, complexity, loc, coupling, score
- [ ] Unit tests verify correct score calculation
- [ ] Run `uv run pytest tests/test_scoring.py::TestScoringEngine -v` - passes
- [ ] Coverage for scoring.py >= 70%

**Dependencies**: PSM-CRIT-022

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.4.1

---

---
id: "PSM-CRIT-024"
title: "Implement rank() method for refactor prioritization"
description: "Add rank(index) to sort all files by refactor priority score"
priority: critical
status: ⏸️ proposed
---

**Context**:
Provide agents with prioritized list of files needing refactoring by scoring and ranking all files in the codebase.

**Files**:
- `src/pystructmap/scoring.py` - Add rank() method to ScoringEngine
- `tests/test_scoring.py` - Add tests for rank()

**Acceptance Criteria**:
- [ ] Method signature: rank(self, index: dict) -> list[dict[str, Any]]
- [ ] Extracts dependencies from index["dependencies"]
- [ ] Calls score_file() for each file in index["files"]
- [ ] Sorts results by score descending (highest score = highest priority)
- [ ] Returns sorted list of score dicts
- [ ] Unit tests verify correct ranking order
- [ ] Unit tests verify score values are deterministic
- [ ] Run `uv run pytest tests/test_scoring.py::test_rank -v` - passes
- [ ] Coverage for scoring.py >= 90%

**Dependencies**: PSM-CRIT-023

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.4.1

---

---
id: "PSM-CRIT-025"
title: "Add rank CLI command"
description: "Implement uv run pystructmap rank to generate refactor_rank.json"
priority: critical
status: ⏸️ proposed
---

**Context**:
Expose scoring functionality via CLI so agents can generate refactor priority rankings.

**Files**:
- `src/pystructmap/cli.py` - Add rank command to Typer app
- `tests/test_cli.py` - Add tests for rank command

**Acceptance Criteria**:
- [ ] Add rank(rules: Path, top: int) command
- [ ] Default rules="rules.yaml", top=20
- [ ] Loads code_index.json with CodeIndex
- [ ] Creates ScoringEngine with rules file
- [ ] Calls se.rank(ci.data) to get rankings
- [ ] Writes top N results to refactor_rank.json
- [ ] Prints each result: file, score, complexity, loc
- [ ] CLI tests verify JSON output is correct
- [ ] Run `uv run pystructmap rank --top 10` - creates refactor_rank.json
- [ ] Run `uv run pytest tests/test_cli.py::test_rank -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-024

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 9.3

---

---
id: "PSM-CRIT-026"
title: "Add check CLI command for rule violations"
description: "Implement uv run pystructmap check to generate violations.json"
priority: critical
status: ⏸️ proposed
---

**Context**:
Expose rules engine via CLI so agents can check for code quality violations.

**Files**:
- `src/pystructmap/cli.py` - Add check command to Typer app
- `tests/test_cli.py` - Add tests for check command

**Acceptance Criteria**:
- [ ] Add check(rules: Path, threshold: int) command
- [ ] Default rules="rules.yaml", threshold=0
- [ ] Loads code_index.json with CodeIndex
- [ ] Creates RuleEngine with rules file
- [ ] Evaluates each file: flagged += re.evaluate(f)
- [ ] Writes all violations to violations.json
- [ ] Prints count of violations found
- [ ] CLI tests verify JSON output contains violations
- [ ] Run `uv run pystructmap check` - creates violations.json
- [ ] Run `uv run pytest tests/test_cli.py::test_check -v` - passes
- [ ] Coverage remains >= 70%

**Dependencies**: PSM-CRIT-025

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 9.4

---

---
id: "PSM-CRIT-027"
title: "Create AgentAdapter class with convenience methods"
description: "Build high-level API that combines CodeIndex, RuleEngine, ScoringEngine"
priority: critical
status: ⏸️ proposed
---

**Context**:
Provide agents with a unified, convenient interface that wraps all query, rules, and scoring functionality.

**Files**:
- `src/pystructmap/agent_adapter.py` - Create AgentAdapter class
- `tests/test_agent_adapter.py` - Unit tests for AgentAdapter

**Acceptance Criteria**:
- [ ] Class has __init__(root: Path) accepting workspace root
- [ ] Initializes CodeIndex, RuleEngine, ScoringEngine in __init__
- [ ] Implements get_symbol_location(symbol) -> returns ci.find(symbol)
- [ ] Implements get_top_refactors(limit) -> loads refactor_rank.json[:limit]
- [ ] Implements get_rule_violations() -> loads violations.json
- [ ] Implements get_complex_functions(threshold) -> returns ci.complex(threshold)
- [ ] Implements get_dependency_hotspots(min_edges) -> filters high-coupling files
- [ ] Implements get_untyped_or_poor_docs() -> finds low coverage files
- [ ] Implements summarize_state() -> returns compact summary dict
- [ ] Unit tests verify all methods work correctly
- [ ] Run `uv run pytest tests/test_agent_adapter.py -v` - passes
- [ ] Coverage for agent_adapter.py >= 90%

**Dependencies**: PSM-CRIT-026

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 4.5.1

---

---
id: "PSM-CRIT-028"
title: "Add agent CLI command for query interface"
description: "Implement uv run pystructmap agent with various query options"
priority: critical
status: ⏸️ proposed
---

**Context**:
Provide CLI interface for agents to query the codebase via subprocess calls, outputting structured JSON.

**Files**:
- `src/pystructmap/cli.py` - Add agent command to Typer app
- `tests/test_cli.py` - Add tests for agent command

**Acceptance Criteria**:
- [ ] Add agent(summary, symbol, top, complex_threshold, untyped) command
- [ ] If summary=True: output adapter.summarize_state()
- [ ] If symbol provided: output adapter.get_symbol_location(symbol)
- [ ] If untyped=True: output adapter.get_untyped_or_poor_docs()
- [ ] Else: output dict with top_refactors, complex_functions, dependency_hotspots, rule_violations
- [ ] All output is JSON (json.dumps with indent=2)
- [ ] CLI tests verify correct JSON structure for each option
- [ ] Run `uv run pystructmap agent --summary` - outputs JSON
- [ ] Run `uv run pystructmap agent --symbol ApiClient` - outputs location
- [ ] Run `uv run pytest tests/test_cli.py::test_agent -v` - passes
- [ ] Coverage for cli.py >= 90%

**Dependencies**: PSM-CRIT-027

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 9.5

---

---
id: "PSM-CRIT-029"
title: "Create comprehensive unit tests for rules and scoring"
description: "Complete test coverage for RuleEngine, ScoringEngine, AgentAdapter"
priority: critical
status: ⏸️ proposed
---

**Context**:
Ensure rules, scoring, and adapter modules have robust test coverage with tests for all functionality and edge cases.

**Files**:
- `tests/test_rules.py` - Complete test suite for RuleEngine
- `tests/test_scoring.py` - Complete test suite for ScoringEngine
- `tests/test_agent_adapter.py` - Complete test suite for AgentAdapter

**Acceptance Criteria**:
- [ ] RuleEngine tests: YAML loading, evaluate() with various conditions, error handling
- [ ] ScoringEngine tests: score calculation, normalization, ranking, custom weights
- [ ] AgentAdapter tests: all convenience methods, JSON loading, integration with other components
- [ ] Edge case tests: missing files, invalid YAML, division by zero in scoring
- [ ] All tests use fixture data for consistency
- [ ] Run `uv run pytest tests/test_rules.py tests/test_scoring.py tests/test_agent_adapter.py -v` - all pass
- [ ] Coverage for rules.py >= 90%
- [ ] Coverage for scoring.py >= 90%
- [ ] Coverage for agent_adapter.py >= 90%
- [ ] All tests complete within 5 seconds

**Dependencies**: PSM-CRIT-028

**References**: `.work/agent/issues/references/pystructmap-specification.md` Section 10.1

---

---
id: "PSM-CRIT-030"
title: "Final build validation and documentation check"
description: "Run complete build pipeline and verify all critical functionality"
priority: critical
status: ⏸️ proposed
---

**Context**:
Final validation of all critical components before moving to high priority tasks (incremental caching, watch mode, static analysis integration).

**Files**:
- Run `scripts/build.py`
- Update `README.md` if needed
- Fix any issues found

**Acceptance Criteria**:
- [ ] `uv sync` completes successfully
- [ ] `uv run ruff format src/pystructmap/` - no changes needed
- [ ] `uv run ruff check src/pystructmap/` - no errors
- [ ] `uv run mypy src/pystructmap/` - no type errors
- [ ] `uv run ruff check --select S src/pystructmap/` - security checks pass
- [ ] `uv run pytest tests/` - all tests pass
- [ ] Test coverage >= 70% overall (aim for 75-80%)
- [ ] All module coverage >= 90% (scanner, query, rules, scoring, agent_adapter, cli)
- [ ] All tests complete within 5 seconds
- [ ] README.md has accurate quick start guide
- [ ] README.md examples work correctly
- [ ] Run `uv run python scripts/build.py --verbose` - BUILD SUCCESSFUL
- [ ] Manual verification: scan sample project, query results, check rules, rank files
- [ ] Commit changes: "feat: implement rules engine, scoring system, and agent adapter"
- [ ] Tag release: v0.1.0-critical-complete

**Dependencies**: PSM-CRIT-029

**References**: `.work/agent/issues/references/pystructmap-specification.md` Sections 2.5, 13

---

## Summary

- **Group 1 (Tasks 1-10)**: Core Scanner Infrastructure - AST parsing, entity extraction, metrics collection, git metadata, basic CLI
- **Group 2 (Tasks 11-20)**: Query System - CodeIndex with O(1) lookups, find/complex/dependencies methods, integration testing
- **Group 3 (Tasks 21-30)**: Rules Engine & Scoring - Dynamic YAML rules, evaluation engine, weighted scoring, agent adapter, CLI commands

**Next Steps**: After completing all critical tasks (PSM-CRIT-030), proceed to high priority tasks for incremental caching, watch mode, deep analysis features, and static analysis integration.
