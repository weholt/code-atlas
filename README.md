# CodeAtlas

**Agent-oriented Python codebase structure and metrics analyzer**

CodeAtlas is a fast, local codebase analysis tool designed specifically for agentic coders. It scans Python projects, extracts structure (classes, methods, functions) and metrics (LOC, complexity, dependencies), then provides O(1) in-memory query API for instant access. Zero HTTP overhead, pure Python imports.

## Features

- **AST-Based Parsing** - Accurate extraction of classes, methods, functions with line numbers and docstrings
- **Radon Metrics** - Cyclomatic complexity, LOC, comment ratio, maintainability index
- **Dependency Graphs** - Import relationships and coupling analysis
- **Dynamic Rules** - YAML-based thresholds for detecting large classes, complex methods, refactor targets
- **O(1) Lookups** - In-memory indices for instant queries (find, complex, dependencies)
- **Agent-First Design** - JSON + Python API, no HTTP overhead, optimized for autonomous systems
- **Watch Mode** - Continuous monitoring with automatic rescanning on file changes
- **Extensible** - Protocol-based architecture for future language plugins (JS/TS/Go)

## Quick Start

### Installation

```bash
cd A-NEW-WORLD/code-atlas
uv sync
```

### Scan Your Codebase

```bash
# Scan current directory
uv run code-atlas scan .

# Scan with custom output
uv run code-atlas scan /path/to/project --output analysis/code_index.json
```

### CLI Commands

```bash
# Scan - Generate code_index.json
uv run code-atlas scan . --output code_index.json

# Rank - Prioritize refactor targets
uv run code-atlas rank --top 20 --output refactor_rank.json

# Check - Find rule violations
uv run code-atlas check --rules rules.yaml --output violations.json

# Agent - Query interface (JSON output for subprocess)
uv run code-atlas agent --summary
uv run code-atlas agent --symbol ClassName
uv run code-atlas agent --top 10
uv run code-atlas agent --complex-threshold 15

# Watch - Continuous monitoring
uv run code-atlas watch . --debounce 2.0
```

### Query from Python (Agent Integration)

```python
from code_atlas.query import CodeIndex

# Load once at agent startup
ci = CodeIndex("code_index.json")

# Find where a class or function is defined (O(1))
info = ci.find("DatabaseManager")
print(f"Found at {info['file']}:{info['meta']['lineno']}")

# Get high-complexity functions (for refactor prioritization)
complex_funcs = ci.complex(threshold=15)
for fn in complex_funcs:
    print(f"{fn['file']}:{fn['function']} - complexity {fn['complexity']}")

# Check dependencies for a file
deps = ci.dependencies("src/core/api.py")
print(f"Imports: {deps['imports']}")
print(f"Imported by: {deps['imported_by']}")
```

## Architecture

```
┌─────────────┐
│  Codebase   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Scanner   │  AST + Radon + Dependency Analysis
│  (scan cmd) │
└──────┬──────┘
       │
       ▼ (writes)
┌─────────────────┐
│ code_index.json │  Persistent, portable, agent-friendly
└──────┬──────────┘
       │
       ▼ (loads once)
┌─────────────┐
│  CodeIndex  │  In-memory indices for O(1) lookups
│ (query API) │
└──────┬──────┘
       │
       ▼ (imports)
┌─────────────┐
│    Agent    │  Autonomous coder using fast queries
└─────────────┘
```

## Output Format

### code_index.json Structure

```json
{
  "scanned_root": "/workspace/project",
  "scanned_at": "2025-11-10T12:34:56",
  "version": "0.1.0",
  "files": [
    {
      "path": "src/module.py",
      "entities": [
        {
          "type": "class",
          "name": "ApiClient",
          "lineno": 15,
          "end_lineno": 120,
          "docstring": "HTTP client for API communication",
          "methods": ["__init__", "request", "get", "post"]
        },
        {
          "type": "function",
          "name": "parse_response",
          "lineno": 125,
          "end_lineno": 140,
          "docstring": "Parse JSON response",
          "complexity": 8
        }
      ],
      "complexity": [
        {"function": "parse_response", "complexity": 8, "lineno": 125}
      ],
      "raw": {
        "loc": 250,
        "sloc": 180,
        "comments": 40,
        "multi": 10,
        "blank": 20
      }
    }
  ],
  "dependencies": {
    "src/module.py": {
      "imports": ["os", "json", "httpx", "src.config"],
      "imported_by": ["src/main.py", "tests/test_api.py"]
    }
  }
}
```

## Rules Configuration

Create `rules.yaml` to define dynamic thresholds:

```yaml
metrics:
  max_class_loc: 200        # Flag large classes
  max_function_loc: 40      # Flag long functions
  max_complexity: 15        # Flag complex functions
  min_comment_ratio: 0.05   # Flag poorly documented files

actions:
  - id: "R001"
    condition: "entity.type == 'class' and entity.loc > max_class_loc"
    message: "Class {entity.name} exceeds max LOC ({entity.loc} > {max_class_loc})"
    action: "Consider splitting into smaller classes"

  - id: "R002"
    condition: "entity.type == 'function' and entity.complexity > max_complexity"
    message: "Function {entity.name} exceeds max complexity ({entity.complexity} > {max_complexity})"
    action: "Refactor to reduce cyclomatic complexity"
```

Use in agent:

```python
from code_atlas.rules import RuleEngine

re = RuleEngine("rules.yaml")
issues = re.evaluate(file_data)
# Returns list of flagged issues with recommended actions
```

## Development

### Essential Commands

```bash
uv sync                          # Install dependencies
uv run python scripts/build.py   # Run full quality pipeline
uv run python scripts/build.py --verbose --fix  # Auto-fix issues
uv run pytest tests/             # Run tests only
uv run mypy src/code_atlas/      # Type check only
uv run ruff check src/code_atlas/   # Lint only
```

### Project Structure

```
code-atlas/
├── src/code_atlas/
│   ├── __init__.py
│   ├── scanner.py      # AST parsing, radon metrics, entity extraction
│   ├── query.py        # CodeIndex class with O(1) lookups
│   ├── rules.py        # RuleEngine for YAML-based analysis
│   └── cli.py          # Typer commands (scan, load, query)
├── tests/
│   ├── test_scanner.py
│   ├── test_query.py
│   ├── test_rules.py
│   └── fixtures/       # Sample Python files for testing
├── examples/
│   ├── agent_usage.py
│   └── rules.yaml
├── scripts/
│   └── build.py
├── pyproject.toml
├── rules.yaml.example
└── README.md
```

### Quality Standards

- **70%+ test coverage** enforced via pytest-cov
- **5-second test timeout** for all tests
- **Ruff** for linting and formatting
- **MyPy** for type checking (strict mode)
- **Security checks** via ruff --select S

## Agent Integration Patterns

### Pattern 1: Direct Python API (Recommended)

```python
from code_atlas.query import CodeIndex

# Agent startup
ci = CodeIndex("code_index.json")

# Throughout agent session
def find_refactor_candidates():
    return ci.complex(threshold=15)

def locate_class(name: str):
    return ci.find(name)

def analyze_coupling(file: str):
    return ci.dependencies(file)
```

### Pattern 2: CLI for Batch Analysis

```bash
# Pre-agent scan
uv run code-atlas scan /workspace --output /tmp/code_index.json

# Agent reads JSON directly
import json
with open("/tmp/code_index.json") as f:
    data = json.load(f)
```

### Pattern 3: Watch Mode for Continuous Updates

```bash
# Run watch mode in background
uv run code-atlas watch . --output code_index.json --debounce 2.0

# Agent loads index and always has fresh data
# Index automatically updates when .py files change
```

### Pattern 4: Agent CLI Interface

```bash
# Query via subprocess for structured JSON output
uv run code-atlas agent --summary
uv run code-atlas agent --symbol ApiClient
uv run code-atlas agent --top 10
uv run code-atlas agent --complex-threshold 15

# Or use high-level convenience API
```python
from code_atlas.agent_adapter import AgentAdapter

adapter = AgentAdapter(root=Path.cwd())
summary = adapter.summarize_state()
violations = adapter.get_rule_violations()
hotspots = adapter.get_dependency_hotspots(min_edges=5)
```

## Performance

- **Scan**: ~1000 files/second (Python AST + radon)
- **Load**: <200ms for 50MB JSON (in-memory indices)
- **Query**: <1µs per lookup (dict-based O(1) access)
- **Memory**: ~2x JSON file size for in-memory indices

## Troubleshooting

### Import Errors

If `radon` or `pyyaml` not found:
```bash
uv sync
```

### Missing code_index.json

Run scan first:
```bash
uv run code-atlas scan .
```

### Slow Scans

Use watch mode for continuous updates (rescans only on file changes):
```bash
uv run code-atlas watch . --debounce 2.0
```

For large codebases, consider scanning specific directories:
```bash
uv run code-atlas scan src/core
```

## Contributing

See `AGENTS.md` for development workflow and mandatory standards.

## License

MIT License - see `LICENSE` file.

## References

- **Radon**: https://radon.readthedocs.io/
- **AST Module**: https://docs.python.org/3/library/ast.html
- **Typer**: https://typer.tiangolo.com/
