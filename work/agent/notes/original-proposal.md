# PyStructMap - Original Proposal

## Context

I need a utility or a script that can scan a python based codebase, build a searchable tree of all classes, methods, functions etc with metrics on each like lines of code, dependency graphs etc. It should link to the original files as well. I want to use this as a tool the agentic coder can use to navigate the codebase faster, find files that needs to be refactored etc. I'd like to use an existing tool for code analysis and just want to package this in a way the agent can update and use easily

## Evolution

The proposal evolved through several iterations:

### Iteration 1: Core Concept
- Use pylint + radon + networkx + ast as core analyzers
- Expose results as JSON + Markdown index
- AST to collect classes, functions, methods, file paths
- Record start/end line numbers, docstrings, decorators, cyclomatic complexity
- radon cc for complexity, radon raw for LOC, comment ratio
- Build call/dependency graph using networkx

### Iteration 2: Agent-First Design
- **Key Decision**: Use uv for easy agent use
- Focus on agent-friendly solution over human visualization
- Humanly nice stuff like rich and visualization should be opt-in
- Minimal dependencies, fast parse, ready for uv
- Optional human features toggled with --visual or --rich

### Iteration 3: Query Interface
- **Critical Requirement**: Locally running thing for the agent to use only, must be as fast as possible
- **Key Decision**: Skip HTTP entirely - use direct JSON + in-memory index with minimal Python API
- Fast, zero-overhead, no serialization
- O(1) lookups via in-memory indices
- Load JSON once (~50 MB in <0.2 s), microsecond dict lookups
- No HTTP, no process overhead

### Iteration 4: Dynamic Rules
- **Key Enhancement**: Define a set of dynamic rules, preferably not hardcoded
- Externalize analysis rules into YAML or JSON ruleset file
- Agent and human can both edit it; no code changes needed
- Rules define thresholds for large classes, complex methods, poorly documented files
- Actions define conditions and recommended fixes

### Iteration 5: Scoring and Ranking
- Automatic scoring + refactor priority ranking
- Weight by complexity × size × coupling
- Normalized metrics (0-1 scale) for complexity, size, coupling
- Configurable weights in rules.yaml
- Generates refactor_rank.json with prioritized targets

### Iteration 6: Enhanced Metadata
- **Comment ratio**: Detect poor documentation
- **Git metadata**: Commit count, last author, last modification date (detect hotspots)
- **Test coverage linkage**: Flag files with/without matching test files
- **Maintainability index**: radon.metrics.mi_visit (0-100 scale)
- **Symbol index**: Quick lookup table for any symbol

### Iteration 7: Deep Analysis Mode
- **Call graph mapping**: Static call graph (function → functions it calls)
- **Type-annotation coverage**: Count functions with type hints
- **Docstring presence ratio**: Measure self-documentation
- **Stable SHA-256 hashes**: Detect exact changes without re-parsing

### Iteration 8: Incremental Caching
- Skip unchanged files using SHA-256 hash comparison
- Merge fresh metrics only for modified ones
- .pystructmap_cache.json for persistence
- Cut scan time to tens of milliseconds for large codebases

### Iteration 9: Watch Mode
- Continuous scanning using watchdog
- Triggers instant incremental rescans when .py files change
- No re-analysis of untouched files
- Keeps code_index.json always current for agents

### Iteration 10: Static Analysis Integration
- **Key Insight**: Offload to mature static-analysis tools instead of custom AST walking
- Tools produce machine-readable output (JSON, SARIF)
- Aggregate reports from: ruff, radon, mypy, bandit, vulture, safety, coverage
- Build orchestrator that runs tools and merges normalized JSON
- Agent consumes single agent_report.json with all findings

### Iteration 11: Issue Generation
- Convert static analysis findings to structured issue format
- Map linter/analyzer output → templated issue files with YAML front-matter
- Deduplication using stable IDs (hash of section + title + tags)
- Incremental updates: only write new or changed issues
- Merge duplicate findings (same file + line + tag)

## Final Architecture

```
┌─────────────┐
│  Codebase   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Scanner       │  AST + Radon + Git + Radon MI + Call Graph + Type Coverage
│  (scan cmd)     │  With incremental caching (--cache) and deep analysis (--deep)
└──────┬──────────┘
       │
       ▼ (writes)
┌─────────────────┐
│ code_index.json │  Persistent, portable, agent-friendly
└──────┬──────────┘
       │
       ▼ (loads once)
┌─────────────┐
│  CodeIndex  │  In-memory indices for O(1) lookups
│ (query API) │  + RuleEngine + ScoringEngine
└──────┬──────┘
       │
       ▼ (imports)
┌─────────────┐
│    Agent    │  Autonomous coder using fast queries
└─────────────┘

Parallel:
┌─────────────────────┐
│ Watch Mode (--watch)│ → Continuous updates to code_index.json
└─────────────────────┘

┌─────────────────────────┐
│ Static Tools Orchestra  │ → ruff, radon, mypy, bandit → agent_report.json → issue files
└─────────────────────────┘
```

## Key Design Decisions

1. **No HTTP/FastAPI** - Pure Python API for zero overhead
2. **JSON as intermediate format** - Portable, parseable, agent-friendly
3. **In-memory indices** - O(1) lookups for instant queries
4. **Dynamic YAML rules** - Flexibility without code changes
5. **AST + radon** - Accurate metrics
6. **Incremental scan** - Performance optimization for large codebases
7. **Protocol-based extensibility** - Future language plugins (JS/TS/Go)
8. **Watch mode** - Continuous analysis for always-current data
9. **Static tool integration** - Leverage mature analyzers instead of custom scanning
10. **Issue format standardization** - Deterministic issue generation from static analysis

## Dependencies

### Core
- typer>=0.9.0 - CLI framework
- radon>=6.0.0 - Metrics (complexity, MI, LOC)
- pyyaml>=6.0 - Dynamic rules configuration

### Optional (Human Visualization)
- rich>=13.7.0 - Pretty console output
- networkx>=3.2 - Dependency graph analysis
- pyvis>=0.3.2 - HTML dependency visualization

### Dev
- pytest>=7.4.3 - Testing
- pytest-cov>=4.1.0 - Coverage
- pytest-timeout>=2.2.0 - Timeout enforcement
- ruff>=0.1.9 - Linting and formatting
- mypy>=1.7.1 - Type checking

## Performance Targets

- **Scan**: ~1000 files/second (Python AST + radon)
- **Load**: <200ms for 50MB JSON (in-memory indices)
- **Query**: <1µs per lookup (dict-based O(1) access)
- **Memory**: ~2x JSON file size for in-memory indices

## Agent Integration Patterns

### Pattern 1: Direct Python API (Recommended)
```python
from pystructmap.query import CodeIndex
ci = CodeIndex("code_index.json")
info = ci.find("ClassName")
complex_funcs = ci.complex(threshold=15)
```

### Pattern 2: CLI for Scripts
```bash
uv run pystructmap scan . --output analysis/code_index.json
# Agent reads JSON directly
```

### Pattern 3: Rules-Based Analysis
```python
from pystructmap.rules import RuleEngine
re = RuleEngine("rules.yaml")
issues = re.evaluate(file_data)
```

### Pattern 4: Continuous Updates
```bash
uv run pystructmap watch .
# code_index.json stays current automatically
```

### Pattern 5: Agent CLI Interface
```bash
uv run pystructmap agent --summary
uv run pystructmap agent --symbol ApiClient
uv run pystructmap agent --untyped
```

## Success Criteria

1. ✅ Agent can query codebase structure in <1µs per lookup
2. ✅ Incremental scans complete in <1s for typical changes
3. ✅ No external dependencies (HTTP, databases, network)
4. ✅ Deterministic output for reproducible agent reasoning
5. ✅ Extensible rules without code modifications
6. ✅ Integration with mature static analysis tools
7. ✅ Automated issue generation from findings
8. ✅ Watch mode for continuous analysis
