# CodeAtlas Development Guide

## General instructions

- **IMPORTANT** Do not create summaries or explanations.
- **NO FUCKING SUMMARY DOCUMENTS**
- Focus on writing code, not talking.
- **NEVER** use `python -c` commands with multi-line code in terminal - it hangs the terminal
- Use separate Python files or simple single-line commands only
- **NEVER** print code to the terminal that should go into a file. Write directly to file. It hangs the terminal and stops the process.
- There is **NO** time constraints - fuck estimates, just finish your tasks
- There is **NO** legacy system to consider, no need for migration or fallback to legacy code while implementing

## Development Workflows

### Essential Commands (ALWAYS use `uv`)

```bash
uv sync                    # Install dependencies
uv run python scripts/build.py    # Full quality pipeline (format, lint, type-check, test)
uv run python scripts/build.py --verbose  # Auto-fix issues with detailed output
uv run code-atlas scan .  # Scan current codebase
uv run pytest tests/      # Run tests only
```

## Key Patterns & Conventions

### Agent-First Design

- **Fast local operation** - No HTTP/API overhead, pure Python imports
- **O(1) lookups** - In-memory indices for instant queries
- **JSON intermediate** - Portable, parseable, agent-friendly
- **Dynamic rules** - YAML-based configuration without code changes

### Quality Standards (Enforced by build.py)

- **70%+ test coverage** required
- **5-second test timeout** for all tests
- **Ruff** for linting + formatting (replaces black/isort)
- **MyPy** type checking with strict mode
- Security checks via `ruff --select S`

## File Organization Logic

- **`src/code_atlas/`** - Main package
  - `scanner.py` - AST parsing and entity extraction
  - `query.py` - CodeIndex class with O(1) lookups
  - `rules.py` - RuleEngine for dynamic YAML-based metrics
  - `cli.py` - Typer commands (scan, load, query)
- **`tests/`** - All tests with strict timeout enforcement
- **`examples/`** - Agent integration examples
- **`rules.yaml.example`** - Sample rule configuration

## Common Pitfalls

- Always use `uv run` prefix for Python commands (never direct python)
- Tests must complete within 5 seconds (use minimal fixtures)
- Never use HTTP/FastAPI - this is a local-only tool for agents
- All imports must be at top of file (never inline)
- JSON schema must be stable and versioned

## Mandatory instructions

- Failure to follow these particular rules will result in **immediate** termination.
- You are not allowed to write non-code related files, like summaries and explanation in markdown files, testscripts etc into the project structure other places than the `.work/agent` folder.
- Follow instructions given in specifications, tasklists and other reference material provided.
- Do not get creative outside the instructions given.
- Do not create nice-to-have fields in models not mentioned in the spec
- Do not create nice-to-have commands in CLIs or endpoints in APIs not mentioned in the spec
- Do not adjust the test coverage threshold.

## Development guide

- Run `uv run python scripts/build.py` after each substantial change
    - Iterate until all checks pass
    - Write tests until coverage is 70%+
- Use `uv run python scripts/build.py --verbose` to auto-fix formatting/linting issues
- Add tests for new features in `tests/`
- Follow existing code style and patterns
- **MANDATORY** **IMPORTS** ALWAYS at the top of the file, NEVER inline
    - Use conditional imports at module level if needed (try/except at top)
    - Never use inline imports inside functions or methods

## Performance Considerations

- **In-memory indices** - Load JSON once, query many times
- **Lazy loading** - Only parse files when needed
- **Incremental scan** - Support updating index for changed files only
- **Parallel processing** - Use multiprocessing for large codebases
- **Caching** - Cache parsed AST and metrics between runs

## Agent Integration Patterns

### Direct Python API (Preferred)

```python
from code_atlas.query import CodeIndex

# Load once at agent startup
ci = CodeIndex("code_index.json")

# O(1) lookups throughout session
info = ci.find("ClassName")
complex_funcs = ci.complex(threshold=15)
deps = ci.dependencies("src/module.py")
```

### CLI for Scripts

```bash
# Scan before agent starts
uv run code-atlas scan . --output analysis/code_index.json

# Agent reads JSON directly
```

### Rules-Based Analysis

```python
from code_atlas.rules import RuleEngine

re = RuleEngine("rules.yaml")
issues = re.evaluate(file_data)
# Returns list of flagged issues with IDs, descriptions, actions
```

## Note-taking, issue reporting and task management

- When you find bugs or other issues you add them to the correct file in `./.work/agent/issues/` by priority, ie. medium issues goes into `./.work/agent/issues/medium.md` etc.
- When you have completed an issue, mark it as done, then move it from the original file into `./.work/agent/issues/history.md`.
- When you feel you need to write something down for later reference, use the `./.work/agent/notes/` folder, and nowhere else.

## Tools

- always use Context7 mcp tool for up to date documentation
- always use Sequential Thinking mcp for help to break tasks into atomic tasks
- always use Memory mcp to keep your context organized
