# Focused Project Template

## Inputs

* **PROJECT_NAME**: *(Your project name)*
* **COVERAGE_TARGET**: *Desired test coverage threshold (e.g. 90)*
* **PY_MIN**: *Minimum Python version (e.g. 3.11)*
* **DOMAIN_DIR**: *Domain (core logic) subpackage (e.g. src/project-slug/domain)*
* **APP_DIRS_IGNORED_FOR_COVERAGE**: *Subpackages to exclude from coverage (e.g. api,cli,web,models,schemas,migrations)*

## Required Tools

The following tools must be available in your development environment:

### Essential Tools

* **Python** (version PY_MIN or higher) - Only for installing uv initially
* **uv** - Universal Python package installer and runner (mandatory for all Python operations)
* **Git** - Version control system
* **GitHub CLI (gh)** - For GitHub operations and automation
* **VS Code** - Recommended editor with extensions:
  - Python extension
  - Pylance (language server)
  - GitHub Copilot (optional but recommended)

### Development Tools

* **pre-commit** - Installed via uv for git hooks
* **Docker** (optional) - For containerized testing and deployment
* **Node.js** (optional) - If building web frontends or using JavaScript tooling

### Installation Order

1. Install Python from python.org
2. Install uv: `python -m pip install --upgrade uv`
3. Install GitHub CLI from cli.github.com
4. Install Git from git-scm.com
5. Install VS Code from code.visualstudio.com
6. From project root: `uv sync` (installs all Python dependencies)
7. Setup pre-commit: `uv run pre-commit install`

**Note**: After initial setup, never use `python` or `pip` directly - always use `uv run python` and `uv` commands.

## Directives

1. **Logic-First Design:** Encapsulate all business logic in DOMAIN_DIR with pure, deterministic functions and classes. **No I/O or external calls in domain code.**

2. **Thin Transport Layers:** API, CLI, UI, etc. should only handle parsing/validation and delegate to domain logic. They perform no business logic.

3. **Dependency Injection via Protocols:** Define abstract interfaces (typing.Protocol) in the domain for all external dependencies (DB, file storage, network clients, etc.). Provide concrete implementations in an adapters/ layer, injected into domain services.

4. **Testing Priority:** Write unit tests targeting domain logic first (using fakes or mocks for interfaces). Add integration tests for real adapters and I/O later, marked and separated.

5. **High Coverage:** Achieve effective coverage ≥ **COVERAGE_TARGET%** on domain and service code. Non-essential boilerplate (e.g. frameworks, data models) can be omitted from coverage.

6. **Unified, OS-agnostic Commands:** Use uv (universal Python package installer) for ALL package management and running of Python code. Never run Python directly except to install uv. This is mandatory - uv handles dependency management, virtual environments, and script execution consistently across platforms.

7. **Automate Quality Gates:** Set up CI to run linting, type-checking, and tests. The build should **fail** if coverage or type checks do not meet the targets.

8. **Prefer CLI Over AI-Agents:** Use straightforward scripts and CLI tools to run checks (formatters, tests, etc.) rather than interactive multi-step AI pipelines (to minimize complexity and token usage).

## Repository Structure

```
.
├─ pyproject.toml
├─ AGENTS.md
├─ .pre-commit-config.yaml
├─ .github/
│  ├─ workflows/ci.yml
│  ├─ prompts/
├─ src/
│  └─ project-slug/       # main package (replace with actual project slug)
│     ├─ domain/          # core business logic (pure code, no I/O)
│     │  ├─ __init__.py
│     │  └─ ... (*.py modules for logic and interfaces)
│     ├─ adapters/        # external implementations (DB, FS, HTTP, etc.)
│     ├─ services/        # orchestration layer, composes domain + adapters
│     ├─ api/             # e.g. FastAPI controllers (no business logic)
│     ├─ cli/             # e.g. Typer command-line interface (no business logic)
│     ├─ web/             # web presentation or UI layer (no business logic)
│     └─ ... (other app-specific layers like models, migrations, etc.)
├─ tests/
│  ├─ unit/              # fast, isolated tests for domain/services
│  ├─ integration/       # tests using real adapters or external systems
│  └─ conftest.py        # shared fixtures and config
├─ .work/
│  ├─ agent/             # temporary agent files (gitignored)
├─ .gitignore            # includes .work/agent/
└─ README.md (and other docs as needed)
```

## Project Documentation Structure

Establish a comprehensive documentation system that separates human-readable documentation from agent working files:

### .gitignore Configuration

Ensure your .gitignore includes:

```gitignore
# Agent working files
.work/agent/
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/
# IDEs
.vscode/settings.json
.idea/
*.swp
*.swo
# Environment
.env
.venv
env/
venv/
temp/
```

## Agent Coding Guidelines

When working with AI coding agents (GitHub Copilot, Claude, etc.), follow these principles to maintain code quality and architectural integrity:

### Agent Responsibilities

* **Respect Architecture**: Always follow the ports and adapters pattern - domain code must remain pure

* **Use uv Exclusively**: Never suggest `pip` or direct `python` commands - always use `uv run` prefix

* **Test-First Approach**: Write unit tests for domain logic before implementing features

* **File Placement**:
  - Production code → appropriate `src/project-slug/` subdirectory
  - Tests → `tests/unit/` or `tests/integration/`
  - Temporary agent files → `.work/agent/notes/`
	  - This includes all summaries, test scripts, fix scripts etc

### Code Generation Standards

* **Type Safety**: Generate fully typed code with proper type hints

* **Protocol Compliance**: Implement interfaces using typing.Protocol for external dependencies

* **Dependency Injection**: Always inject dependencies rather than importing them directly in domain code

* **Error Handling**: Include proper error handling and validation

* **Documentation**: Add docstrings to public functions and classes

### Agent Workflow

1. **Analysis Phase**:

   - Read existing code to understand current architecture

   - Write analysis summary to `.work/agent/notes/analysis-[timestamp].md`

   - Identify which layer the new feature belongs to (domain, service, adapter, transport)

2. **Design Phase**:

   - Create interface definitions (Protocols) if external dependencies are needed

   - Write design summary to appropriate .work/ subfolder

   - Plan test strategy (unit tests for domain, integration tests for adapters)

3. **Implementation Phase**:

   - Implement domain logic first (pure functions/classes)

   - Add service layer orchestration if needed

   - Implement adapters for external dependencies

   - Create transport layer (API/CLI) last

4. **Testing Phase**:

   - Write unit tests using fakes/mocks for domain logic

   - Write integration tests for adapters

   - Ensure coverage meets threshold

   - Create any testing utilities in `.work/agent/scripts/`

5. **Cleanup Phase**:

   - Remove any temporary files created during development

   - Update documentation if architecture changes

   - Verify all agent working files are in `.work/agent/`

### Prohibited Agent Actions

* **Never bypass uv**: Don't suggest pip, python -m, or direct execution

* **No direct imports in domain**: Domain code must not import from adapters or external libraries

* **No I/O in domain**: Domain functions must be pure - no database, file, or network calls

* **No root clutter**: Don't create temporary files in project root

* **No architecture violations**: Respect the layered architecture boundaries

### Agent Communication

* **Explain Decisions**: Always explain why you're placing code in a specific layer

* **Show Dependencies**: Clearly indicate what protocols/interfaces need to be created

* **Test Strategy**: Explain your testing approach (unit vs integration)

* **File Organization**: State where you're placing files and why

## Coding Rules

* **Single Responsibility:** One purpose per module or class. Keep functions small and focused.

* **Pure Domain Functions:** In domain/, functions and methods should be deterministic and free of side-effects. No database calls, no HTTP requests, no file access, no OS calls in this layer.

* **External via Interfaces:** Represent external systems (databases, file storage, APIs, etc.) with Protocol interfaces defined in the domain. Pass concrete implementations (adapters) into domain logic (via constructor or function parameters). This allows swapping them out in tests.

* **Strict Boundaries:** Domain code never imports from adapters or frameworks. The dependency direction is **inward**: adapters know about domain interfaces, but domain is oblivious to who implements its interfaces.

* **Type Safety:** All public functions and methods should have type hints. Avoid using Any for domain logic inputs/outputs. Use dataclasses or pydantic models for structured data if needed, but keep domain logic type-consistent.

* **Side Effects Isolation:** Any operation with side effects (database writes, file I/O, network calls, randomness, time, etc.) should be done in adapter implementations behind a Protocol. This makes domain logic easily testable and predictable.

## Ports and Adapters for I/O

Keep a clear **ports and adapters** structure (Hexagonal Architecture). Define Protocols in the domain for any external dependency, implement them in the adapters layer, and inject into services. This decouples core logic from infrastructure:

```python
# filename: src/project-slug/domain/ports.py
from typing import Protocol, runtime_checkable, Iterable, BinaryIO

@runtime_checkable
class UnitOfWork(Protocol):
    """Transaction boundary (for DB transactions)."""

    def __enter__(self): ...

    def __exit__(self, exc_type, exc, tb): ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
    
@runtime_checkable
class UserRepo(Protocol):
    """Abstract repository for Users."""

    def get(self, user_id: int) -> dict: ...

    def list(self) -> Iterable[dict]: ...

    def save(self, user: dict) -> None: ...

@runtime_checkable
class FileStore(Protocol):
    """Abstract file storage (e.g. for user uploads)."""

    def put(self, key: str, data: BinaryIO, *, content_type: str | None = None) -> str: ...

    def get(self, key: str) -> BinaryIO: ...

    def delete(self, key: str) -> None: ...

@runtime_checkable
class Clock(Protocol):
    """Abstract clock to get current time (for timestamps, scheduling, etc.)."""

    def now(self): ...
```

**Services** in the services/ layer orchestrate domain logic with these ports:
```python
# filename: src/project-slug/services/user_photos.py
from project_slug.domain.ports import UserRepo, FileStore, UnitOfWork, Clock

class UserPhotosService:
    """Service handling user profile photo uploads."""

    def __init__(self, repo: UserRepo, fs: FileStore, uow: UnitOfWork, clock: Clock):
        self.repo = repo
        self.fs = fs
        self.uow = uow
        self.clock = clock
        
    def upload_avatar(self, user_id: int, image_stream, content_type: str) -> str:
        # 1. Retrieve domain entity (user)
        user = self.repo.get(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        # 2. Generate unique storage key (e.g., using current timestamp)
        timestamp = int(self.clock.now().timestamp())
        key = f"avatars/{user_id}-{timestamp}"
        # 3. Store the image via file storage adapter, get returned URL/path
        url = self.fs.put(key, image_stream, content_type=content_type)
        # 4. Save the updated user record with new avatar URL within a transactional UoW
        with self.uow:
            user["avatar_url"] = url
            self.repo.save(user)       # stage update
            self.uow.commit()          # commit transaction if no errors
        # 5. Return the location of the stored avatar
        return url
```

**Adapters** implement these interfaces in the adapters/ layer, using specific technologies (e.g. SQLAlchemy, boto3, etc.):

* *Database Example:* A SqlAlchemyUserRepo class in src/project-slug/adapters/db/ implements UserRepo using SQLAlchemy models, and a SqlAlchemyUoW implements UnitOfWork (managing session/transactions).

* *File Storage Example:* An S3FileStore in src/project-slug/adapters/fs/ implements FileStore using Boto3 to put/get files in an S3 bucket (or a local filesystem adapter for dev/testing).

* *Time Example:* A SystemClock in src/project-slug/adapters/time/ implements Clock by returning datetime.now(). In tests, a fake clock can return fixed times.

```python
# filename: src/project-slug/adapters/db/sqlalchemy_repo.py
from sqlalchemy.orm import Session
from project_slug.domain.ports import UserRepo, UnitOfWork

class SqlAlchemyUoW(UnitOfWork):

    def __init__(self, session: Session):
        self.session = session
    def __enter__(self):
        return self  # Begin transaction scope (session already begun)
    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.session.rollback()  # rollback on error
        # else, commit will be called explicitly
    def commit(self):
        self.session.commit()
    def rollback(self):
        self.session.rollback()
        
class SqlAlchemyUserRepo(UserRepo):

    def __init__(self, session: Session):
        self.session = session
    def get(self, user_id: int) -> dict:
        obj = self.session.query(UserModel).get(user_id)
        return obj.to_dict() if obj else None
    def list(self):
        return [obj.to_dict() for obj in self.session.query(UserModel).all()]
    def save(self, user: dict) -> None:
        ...  # convert dict to ORM object and add to session
```

💡 *Wiring:* *In your application startup (e.g. FastAPI dependency or CLI factory), instantiate these adapters and pass them into the service.* For example:

```python
# filename: src/project-slug/api/dependencies.py
from project_slug.adapters.db.sqlalchemy_repo import SqlAlchemyUserRepo, SqlAlchemyUoW
from project_slug.adapters.fs.s3_store import S3FileStore
from project_slug.adapters.time.system_clock import SystemClock
from project_slug.services.user_photos import UserPhotosService

def get_user_photos_service() -> UserPhotosService:
    session = create_sqlalchemy_session()  # function to get a DB session
    return UserPhotosService(
        repo=SqlAlchemyUserRepo(session),
        fs=S3FileStore(bucket="my-app-bucket"),
        uow=SqlAlchemyUoW(session),
        clock=SystemClock(),
    )
```

This approach ensures that **all I/O (DB, file, network)** is confined to adapter classes. The domain and services operate against abstract interfaces, making them easy to test in isolation.

## Testing Strategy

Testing is split into phases to ensure fast feedback for logic and thorough coverage for integrations:

* **Unit Tests (Phase 1):** Located in tests/unit/. These target domain and service logic with **fake or stub implementations** of dependencies. Fakes implement the same Protocols (ports) but use in-memory or simplistic logic. This allows testing core functionality without any external I/O. Unit tests should be fast, deterministic, and cover edge cases of business logic. Mark pure logic tests with a custom marker (e.g. @pytest.mark.logic) for easy selection.

* **Integration Tests (Phase 2):** Located in tests/integration/. These tests use real adapter implementations and external resources (or a close simulation) to ensure the system works end-to-end. Use fixtures to provide real implementations (e.g. a temporary database or a test container, a local S3 emulator or temp directory, etc.). Mark these with @pytest.mark.integration so they can be run separately (since they may be slower or require additional setup). Integration tests can re-use or duplicate some unit test scenarios to verify that actual adapters fulfill the contracts defined by the domain interfaces (this acts as **contract testing** for adapters).

* **End-to-End or System Tests (Phase 3, optional):** If applicable, you might have separate end-to-end tests (e.g. using Playwright for a web UI, or calling the running API service). These should also be marked (e.g. @pytest.mark.e2e or @pytest.mark.slow) and kept separate from unit tests.

**Testing Best Practices:**

* **Isolate Side Effects:** In unit tests, replace any external interaction with fakes or mocks. For example, use an in-memory fake repository or file store, and a fake clock that returns a fixed time, to test logic deterministically.

* **No External Calls in Tests:** Unit tests should not call real databases, web services, or file systems. Use dependency injection to supply test doubles.

* **Mark and Skip as Needed:** Use pytest markers to categorize tests. In CI, you might run all tests by default, but allow skipping integration or e2e tests locally for speed. Configure pytest.ini to treat unknown markers as errors (to avoid typos).

* **Fast Feedback:** Aim for unit tests to run in seconds. Integration tests can run separately (or in parallel) since they may take longer due to I/O (consider using Pytest xdist or separate CI jobs for integration).

## Example: Unit Test with Fakes

Below is an example unit test for the UserPhotosService.upload_avatar logic using fake dependencies. This test ensures that when an avatar image is uploaded, the service stores the file and updates the user record properly, **without touching any real database or file storage**:

```python
# filename: tests/unit/test_user_photos.py
import io
import pytest
from project_slug.services.user_photos import UserPhotosService
from project_slug.domain.ports import UserRepo, FileStore, UnitOfWork, Clock
# Fake implementations of the ports for testing

class FakeRepo(UserRepo):

    def __init__(self):
        # In-memory "database" of users
        self.store = {1: {"id": 1, "name": "Ada"}}
        
    def get(self, user_id: int) -> dict:
        return self.store.get(user_id)
        
    def list(self):
        return self.store.values()
    
    def save(self, user: dict) -> None:
        # Update the in-memory record
        self.store[user["id"]] = user
        
class FakeFileStore(FileStore):

    def __init__(self):
        self.storage = {}  # dict to hold file data by key (for verification if needed)
    
    def put(self, key: str, data: io.BytesIO, *, content_type=None) -> str:
        # Simulate storing file and return a dummy URL/path
        self.storage[key] = data.read()
        return f"mem://{key}"
    
    def get(self, key: str) -> io.BytesIO:
        return io.BytesIO(self.storage[key])
    
    def delete(self, key: str) -> None:
        self.storage.pop(key, None)
        
class FakeUoW(UnitOfWork):

    def __enter__(self):
        return self  # nothing special for begin
    
    def __exit__(self, exc_type, exc, tb):
        # For testing, we don't simulate transactions, just no-op
        return False
    
    def commit(self):
        pass
    
    def rollback(self):
        pass

class FixedClock(Clock):

    def now(self):
        from datetime import datetime, timezone
        # Return a fixed datetime for predictability
        return datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
@pytest.mark.logic
def test_upload_avatar_updates_user_and_returns_url():
    svc = UserPhotosService(repo=FakeRepo(), fs=FakeFileStore(), uow=FakeUoW(), clock=FixedClock())
    image_data = io.BytesIO(b"fake-image-bytes")
    url = svc.upload_avatar(user_id=1, image_stream=image_data, content_type="image/jpeg")
    # The returned URL should be a memory path with correct key format
    assert url.startswith("mem://avatars/1-")
    # After upload, the user's avatar_url should be updated in the fake repo
    updated_user = svc.repo.get(1)
    assert updated_user is not None
    assert "avatar_url" in updated_user and updated_user["avatar_url"] == url
```

In this test, FakeRepo and FakeFileStore simulate the database and file storage, FakeUoW simulates a transaction context (but just does nothing), and FixedClock provides a constant timestamp. This allows the service logic to be tested in complete isolation.

## Example: Integration Test with Real Adapters

Once the real adapters (for database, file storage, etc.) are implemented, an integration test can verify they work with the service. For example, if sql_repo is a fixture that provides a real SqlAlchemyUserRepo connected to a test database, an integration test might look like:

```python
# filename: tests/integration/test_user_repo_adapter.py
import pytest
from project_slug.adapters.db.sqlalchemy_repo import SqlAlchemyUserRepo

pytestmark = pytest.mark.integration  # mark the whole module as integration tests

def test_user_repo_fetches_user(sql_repo: SqlAlchemyUserRepo):
    # Assume sql_repo is a fixture returning a SqlAlchemyUserRepo with a test DB
    user = sql_repo.get(user_id=1)
    assert user is not None
    assert user["id"] == 1
    assert "first" in user or "name" in user  # depending on how the UserModel is defined
```

In integration tests, you might use a temporary or in-memory database (for example, SQLite in-memory for SQLAlchemy, or a Dockerized database started in CI), and possibly a local filesystem or S3 emulator for file storage. These tests ensure that your adapters meet the contract and work in a real scenario. They are slower and more brittle than unit tests, so keep them separate and fewer in number—focus on critical integration points.

*(Advanced:* For complex projects, consider **contract tests** where you run the same test cases against both fakes and real adapters to ensure the behavior is consistent. Also, tools like **Testcontainers** can help spin up real dependencies for integration tests on the fly.)\*

## PyProject Configuration (Tools & Coverage)

Configure your pyproject.toml to enforce testing and style rules. Below is an example snippet integrating **Pytest**, **Coverage**, **Ruff**, and **MyPy**:

```toml
# filename: pyproject.toml
[project]
name = "PROJECT_NAME"
requires-python = ">=PY_MIN"
# ... other project metadata ...

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = [
  "logic: unit tests of pure logic (domain/services)",
  "integration: tests involving real I/O or external systems",
]

addopts = """
  -q
  --strict-markers
  --disable-warnings
  --cov=src
  --cov-report=term-missing
  --cov-report=html
  --cov-fail-under={COVERAGE_TARGET}
"""

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
  "*/__main__.py",
  "*/tests/*",
  "*/({APP_DIRS_IGNORED_FOR_COVERAGE})/*",
]

[tool.coverage.report]
# Exclude boilerplate or defensive code from coverage
exclude_lines = [
  "pragma: no cover",
  "if __name__ == .__main__.:",
  "raise NotImplementedError",
  "if 0:",  # used for debugging
]

[tool.ruff]
target-version = "py311"  # or match PY_MIN if higher
line-length = 100
select = ["E", "F", "I", "B", "C4", "UP", "DTZ", "PYI"]  # Example: errors, code style, etc.
ignore = ["E501"]  # allow long lines if needed (since we set line-length separately)

[tool.mypy]
python_version = "PY_MIN"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
disallow_untyped_defs = true
# Exclude test files or specific modules that are hard to type-check
exclude = ["tests/"]
```

**Notes:**

* Pytest options enforce a coverage report (term and HTML) and will fail if coverage is below the threshold.

* We define custom markers logic and integration for test categorization.

* Coverage omit excludes tests, migrations, and specified app layers from coverage calculation to focus on core logic.

* Ruff is configured as both linter and formatter (so you might not need Black/isort separately). The select codes above are an example; adjust to your preferred lint rules. (You can also use ruff \--fix or ruff format as a code formatter.)

* MyPy is set to strict mode on the source package. You might need to tweak settings or add ignore\_missing\_imports for certain third-party libraries in a real project.

## Pre-commit Hooks

Use *pre-commit* to run linters and type checks before each commit, ensuring code quality is maintained. For example, a .pre-commit-config.yaml:

```yaml
# filename: .pre-commit-config.yaml
repos:
- repo: https://github.com/charliermarsh/ruff-pre-commit
  rev: "v0.RuffVersion"  # specify latest ruff version
  hooks:
    - id: ruff
      args: ["--fix"]     # autofix lint issues (including formatting)
    - id: ruff # run ruff again to ensure no issues remain
      name: ruff (lint)
      args: ["--exit-zero"]  # do not fail (to avoid double failure; first hook already fixes)
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: "v1.LatestMypyVersion"
  hooks:
    - id: mypy
      args: ["--strict", "src/"]
```

*(Adjust versions to the latest release numbers. You can also add other hooks like pytest for running tests, or black if you still use it.)*

With this config, running pre-commit install will set up git hooks that automatically format code with Ruff and check types with MyPy on each commit. This prevents bad code from slipping in.

## CI Pipeline (GitHub Actions Example)

Set up continuous integration to run tests, lint, and type-check on every push/PR. For example, a GitHub Actions workflow file at .github/workflows/ci.yml:

```yaml
# filename: .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "${{ matrix.python-version }}"
        strategy:
          matrix:
            python-version: [ PY_MIN ]  # you can test multiple versions if needed
      - name: Install dependencies
        run: |
          python -m pip install -U uv
          uv sync  # install all dependencies in isolated environment
      - name: Lint (Ruff)
        run: uv run ruff check .
      - name: Type Check (MyPy)
        run: uv run mypy src
      - name: Run Tests (with Coverage)
        run: uv run pytest
      # Optionally, you can add steps to upload coverage reports or test artifacts
```

**Key points:**

* The workflow installs the project in editable mode with dev dependencies (.\[dev\] which should include test tools like pytest, coverage, ruff, mypy, etc.).

* It runs Ruff for linting, MyPy for type checking (skipped if TYPECHECK env var is 'off'), and Pytest for running tests. Pytest configuration (from pyproject.toml) will handle coverage reporting and threshold.

* We use uv if available to ensure a consistent virtualenv environment (this is optional; it's a convenience tool—if you're not using uv, the commands still work with normal pip and direct calls).

* CI should fail if any of these steps fail (lint errors, type errors, tests failing, or coverage below target).

You can extend this workflow with additional jobs (for example, test on multiple Python versions, build docs, etc.) as needed.

## Development Commands

Common commands for development and continuous integration:

* **Install dependencies:** `uv sync` (installs all dependencies in an isolated environment).

* **Run all tests:** `uv run pytest` (runs all tests; uses markers and config as defined).

* **Run only logic unit tests:** `uv run pytest -m logic -q` (quick run of domain/service tests).

* **Run only integration tests:** `uv run pytest -m integration -q` (will run tests marked as integration).

* **Generate coverage report:** `uv run pytest --cov --cov-report=term-missing --cov-report=html` (and then open htmlcov/index.html for details).

* **Lint code:** `uv run ruff check .` (add `--fix` to auto-fix issues or use `uv run ruff format .` to apply formatting).

* **Type-check code:** `uv run mypy src`.

* **Format code:** `uv run ruff format .` (Ruff can auto-format; alternatively use Black if configured).

* **Pre-commit all files:** `uv run pre-commit run --all-files` (to manually run hooks on the entire repo).

* **Full quality check (if using build script):** `uv run python build.py` (runs format, lint, tests, coverage, etc. in one go). Adjust according to your build script name.

Having a single **build script** (like the provided build.py) or a Makefile alternative can help to consistently run all checks with one command. Ensure any such script also enforces the coverage threshold and other quality gates, similar to CI.

## Retrofit Plan for Existing Projects

If you are applying this structure to an **existing project**, follow these steps:

1. **Create domain/ Core:** Identify all business logic (pure computation, algorithms, validations, calculations, etc.) and move it into DOMAIN_DIR (e.g. src/project-slug/domain). Remove or abstract out any direct external calls from this code.

2. **Define Ports (Protocols):** For each external dependency the domain logic used (e.g. database access, HTTP calls, file access, current time, random IDs), define a Protocol in domain/ports.py. This acts as an interface that the domain will depend on.

3. **Implement Adapters:** In a new adapters/ package, implement the protocols using the actual libraries or frameworks. E.g., if the domain has UserRepo interface, implement SQLUserRepo in adapters/db.py (or a subpackage) using your ORM. Similarly, for file storage or others.

4. **Introduce Services Layer:** Create services in services/ that orchestrate the domain logic and use the adapters. The services should receive the needed ports (via constructor or method parameters). Move any business workflows out of your Flask/FastAPI views or CLI commands into these services.

5. **Refactor Entry Points:** Update your API endpoints, CLI commands, and other entry points to use the new services. They should now mostly parse input, call a service method, and format output. This keeps them thin.

6. **Rework Tests:** Move unit tests to tests/unit. For logic tests, use fake implementations of the interfaces (you can create simple in-memory fakes for database or external services). Ensure these tests cover the domain logic thoroughly. Mark them with @pytest.mark.logic. Move any tests that actually hit the database or network into tests/integration and mark with @pytest.mark.integration.

7. **Configure Tooling:** Adopt the pyproject.toml settings for pytest, coverage, etc. as above. Set a reasonable initial `--cov-fail-under` (maybe start lower like your current coverage or slightly above). Integrate Ruff and MyPy gradually if not already. Run pre-commit on the codebase to auto-fix lint issues.

8. **Set Up CI:** Add a GitHub Actions workflow (or your CI of choice configuration) similar to the above to automate tests and checks on each push. This will enforce the new structure and quality goals.

9. **Custom Copilot Instructions:** Create or update the .github/copilot-instructions.md file to explain the project structure to AI coding assistants (and new developers). For example, instruct that *"All business logic goes in src/project-slug/domain, do not access the database or filesystem from domain code"*, *"Always use dependency injection for external services"*, *"Use uv for all Python package management and execution"* etc. This ensures AI suggestions align with your architecture (if using GitHub Copilot or similar).

10. **Incremental Improvement:** If coverage is below target, progressively write more tests for domain logic. You can enforce a rising threshold (e.g. increase `--cov-fail-under` by a few percent with each PR until you reach the goal range). Similarly, address lint and type-check issues over time, aiming for a clean report.

Throughout the retrofit, run the test suite frequently to catch any breakage. Refactoring to this pattern can be done module by module—start with one part of the logic, abstract its external calls, inject dependencies, write tests, and then move to the next.

## Conventions & Best Practices

* Use `# pragma: no cover` to exclude code that is intentionally not covered (for example, defensive branches that should never execute, or CLI boilerplate).

* Write tests for both expected cases and edge cases. Each unit test should focus on one behavior and use **assertions** to validate outcomes. Name test functions clearly (e.g. `test_upload_avatar_updates_url()`).

* Limit one logical assertion per test (helps isolate failures). Use parametrization for multiple scenarios of the same behavior rather than one test doing many things.

* Keep functions and methods short. If a function is more than ~50 lines or does too many things, consider refactoring it into smaller pieces or moving logic into the domain layer.

* **No hidden state:** Avoid global state or singletons that can make testing hard. If using any global config or objects (like a database connection), access them via dependency injection or at least isolate their usage in adapter layer.

* Domain models (entities) can be simple (dict, dataclass, or Pydantic BaseModel) depending on your needs, but they should be free of persistence concerns. The repository adapters handle conversion between domain models and database records.

* Ensure **domain does not import from service or adapter layers**. The import hierarchy should be: **domain** <- **services** <- **adapters** <- **transport/UI**. Violation of this typically indicates a layering problem.

* Document the design for contributors: explain where to add new logic or new integrations (e.g. "to add a new external API integration, create a Protocol for it, then implement an adapter, and inject it into the relevant service").

## Acceptance Criteria

Use the following as a checklist to know if the project setup is successful:

* **Tests:** All tests (pytest) pass locally and in CI. Domain logic has **≥ COVERAGE_TARGET%** coverage. Integration tests can be run optionally and pass against real dependencies (or are skipped if environment not available).

* **Linting & Type Checking:** Codebase passes Ruff linting (after auto-fixes) and MyPy type checks (if type checking is enabled). No unused ignore comments or type errors remain.

* **Isolated Domains:** No file in src/project-slug/domain imports from src/project-slug/adapters or any external library that performs I/O. Domain code is truly decoupled.

* **CI Pipeline:** The GitHub Actions (or equivalent CI) workflow runs on each push/PR and fails on any test, lint, or type errors, or if coverage drops below threshold. This prevents regressions.

* **Pre-commit Hooks:** Contributors have pre-commit set up so that formatting and linting are automatically run on commit (reducing noise in code review).

* **Developer UX:** Running `uv run python build.py` (or the equivalent all-in-one command) locally should format the code, check types, run all tests, and report coverage. Developers can easily test and verify the quality before pushing changes.

* **Documentation:** The repository has a clear README or developer guide (and possibly a docs/ site) that outlines how to set up, run, and test the project, including the architectural principles (so new team members or AI assistants can quickly understand the approach).

* **Extensibility:** Adding a new feature should follow the same pattern: write logic in domain -> define new Protocol if an external call is needed -> implement adapter -> use in a service -> write unit tests for logic -> write integration tests for adapter. If the team (or Copilot) can do this easily, the architecture is working as intended.

By following this template, your Python project will encourage **separation of concerns**, be **easier to test**, and maintain a **high level of code quality** through automated checks. This upfront discipline pays off with faster development in the long run, as features can be added or changed with confidence in the test suite and clear project structure. Good luck with your project!

---