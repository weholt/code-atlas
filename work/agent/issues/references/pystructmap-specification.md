# PyStructMap - Technical Specification

## Version: 0.1.0

## Document Status: DRAFT

## Last Updated: 2025-11-10

---

## 1. Project Overview

### 1.1 Purpose

PyStructMap is an agent-oriented Python codebase structure and metrics analyzer designed specifically for autonomous coding systems. It provides fast, deterministic codebase navigation and analysis capabilities through AST parsing, complexity metrics, and in-memory query APIs.

### 1.2 Problem Statement

Autonomous coding agents need:
- **Fast navigation** - Locate classes, functions, and their definitions instantly
- **Deterministic metrics** - Reproducible complexity, LOC, and quality measurements
- **Structural insight** - Understanding of dependencies, call graphs, and coupling
- **Refactor guidance** - Evidence-based prioritization of technical debt
- **Zero latency** - Local-only operation without HTTP overhead

Traditional code navigation tools either:
- Require heavy IDEs or language servers (too slow for agents)
- Lack machine-readable output formats
- Don't provide comprehensive metrics in one place
- Use HTTP APIs (unnecessary serialization overhead)

### 1.3 Solution

PyStructMap solves this by:

1. **AST-Based Parsing** - Accurate extraction using Python's ast module
2. **Radon Metrics Integration** - Complexity, maintainability, LOC measurements
3. **JSON Intermediate Format** - Portable, parseable, agent-friendly persistence
4. **In-Memory Query API** - O(1) lookups via dict-based indices
5. **Dynamic YAML Rules** - Configurable thresholds without code changes
6. **Incremental Caching** - Skip unchanged files for sub-second updates
7. **Watch Mode** - Continuous monitoring for always-current data
8. **Static Tool Integration** - Leverage ruff, mypy, bandit for comprehensive analysis

### 1.4 Key Features

- AST-based parsing with line numbers and docstrings
- Cyclomatic complexity via radon
- Maintainability index calculation
- Git metadata (commits, authors, dates)
- Type annotation coverage tracking
- Call graph mapping
- Dependency analysis
- O(1) lookup queries
- Dynamic rules engine
- Scoring and ranking system
- Incremental caching
- Watch mode for continuous updates
- CLI agent interface
- Static analysis tool integration
- Automated issue generation

---

## 2. Technical Requirements

### 2.1 Python Version

- **Minimum**: Python >=3.11
- **Rationale**: Modern type hints, match statements, improved performance

### 2.2 Core Dependencies

```toml
dependencies = [
    "typer>=0.9.0",      # CLI framework with type hints
    "radon>=6.0.0",      # Complexity and metrics
    "pyyaml>=6.0",       # Rules configuration
]
```

### 2.3 Optional Dependencies

```toml
[project.optional-dependencies]
visual = [
    "rich>=13.7.0",      # Human-readable console output
    "networkx>=3.2",     # Graph analysis
    "pyvis>=0.3.2",      # HTML visualizations
]
```

### 2.4 Development Dependencies

```toml
dev = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "pytest-timeout>=2.2.0",
    "pytest-asyncio>=0.21.1",
    "ruff>=0.1.9",
    "mypy>=1.7.1",
    "types-pyyaml>=6.0.12",
]
```

### 2.5 Quality Standards

- **Test Coverage**: >=70% enforced via pytest-cov --cov-fail-under=70
- **Test Timeout**: 5 seconds per test via pytest-timeout
- **Linting**: Ruff with security checks (--select S)
- **Type Checking**: MyPy strict mode enabled
- **Line Length**: 120 characters

### 2.6 Build System

- **Package Manager**: uv (Astral's unified Python tool)
- **Build Backend**: hatchling

---

## 3. Architecture

### 3.1 System Architecture Diagram

```
┌─────────────┐
│  Codebase   │ Python source files
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│   Scanner (CLI)      │ ast + radon + git
│   src/pystructmap/   │ - analyze_file()
│   scanner.py         │ - extract entities
└──────┬───────────────┘ - compute metrics
       │                 - git metadata
       │                 - call graphs
       ▼ (writes)
┌──────────────────────┐
│  code_index.json     │ Persistent storage
│  - files[]           │ - Portable format
│  - dependencies{}    │ - Agent-friendly
│  - symbol_index{}    │ - Versioned schema
└──────┬───────────────┘
       │
       ▼ (loads once)
┌──────────────────────┐
│   CodeIndex          │ In-memory indices
│   src/pystructmap/   │ - entity_map: O(1)
│   query.py           │ - complexity_map
└──────┬───────────────┘ - Lazy loading
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐    ┌──────────────┐
│ RuleEngine   │    │ ScoringEngine│
│ rules.py     │    │ scoring.py   │
│ - YAML rules │    │ - Weighted   │
│ - evaluate() │    │ - rank()     │
└──────┬───────┘    └──────┬───────┘
       │                    │
       └────────┬───────────┘
                ▼
┌──────────────────────────┐
│   AgentAdapter           │ Convenience layer
│   agent_adapter.py       │ - High-level queries
│   - get_symbol_location()│ - Summarization
│   - get_top_refactors()  │
└──────┬───────────────────┘
       │
       ▼ (imports or subprocess)
┌──────────────┐
│    Agent     │ Autonomous coder
└──────────────┘

Parallel workflows:
┌────────────────┐
│ Watch Mode     │ watchdog → auto-scan
│ watch.py       │ Keeps JSON current
└────────────────┘

┌────────────────┐
│ Static Tools   │ ruff, mypy, bandit
│ collect.py     │ → agent_report.json
└────────────────┘ → issue files
```

### 3.2 Data Flow

1. **Scan Phase**
   - Scanner walks Python files (*.py)
   - For each file: AST parse, extract entities, compute metrics
   - Optionally: incremental (skip unchanged via hash), deep (call graphs + type coverage)
   - Write code_index.json with all metadata

2. **Query Phase**
   - Agent imports CodeIndex or uses CLI
   - CodeIndex loads JSON once, builds in-memory maps
   - Queries return results in <1µs (O(1) dict lookups)

3. **Analysis Phase**
   - RuleEngine loads rules.yaml
   - Evaluates metrics against thresholds
   - Returns violations (violations.json)
   - ScoringEngine ranks files by weighted score (refactor_rank.json)

4. **Continuous Phase** (optional)
   - Watch mode monitors file changes
   - Triggers incremental rescans
   - Updates JSON atomically

### 3.3 Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| Scanner | Extract structure and metrics | Python files | code_index.json |
| CodeIndex | Fast in-memory queries | code_index.json | Query results |
| RuleEngine | Evaluate rule violations | code_index.json + rules.yaml | violations.json |
| ScoringEngine | Rank refactor targets | code_index.json + rules.yaml | refactor_rank.json |
| AgentAdapter | High-level agent API | CodeIndex + RuleEngine | Structured responses |
| WatchHandler | Continuous monitoring | File system events | Triggers scan |
| CollectOrchestrator | Static analysis aggregation | ruff, mypy, bandit output | Issue files |

---

## 4. Core Components

### 4.1 Scanner Module (src/pystructmap/scanner.py)

#### 4.1.1 ASTScanner Class

**Purpose**: Parse Python files and extract structural elements using AST.

**Class Signature**:
```python
class ASTScanner:
    def __init__(self, root: Path):
        self.root = root
    
    def scan_file(self, path: Path) -> dict[str, Any]:
        """Analyze single Python file."""
        pass
    
    def scan_directory(self, incremental: bool = False, deep: bool = False) -> dict[str, Any]:
        """Scan all Python files in directory."""
        pass
```

**Methods**:

- `scan_file(path)`: Analyzes a single Python file
  - Parses AST using ast.parse()
  - Extracts classes, functions, async functions
  - Records line numbers (lineno, end_lineno)
  - Extracts docstrings via ast.get_docstring()
  - Returns dict with entities, complexity, raw metrics

- `scan_directory(incremental, deep)`: Scans all *.py files recursively
  - Walks directory tree using Path.rglob("*.py")
  - Skips unchanged files if incremental=True (uses cache)
  - Includes deep analysis if deep=True (call graphs, type coverage)
  - Returns complete code_index dict

#### 4.1.2 EntityExtractor

**Purpose**: Extract classes, functions, methods from AST with metadata.

**Function Signature**:
```python
def extract_entities(tree: ast.AST) -> list[dict[str, Any]]:
    """Extract all classes and functions from AST."""
    entities = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            entity = {
                "type": node.__class__.__name__,
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", None),
                "docstring": ast.get_docstring(node),
            }
            if isinstance(node, ast.ClassDef):
                entity["methods"] = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                entity["bases"] = [b.id for b in node.bases if isinstance(b, ast.Name)]
            entities.append(entity)
    return entities
```

**Output Example**:
```json
[
  {
    "type": "ClassDef",
    "name": "ApiClient",
    "lineno": 15,
    "end_lineno": 120,
    "docstring": "HTTP client for API communication",
    "methods": ["__init__", "request", "get", "post"],
    "bases": ["BaseClient"]
  },
  {
    "type": "FunctionDef",
    "name": "parse_response",
    "lineno": 125,
    "end_lineno": 140,
    "docstring": "Parse JSON response"
  }
]
```

#### 4.1.3 MetricsCollector

**Purpose**: Compute complexity and LOC metrics using radon.

**Function Signature**:
```python
def compute_metrics(source: str) -> tuple[list[dict], dict]:
    """Compute complexity and raw metrics."""
    from radon.complexity import cc_visit
    from radon.raw import analyze
    
    complexity = [r.as_dict() for r in cc_visit(source)]
    raw = analyze(source)._asdict()
    
    return complexity, raw
```

**Metrics Collected**:
- **Cyclomatic Complexity**: Per function/method
- **LOC**: Lines of code
- **SLOC**: Source lines (non-blank, non-comment)
- **Comments**: Comment line count
- **Blank**: Blank line count

#### 4.1.4 GitMetadataExtractor

**Purpose**: Extract git history metadata for files.

**Function Signature**:
```python
def extract_git_metadata(path: Path) -> dict[str, Any]:
    """Extract commit count, last author, last date."""
    import subprocess
    
    try:
        count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD", "--", str(path)],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        author = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%an", "--", str(path)],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        date = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%ad", "--date=short", "--", str(path)],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            "commits": int(count or 0),
            "last_author": author,
            "last_commit": date
        }
    except Exception:
        return {}
```

### 4.2 Query Module (src/pystructmap/query.py)

#### 4.2.1 CodeIndex Class

**Purpose**: Provide fast in-memory queries over code_index.json.

**Class Signature**:
```python
class CodeIndex:
    def __init__(self, index_file: str | Path = "code_index.json"):
        self.data: dict[str, Any] = json.loads(Path(index_file).read_text())
        self.entity_map: dict[str, dict] = {}
        self.complexity_map: dict[str, int] = {}
        self._build_indices()
    
    def _build_indices(self) -> None:
        """Build in-memory maps for O(1) lookups."""
        for file in self.data["files"]:
            for entity in file.get("entities", []):
                self.entity_map[entity["name"]] = {
                    "file": file["path"],
                    "meta": entity
                }
            for comp in file.get("complexity", []):
                key = f"{file['path']}::{comp['name']}"
                self.complexity_map[key] = comp["complexity"]
    
    def find(self, name: str) -> dict[str, Any] | None:
        """Find class or function by name (O(1))."""
        return self.entity_map.get(name)
    
    def complex(self, threshold: int = 10) -> list[dict[str, Any]]:
        """List functions above given complexity threshold."""
        results = []
        for key, complexity in self.complexity_map.items():
            if complexity >= threshold:
                file, func = key.split("::")
                results.append({
                    "file": file,
                    "function": func,
                    "complexity": complexity
                })
        return results
    
    def dependencies(self, file: str) -> list[str]:
        """Get dependencies for a file."""
        return self.data["dependencies"].get(file, [])
    
    def top_complex(self, n: int = 10) -> list[tuple[str, int]]:
        """Return top N most complex functions."""
        return sorted(
            self.complexity_map.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
```

**Performance**:
- **find()**: O(1) dict lookup
- **complex()**: O(n) where n = total functions, typically <1ms
- **dependencies()**: O(1) dict lookup
- **top_complex()**: O(n log n) sort, cached results possible

### 4.3 Rules Module (src/pystructmap/rules.py)

#### 4.3.1 RuleEngine Class

**Purpose**: Evaluate code metrics against dynamic YAML-based rules.

**Class Signature**:
```python
class RuleEngine:
    def __init__(self, rules_file: str | Path = "rules.yaml"):
        self.path = Path(rules_file)
        self.data = yaml.safe_load(self.path.read_text()) if self.path.exists() else {}
        self.metrics = self.data.get("metrics", {})
        self.actions = self.data.get("actions", [])
    
    def evaluate(self, file_info: dict) -> list[dict[str, Any]]:
        """Evaluate rules against file metrics."""
        results = []
        raw = file_info.get("raw", {})
        
        for rule in self.actions:
            for entity in file_info.get("entities", []):
                context = {
                    "raw": raw,
                    "complexity": self._get_complexity(file_info, entity),
                    "metrics": self.metrics,
                    "entity": entity
                }
                
                try:
                    if eval(rule["condition"], {}, context):
                        results.append({
                            "rule": rule["id"],
                            "desc": rule["description"],
                            "target": entity["name"],
                            "file": file_info["path"],
                            "action": rule.get("action", "")
                        })
                except Exception:
                    continue
        
        return results
    
    def _get_complexity(self, file_info: dict, entity: dict) -> int:
        """Find complexity for entity."""
        for comp in file_info.get("complexity", []):
            if comp["name"] == entity["name"]:
                return comp["complexity"]
        return 0
```

**rules.yaml Schema**:
```yaml
metrics:
  max_class_loc: 200
  max_function_loc: 50
  max_complexity: 10
  min_comment_ratio: 0.05

actions:
  - id: "R001"
    description: "Large classes"
    condition: "entity['type'] == 'ClassDef' and raw['loc'] > metrics['max_class_loc']"
    action: "Consider splitting into smaller classes"
  
  - id: "R002"
    description: "High complexity"
    condition: "complexity > metrics['max_complexity']"
    action: "Refactor to reduce cyclomatic complexity"
```

### 4.4 Scoring Module (src/pystructmap/scoring.py)

#### 4.4.1 ScoringEngine Class

**Purpose**: Rank files by weighted refactor priority score.

**Class Signature**:
```python
class ScoringEngine:
    def __init__(self, rules_file: str | Path = "rules.yaml"):
        self.rules_file = Path(rules_file)
        self.rules = yaml.safe_load(self.rules_file.read_text()) if self.rules_file.exists() else {}
        self.weights = {
            "complexity": 0.5,
            "size": 0.3,
            "coupling": 0.2
        }
        if "weights" in self.rules:
            self.weights.update(self.rules["weights"])
    
    def score_file(self, file_info: dict, deps: dict[str, list[str]]) -> dict[str, Any]:
        """Compute weighted score for a file."""
        raw = file_info.get("raw", {})
        
        # Average complexity
        complexities = [c["complexity"] for c in file_info.get("complexity", [])]
        avg_complexity = sum(complexities) / max(len(complexities), 1)
        
        # LOC
        loc = raw.get("loc", 0)
        
        # Coupling (number of imports)
        coupling = len(deps.get(file_info["path"], []))
        
        # Normalize to 0-1
        normalized = {
            "complexity": self._scale(avg_complexity, 0, 30),
            "size": self._scale(loc, 0, 500),
            "coupling": self._scale(coupling, 0, 30)
        }
        
        # Weighted sum
        total = sum(self.weights[k] * v for k, v in normalized.items())
        
        return {
            "file": file_info["path"],
            "complexity": avg_complexity,
            "loc": loc,
            "coupling": coupling,
            "score": round(total, 3)
        }
    
    def rank(self, index: dict) -> list[dict[str, Any]]:
        """Rank all files by refactor priority."""
        deps = index.get("dependencies", {})
        ranked = [self.score_file(f, deps) for f in index["files"]]
        return sorted(ranked, key=lambda x: x["score"], reverse=True)
    
    @staticmethod
    def _scale(value: float, min_val: float, max_val: float) -> float:
        """Normalize metric to 0-1."""
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
```

**Output Example** (refactor_rank.json):
```json
[
  {
    "file": "src/core/api.py",
    "complexity": 18.5,
    "loc": 450,
    "coupling": 12,
    "score": 0.875
  },
  {
    "file": "src/db/manager.py",
    "complexity": 15.2,
    "loc": 320,
    "coupling": 8,
    "score": 0.742
  }
]
```

### 4.5 Agent Adapter Module (src/pystructmap/agent_adapter.py)

#### 4.5.1 AgentAdapter Class

**Purpose**: High-level convenience API for agents.

**Class Signature**:
```python
class AgentAdapter:
    def __init__(self, root: Path = Path(".")):
        self.root = root
        self.index_path = root / "code_index.json"
        self.rank_path = root / "refactor_rank.json"
        self.violations_path = root / "violations.json"
        self.ci = CodeIndex(self.index_path)
        self.re = RuleEngine(root / "rules.yaml") if (root / "rules.yaml").exists() else None
        self.se = ScoringEngine(root / "rules.yaml") if (root / "rules.yaml").exists() else ScoringEngine()
    
    def get_symbol_location(self, symbol: str) -> dict[str, Any] | None:
        """Return file and line location for symbol."""
        return self.ci.find(symbol)
    
    def get_top_refactors(self, limit: int = 10) -> list[dict[str, Any]]:
        """Return top-N ranked refactor targets."""
        data = self._load_json(self.rank_path)
        return data[:limit]
    
    def get_rule_violations(self) -> list[dict[str, Any]]:
        """Return all rule violations."""
        return self._load_json(self.violations_path)
    
    def get_complex_functions(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Find all functions above complexity threshold."""
        return self.ci.complex(threshold)
    
    def get_dependency_hotspots(self, min_edges: int = 3) -> list[str]:
        """Return modules with many import dependencies."""
        deps = self.ci.data.get("dependencies", {})
        return [f for f, imps in deps.items() if len(imps) >= min_edges]
    
    def get_untyped_or_poor_docs(self) -> list[dict[str, Any]]:
        """Find files with low type coverage or missing docstrings."""
        untyped = []
        for f in self.ci.data["files"]:
            tc = f.get("type_coverage") or {}
            if tc.get("ratio", 1) < 0.5 or f.get("docstring_ratio", 1) < 0.3:
                untyped.append({
                    "file": f["path"],
                    "type_ratio": tc.get("ratio"),
                    "doc_ratio": f.get("docstring_ratio")
                })
        return untyped
    
    def summarize_state(self) -> dict[str, Any]:
        """Compact summary for agent decision loops."""
        return {
            "total_files": len(self.ci.data["files"]),
            "top_refactors": [r["file"] for r in self.get_top_refactors(5)],
            "complex_hotspots": [x["file"] for x in self.get_complex_functions(12)[:5]],
            "dependency_hotspots": self.get_dependency_hotspots(),
            "untyped_or_poor_docs": self.get_untyped_or_poor_docs()
        }
    
    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            return []
        return json.loads(path.read_text())
```

---

## 5. JSON Schema

### 5.1 code_index.json Structure

```json
{
  "scanned_root": "/workspace/project",
  "scanned_at": "2025-11-10T12:34:56",
  "version": "0.1.0",
  "total_files": 67,
  "files": [
    {
      "path": "src/module.py",
      "entities": [
        {
          "type": "ClassDef",
          "name": "ApiClient",
          "lineno": 15,
          "end_lineno": 120,
          "docstring": "HTTP client for API communication",
          "methods": ["__init__", "request", "get", "post"],
          "bases": ["BaseClient"]
        },
        {
          "type": "FunctionDef",
          "name": "parse_response",
          "lineno": 125,
          "end_lineno": 140,
          "docstring": "Parse JSON response"
        }
      ],
      "complexity": [
        {
          "type": "function",
          "name": "parse_response",
          "lineno": 125,
          "complexity": 8
        }
      ],
      "raw": {
        "loc": 250,
        "sloc": 180,
        "comments": 40,
        "multi": 10,
        "blank": 20
      },
      "comment_ratio": 0.16,
      "git": {
        "commits": 34,
        "last_author": "Thomas Weholt",
        "last_commit": "2025-11-08"
      },
      "maintainability_index": 72.4,
      "has_tests": true,
      "hash": "3e2f8b8c71c5d9d8d5c85f2e6a4d8a3b2fbe9b1a",
      "type_coverage": {
        "annotated": 12,
        "total": 15,
        "ratio": 0.8
      },
      "docstring_ratio": 0.67,
      "call_graph": [
        ["send_request", "log_error"],
        ["send_request", "make_request"]
      ]
    }
  ],
  "dependencies": {
    "src/module.py": {
      "imports": ["os", "json", "httpx", "src.config"],
      "imported_by": ["src/main.py", "tests/test_api.py"]
    }
  },
  "symbol_index": {
    "ApiClient": "src/module.py:15",
    "parse_response": "src/module.py:125"
  }
}
```

### 5.2 Schema Version

- **Current**: 0.1.0
- **Compatibility**: Backward compatible additions only
- **Breaking Changes**: Require major version bump

---

## 6. Query API

### 6.1 CodeIndex Methods

#### find(name: str) -> dict | None
Returns entity location and metadata.

**Example**:
```python
ci = CodeIndex()
result = ci.find("ApiClient")
# Returns: {"file": "src/api.py", "meta": {...}}
```

#### complex(threshold: int = 10) -> list[dict]
Returns functions above complexity threshold.

**Example**:
```python
complex_funcs = ci.complex(threshold=15)
# Returns: [{"file": "...", "function": "...", "complexity": 18}, ...]
```

#### dependencies(file: str) -> list[str]
Returns list of imports for a file.

**Example**:
```python
deps = ci.dependencies("src/api.py")
# Returns: ["os", "json", "httpx", "src.config"]
```

#### top_complex(n: int = 10) -> list[tuple]
Returns top N most complex functions.

**Example**:
```python
top = ci.top_complex(5)
# Returns: [("src/api.py::send_request", 18), ...]
```

---

## 7. Rules Engine

### 7.1 rules.yaml Schema

```yaml
metrics:
  max_class_loc: 200
  max_function_loc: 50
  max_complexity: 10
  min_comment_ratio: 0.05

weights:
  complexity: 0.5
  size: 0.3
  coupling: 0.2

actions:
  - id: "R001"
    description: "Large classes"
    condition: "entity['type'] == 'ClassDef' and raw['loc'] > metrics['max_class_loc']"
    action: "Consider splitting into smaller classes"
  
  - id: "R002"
    description: "High complexity"
    condition: "complexity > metrics['max_complexity']"
    action: "Refactor to reduce cyclomatic complexity"
  
  - id: "R003"
    description: "Poor documentation"
    condition: "raw['loc'] > 50 and raw['comments'] / raw['loc'] < metrics['min_comment_ratio']"
    action: "Add docstrings and comments"
```

### 7.2 Condition Evaluation

Conditions are Python expressions evaluated with safe context:
- `entity`: Current entity dict (type, name, lineno, etc.)
- `raw`: Raw metrics dict (loc, sloc, comments, etc.)
- `complexity`: Cyclomatic complexity value
- `metrics`: Configured thresholds from rules.yaml

**Security**: Uses eval() with restricted globals/locals to prevent code injection.

---

## 8. Scoring System

### 8.1 Weighted Scoring Formula

```
normalized_complexity = scale(avg_complexity, 0, 30)
normalized_size = scale(loc, 0, 500)
normalized_coupling = scale(coupling, 0, 30)

score = (
    weights["complexity"] * normalized_complexity +
    weights["size"] * normalized_size +
    weights["coupling"] * normalized_coupling
)
```

### 8.2 Normalization

Scale function maps metric values to [0, 1]:
```python
def scale(value, min_val, max_val):
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
```

### 8.3 Default Weights

- **complexity**: 0.5 (highest priority)
- **size**: 0.3 (medium priority)
- **coupling**: 0.2 (lower priority)

Weights can be overridden in rules.yaml.

---

## 9. CLI Commands

### 9.1 scan Command

**Signature**:
```bash
uv run pystructmap scan [ROOT] [OPTIONS]
```

**Options**:
- `--output PATH`: Output file (default: code_index.json)
- `--deep`: Enable deep analysis (call graphs, type coverage)
- `--cache / --no-cache`: Use incremental caching (default: True)
- `--rich`: Pretty console output
- `--visual`: Generate HTML dependency graph

**Examples**:
```bash
# Basic scan
uv run pystructmap scan .

# Deep scan with caching
uv run pystructmap scan . --deep --cache

# Custom output location
uv run pystructmap scan /path/to/project --output analysis/index.json
```

### 9.2 watch Command

**Signature**:
```bash
uv run pystructmap watch [ROOT] [OPTIONS]
```

**Options**:
- `--deep`: Enable deep analysis
- `--cache / --no-cache`: Use incremental caching (default: True)

**Example**:
```bash
# Watch current directory
uv run pystructmap watch .

# Watch with deep analysis
uv run pystructmap watch . --deep
```

### 9.3 rank Command

**Signature**:
```bash
uv run pystructmap rank [OPTIONS]
```

**Options**:
- `--rules PATH`: Custom rules file (default: rules.yaml)
- `--top N`: Show top N files (default: 20)

**Example**:
```bash
# Rank top 10 refactor targets
uv run pystructmap rank --top 10
```

### 9.4 check Command

**Signature**:
```bash
uv run pystructmap check [OPTIONS]
```

**Options**:
- `--rules PATH`: Rule definitions (default: rules.yaml)
- `--threshold N`: Min complexity (default: 0)

**Example**:
```bash
# Check for rule violations
uv run pystructmap check
```

### 9.5 agent Command

**Signature**:
```bash
uv run pystructmap agent [OPTIONS]
```

**Options**:
- `--summary`: Print summarized project state
- `--symbol NAME`: Lookup specific class or function
- `--top N`: Show top-N ranked refactor targets (default: 5)
- `--complex-threshold N`: Minimum complexity (default: 12)
- `--untyped`: List untyped or poorly documented files

**Examples**:
```bash
# Get project summary
uv run pystructmap agent --summary

# Find symbol location
uv run pystructmap agent --symbol ApiClient

# Get top refactors
uv run pystructmap agent --top 10

# Find untyped files
uv run pystructmap agent --untyped
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

#### Scanner Tests (tests/test_scanner.py)
- Test AST parsing for classes, functions, async functions
- Test entity extraction with line numbers and docstrings
- Test metrics calculation (complexity, LOC, MI)
- Test git metadata extraction
- Test incremental caching logic
- Test deep analysis (call graphs, type coverage)
- Mock file system for deterministic tests

#### Query Tests (tests/test_query.py)
- Test CodeIndex initialization and index building
- Test find() with existing and non-existing symbols
- Test complex() filtering
- Test dependencies() lookup
- Test top_complex() sorting
- Use fixture JSON data for consistency

#### Rules Tests (tests/test_rules.py)
- Test YAML loading and parsing
- Test condition evaluation with various metrics
- Test action recommendations
- Test error handling for invalid conditions
- Mock rules.yaml files

#### Scoring Tests (tests/test_scoring.py)
- Test score calculation with various metrics
- Test normalization function
- Test weighted scoring
- Test ranking order
- Test custom weights from rules.yaml

### 10.2 Integration Tests

#### Full Scan Workflow (tests/test_integration_scan.py)
- Create temporary directory with sample Python files
- Run full scan (scanner → JSON → CodeIndex)
- Verify JSON structure and content
- Verify query results match expected values
- Clean up temporary files

#### Incremental Updates (tests/test_integration_incremental.py)
- Run initial scan
- Modify a file
- Run incremental scan
- Verify only modified file was re-scanned
- Verify cache was updated correctly

#### Performance Tests (tests/test_integration_performance.py)
- Scan large fixture codebase (~1000 files)
- Measure scan time (should be <10s)
- Measure load time (should be <200ms)
- Measure query time (should be <1ms)
- Use pytest-benchmark for accurate timing

### 10.3 Test Coverage Requirements

- **Minimum**: 70% overall coverage
- **Critical modules**: 90% coverage for scanner.py, query.py
- **Timeout**: All tests must complete within 5 seconds
- **Fixtures**: Use realistic Python code samples

### 10.4 Test Execution

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src/pystructmap --cov-report=term-missing

# Run with timeout enforcement
uv run pytest tests/ --timeout=5

# Run specific test file
uv run pytest tests/test_scanner.py -v
```

---

## 11. Performance Optimization

### 11.1 Incremental Caching

**Mechanism**:
- Compute SHA-256 hash of each Python file
- Store hashes in .pystructmap_cache.json
- On rescan, skip files with unchanged hashes
- Only re-analyze modified files
- Merge results with existing index

**Performance Gain**:
- First scan: ~1000 files/second
- Incremental scan: ~10ms for typical changes (1-5 files modified)

**Implementation**:
```python
import hashlib

def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# In scanner
cached_hash = cache.get_hash(str(path))
current_hash = file_hash(path)
if cached_hash == current_hash:
    continue  # Skip unchanged file
```

### 11.2 Watch Mode

**Mechanism**:
- Uses watchdog library for file system events
- Monitors CREATE, MODIFY, DELETE events
- Filters for *.py files only
- Triggers incremental rescan on change
- Atomic write to code_index.json

**Performance**:
- Event detection: <100ms
- Incremental rescan: <500ms for typical changes
- No polling overhead (event-driven)

**Implementation**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            trigger_incremental_scan(event.src_path)
```

### 11.3 In-Memory Indices

**Mechanism**:
- Load code_index.json once at startup
- Build dict-based indices for O(1) lookups
- entity_map: name → {file, meta}
- complexity_map: "file::function" → complexity
- Keep indices in memory for entire session

**Performance**:
- Load time: <200ms for 50MB JSON
- Query time: <1µs per lookup (dict access)
- Memory overhead: ~2x JSON file size

### 11.4 Parallel Processing

**Mechanism** (future optimization):
- Use multiprocessing.Pool for large codebases
- Distribute files across CPU cores
- Merge results from workers
- Maintain deterministic order

**Expected Gain**:
- 4x speedup on 8-core machines for large codebases (>1000 files)

### 11.5 Lazy Loading

**Mechanism**:
- Don't compute expensive metrics unless needed
- Skip deep analysis (call graphs, type coverage) by default
- Only load RuleEngine/ScoringEngine when used
- Defer JSON parsing until first query

**Performance**:
- Faster startup for simple queries
- Reduced memory footprint when deep analysis not needed

---

## 12. Agent Integration

### 12.1 Direct Python API (Recommended)

**Pattern**:
```python
from pystructmap.query import CodeIndex
from pystructmap.agent_adapter import AgentAdapter

# One-time setup
adapter = AgentAdapter()

# Throughout agent session
location = adapter.get_symbol_location("ApiClient")
refactors = adapter.get_top_refactors(10)
complex_funcs = adapter.get_complex_functions(15)
summary = adapter.summarize_state()
```

**Advantages**:
- Zero serialization overhead
- Type-safe Python API
- O(1) lookups
- Direct memory access

### 12.2 CLI for Scripts

**Pattern**:
```bash
# Agent startup script
uv run pystructmap scan . --deep --cache

# Agent queries via subprocess
SYMBOL=$(uv run pystructmap agent --symbol ApiClient)
REFACTORS=$(uv run pystructmap agent --top 10)
```

**Advantages**:
- Language-agnostic (works from any language)
- Simple integration
- Structured JSON output

### 12.3 Rules-Based Analysis

**Pattern**:
```python
from pystructmap.rules import RuleEngine

re = RuleEngine("custom_rules.yaml")
violations = []
for file_data in ci.data["files"]:
    violations.extend(re.evaluate(file_data))

# Prioritize by rule severity
critical = [v for v in violations if v["rule"].startswith("CRIT")]
```

**Advantages**:
- Customizable without code changes
- Domain-specific rules
- Actionable recommendations

### 12.4 Static Analysis Integration

**Pattern**:
```bash
# Run comprehensive analysis
uv run pystructmap collect

# Agent reads consolidated report
import json
report = json.load(open("agent_report.json"))

lint_issues = report["ruff"]
security_issues = report["bandit"]
type_errors = report["mypy"]
```

**Tools Integrated**:
- **ruff**: Linting and style (JSON output)
- **mypy**: Type checking (JSON report)
- **bandit**: Security scanning (JSON output)
- **radon**: Already integrated in scanner

**Advantages**:
- Comprehensive coverage
- Mature, battle-tested tools
- Machine-readable output
- Deterministic results

### 12.5 Issue Generation

**Pattern**:
```python
# Generate issues from static analysis
from pystructmap.collect import collect_reports, write_issue

for idx, issue in enumerate(collect_reports(), 1):
    write_issue(issue, idx)

# Agent reads issues
issue_files = Path(".work/agent/issues").glob("BL-*.md")
for issue_file in issue_files:
    # Parse YAML front-matter and process
    pass
```

**Issue Format**:
```markdown
---
id: "BL-001"
title: "High complexity in send_request (18)"
description: "Cyclomatic complexity exceeds threshold"
priority: high
status: ⏳ OPEN
created: 2025-11-09
section: src/api
tags: [complexity, maintainability]
type: tech-debt
---

**Details**: Found by radon complexity scan.

**Suggested Action**:
- Split function into smaller helpers
- Move business rules to service layer

**Files Affected**:
- src/api/client.py:42-108
```

**Advantages**:
- Standardized issue format
- Deduplication via stable IDs
- Actionable recommendations
- Incremental updates (only new issues)

---

## 13. Acceptance Criteria

### 13.1 Core Functionality

- [ ] Scanner successfully parses 100% of valid Python files
- [ ] Extracted entities include correct line numbers and docstrings
- [ ] Complexity metrics match radon output
- [ ] Git metadata extraction handles missing .git directory gracefully
- [ ] CodeIndex.find() returns correct results in <1µs
- [ ] CodeIndex.complex() filters correctly
- [ ] RuleEngine evaluates conditions without errors
- [ ] ScoringEngine produces deterministic rankings
- [ ] AgentAdapter provides all documented methods

### 13.2 Performance

- [ ] Scan 1000 files in <10 seconds
- [ ] Incremental scan with 5 changed files completes in <1 second
- [ ] Load 50MB code_index.json in <200ms
- [ ] Query operations complete in <1ms
- [ ] Watch mode detects changes within 100ms

### 13.3 Quality

- [ ] 70%+ test coverage
- [ ] All tests complete within 5 seconds
- [ ] Zero linting errors (ruff check)
- [ ] Zero type checking errors (mypy)
- [ ] Security checks pass (ruff --select S)

### 13.4 Agent Integration

- [ ] Agent can import and use CodeIndex
- [ ] Agent can run CLI commands via subprocess
- [ ] Agent can parse rules.yaml and violations.json
- [ ] Agent can read refactor_rank.json
- [ ] Agent can consume issue files with YAML front-matter

### 13.5 Documentation

- [ ] README.md includes quick start guide
- [ ] All CLI commands documented with examples
- [ ] API reference for CodeIndex, RuleEngine, ScoringEngine
- [ ] Agent integration patterns documented
- [ ] rules.yaml schema documented with examples

---

## 14. Future Extensions

### 14.1 Language Plugins

- Support for JavaScript/TypeScript via esprima or ts-ast
- Support for Go via go/ast package
- Protocol-based scanner interface for extensibility

### 14.2 Semantic Search

- Embed docstrings and comments using sentence transformers
- Vector index for semantic code search
- "Find functions that handle authentication"

### 14.3 Historical Tracking

- Store metric deltas over time
- Detect improvement/regression trends
- Visualize code quality evolution

### 14.4 Team Dashboard

- Web UI for browsing code index
- Visualizations for dependency graphs
- Team-level metrics and goals

### 14.5 CI/CD Integration

- GitHub Actions workflow
- Quality gates (fail if complexity > threshold)
- Automated issue creation in issue tracker

---

## 15. References

### 15.1 Internal Documents

- **Development Guide**: `AGENTS.md`
- **Original Proposal**: `.work/agent/notes/original-proposal.md`
- **Task Lists**: `.work/agent/issues/{critical,high,medium,low}.md`

### 15.2 External Libraries

- **Radon**: Complexity and metrics - https://radon.readthedocs.io/
- **AST Module**: Python abstract syntax trees - https://docs.python.org/3/library/ast.html
- **Typer**: CLI framework - https://typer.tiangolo.com/
- **Watchdog**: File system events - https://github.com/gorakhargosh/watchdog

### 15.3 Related Tools

- **Ruff**: Fast Python linter - https://github.com/astral-sh/ruff
- **MyPy**: Static type checker - https://mypy.readthedocs.io/
- **Bandit**: Security linter - https://bandit.readthedocs.io/

---

**End of Specification Document**
