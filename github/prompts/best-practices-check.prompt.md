---
title: Best Practices for Large Python Projects
description: Engineering reference for maintaining high code quality in large Python projects.
tags: [engineering, best-practices, python, code-quality]
---

# Best Practices for Large Python Projects

This document provides an **engineering reference** for maintaining high code quality in large Python projects. It covers key aspects such as code style, design principles, testing, architecture, documentation, and tooling. The goal is to ensure that a codebase remains **readable, maintainable, and scalable** as it grows. Use this as a guide for code reviews and when developing new features.

## Instructions

- Use the following document to analyze the current codebase.
- Identify areas for improvement based on the best practices outlined.
- All findings should be appended to the `.work/agent/issues/<priority>.md` file, with type set to "enhancement" and priority "medium".
- Provide specific recommendations and examples for refactoring or enhancing the code.
- Ignore these folders:
  - `tests/`
  - `.github/`
  - `docs/`
  - `scripts/`
  - `migrations/`
  - `.work/`
- Focus on these folders:
  - `src/` (or equivalent main source folder or specified by the user)
  - `pyproject.toml`
  - `setup.py`
  - `build.py`
- **NEVER** import directly from the `src` folder, like `from src.package import X`

- The appended items should each have this format:

```markdown
---
id: "ENHANCE-001"
title: "Enhancement title"
description: "Short summary of the enhancement"
created: 2025-10-09
section: what part of the project or solution does this relate to
tags: extracted tags
type: enhancement
priority: critical | high | medium | low
references: any relevant references, links, documentation, research, inspiration, etc.
status: proposed | in progress | completed | won't fix | recommended | blocked
---

A detailed description of the enhancement, why this is important, how it can be implemented, and any other relevant information to ensure a clear understanding of the enhancement's purpose and requirements.
```

## Key Aspects of Code Quality

When evaluating a Python codebase, consider the following core criteria:

* **Readability & Style:** Code should follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines with clear naming conventions. It should be easy to understand at a glance.

* **Design Principles:** The design should avoid needless complexity. Follow principles like DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid), and SOLID (e.g. Single Responsibility, Dependency Inversion) to produce clean, modular code.

* **Architecture:** The project structure should be modular with a clear separation of concerns (e.g. layers for logic vs. UI). Ideally, follow a layered or hexagonal architecture for scalability.

* **Testing & Quality Assurance:** There should be a robust test suite (unit tests for core logic, integration tests for components working together). Aim for high coverage and easy testability.

* **Documentation:** Public functions/classes have docstrings (preferably in a standard format like Google or NumPy style). There should be a clear README and possibly a docs site explaining usage and development setup.

* **Security & Performance:** No sensitive data is hardcoded; configuration is handled securely. The code uses efficient algorithms/data structures and avoids performance pitfalls. Profiling and optimization are considered for critical paths.

* **Tooling & Automation:** Utilize linters (like Ruff or Flake8) and formatters (Black) to maintain consistency. A continuous integration (CI) pipeline should automate tests and checks on each commit. Deployment or release processes should also be automated (for example, publishing to PyPI via CI).

Each of these areas is detailed in the sections below, with best practices and recommendations.

## 1. Code Style and Readability

**Consistency and clarity** in code style make a huge difference in maintainability:

* **PEP 8 Compliance:** Adhere to the official Python style guide, PEP 8, for basic formatting (indentation, spacing, line breaks, etc.). Automated tools like **Black** (for formatting) and **Ruff** or **Flake8** (for linting) can enforce these conventions.

* **Naming Conventions:** Use descriptive, unambiguous names for variables, functions, classes, etc. Follow conventions (e.g. snake_case for functions/variables, CamelCase for classes). Avoid single-letter names except in very short scopes (like loop indices).

* **Line Length:** Decide on a maximum line length and enforce it. Common choices are 88 (Black's default) or 100-120 characters. Consistently wrapping lines improves readability on smaller screens and side-by-side diffs.

* **Spacing and Formatting:** Keep code visually clean. Insert blank lines between logical sections of code, around class and function definitions, etc. Avoid trailing whitespace and ensure files end with a newline. Automated formatters will handle most of this.

* **Imports Ordering:** Organize imports into groups (standard library, third-party, local) and sort them alphabetically. Tools like **isort** (or Ruff's import sorting) can do this automatically.

* **OS Agnosticism (Portability):** Write code that runs consistently on Linux, Mac, or Windows. Use pathlib.Path for file paths instead of hardcoding directory separators. Avoid OS-specific shell commands when a Python library can abstract it. If cross-platform support is needed, test the code on multiple environments.

By maintaining a consistent style and paying attention to naming and structure, you make the codebase approachable for any developer or AI agent reading it.

## 2. Core Design Principles

Large projects benefit from well-established design principles that keep the codebase organized and flexible:

* **Small, Focused Functions:** Aim for functions to do one thing and do it well. If a function exceeds \~5-15 lines of code (excluding docstrings/comments) or is handling multiple tasks, consider refactoring it into smaller functions. Small functions are easier to understand, test, and reuse.

* **Single Responsibility Principle (SRP):** Each module, class, or function should have one reason to change. In practice, this means grouping related logic together and not mixing concerns. For example, a function that calculates a result shouldn’t also handle file I/O or user input.

* **Don’t Repeat Yourself (DRY):** Avoid duplicating code or logic. If you notice similar code in multiple places, refactor it into a common function or utility. This reduces bugs and makes maintenance easier (fixing an issue in one place fixes it everywhere).

* **Keep It Simple, Stupid (KISS):** Simplicity is key. Do not over-engineer a solution when a straightforward approach works. Clever or complex code can be difficult to understand and error-prone. If you must implement complex logic (due to requirements), make sure to document it clearly (e.g., in comments or docstrings).

* **You Aren’t Gonna Need It (YAGNI):** Don’t add functionality until it’s necessary. Avoid building features or hooks for future scenarios that may not happen – this adds complexity without immediate benefit.

* **SOLID Principles:**

* *Open/Closed Principle:* Code should be open to extension (you can add new functionality without modifying existing code) but closed to modification (modifying existing, working code can introduce bugs). Achieve this through abstractions: e.g., define interfaces or base classes that can be extended with new implementations.

* *Liskov Substitution Principle:* Subclasses or derived classes should be substitutable for their base class without affecting the correctness of the program. In Python terms, any class that implements an interface (or duck-types a certain behavior) should honor the expectations (no surprising side-effects or constraints).

* *Interface Segregation Principle:* Don’t force one class to implement methods it doesn't use. It's better to have smaller, specific interfaces (or abstract base classes / protocols) than one large interface. In Python, this could mean multiple small protocols or base classes rather than one giant class with many responsibilities.

* *Dependency Inversion Principle:* High-level modules should not depend on low-level modules directly; both should depend on abstractions. In practice, this often means using dependency injection (see below) and defining abstract interfaces for key functionalities, so implementations can be swapped without changing the code that uses them.

* **Separation of Concerns:** Clearly separate different concerns of the application. For example, business logic, data access, and presentation (UI/CLI) should reside in different modules or layers. This makes the system easier to understand and modify.
  * *Thin UI Layer:* Keep user interface code (CLI commands, web routes, GUI code) as simple as possible—just parsing input and formatting output. Move complex logic out of the UI and into core modules or services. This not only makes it more testable (you can test the logic without the UI) but also avoids duplication if you have multiple interfaces.
  * *Decouple I/O from Logic:* Similarly, separate code that interacts with external systems (files, databases, network) from pure computation logic. This way, the pure logic can be reused and tested in isolation, and the I/O parts can be handled in one place (with error handling, logging, etc.).

By following these principles, the codebase will be easier to extend and maintain. New features can often be added by extending classes or writing new ones, rather than modifying a lot of existing code.

### Dependency Injection and Decoupling

A specific technique to achieve decoupling is **Dependency Injection (DI)**, which means that instead of hard-coding dependencies, you **inject** them into classes or functions:

* **What and Why:** If a class or function relies on an external component (database, API client, logger, etc.), do not instantiate that component inside the class/function. Instead, accept it as a parameter (either in the constructor or the function arguments). This allows you to pass in different implementations for different scenarios (for example, a fake or mock for testing, or an alternative implementation in the future) without changing the dependent code.

* **Use Abstractions:** Define an abstract base class or a typing.Protocol for the dependency’s interface. The high-level code should depend on this abstract interface, not a concrete implementation. The concrete implementations (e.g., a real database class, a file-based class, etc.) will implement the interface. This is the "dependency inversion" part of SOLID.

* **Benefits:** DI greatly improves **testability** (you can inject a dummy dependency in tests), **flexibility** (swap out implementations easily), and **modularity** (low-level modules aren’t tightly coupled to high-level logic).

* **Example:**

```python
from typing import Protocol, List

class DataReader(Protocol):
    def read_items(self) -> List[str]:
        ...

class DatabaseReader:
    def read_items(self) -> List[str]:
        # ... e.g., query a database ...
        return ["item from DB"]

class FileReader:
    def __init__(self, path: str):
        self.path = path
    def read_items(self) -> List[str]:
        # ... read from a file ...
        return ["item from file"]

class DataProcessor:
    def __init__(self, reader: DataReader):
        self.reader = reader
    def process_all(self):
        items = self.reader.read_items()
        # ... process the items ...
        print("Processing", items)

# Usage:
processor1 = DataProcessor(reader=DatabaseReader())        # injecting a database dependency
processor2 = DataProcessor(reader=FileReader("data.txt"))  # injecting a file dependency

processor1.process_all()  # works with database
processor2.process_all()  # works with file
```

* In this example, DataProcessor doesn’t know or care where data comes from. We can inject a different reader without changing DataProcessor. This makes testing easy (we could create a FakeReader that returns a known list of items for a test).

* **Frameworks:** You typically don't need a special library for DI in Python; simple patterns like above suffice. However, there are libraries (like dependency_injector) if you need more structure for larger applications.

### Modularity and Architecture

Structuring a large project well is as important as writing good code inside each module:

* **High Cohesion, Low Coupling:** Aim for modules that group related functionality (high cohesion) and minimize how much they depend on other modules (low coupling). For instance, a database module might contain all data access code, and it provides a clean interface to the rest of the app. Other parts of the app don't need to know details of how it works, they just call its interface.

* **Layered Architecture:** Consider separating the project into layers, such as:

* *UI Layer:* CLI or API endpoints, just marshaling input/output.

* *Service/Logic Layer:* Core business logic, rules, calculations.

* *Data Layer:* Interactions with databases, file system, external APIs.

Each layer only interacts with the layer below it (the UI calls the service layer, which calls the data layer). This makes it easier to change one layer (e.g., swap a database) without rewriting the others, as long as the interfaces remain consistent. \- **“Clean Architecture” or Hexagonal Architecture:** These are advanced patterns that enforce a strong separation of concerns. The idea is that the core logic is independent of frameworks or external systems. For example, your core logic doesn’t depend on Django or FastAPI or a specific database. Instead, those are plugged in at the boundaries. If you adhere to this, testing and modifying the system becomes much easier. \- **Stateless Design (when possible):** Unless your application inherently requires state (like a game or certain types of servers), design components to be stateless. Stateless services (pure functions or classes that don’t hold global state) are easier to scale and debug. When state is needed (e.g., caching, user sessions), keep it well-contained and managed explicitly.

By designing a solid architecture early on, you prevent a lot of pain as the codebase grows. Adding features or swapping out technology is straightforward when the code is organized and follows these guidelines.

## 3. Testing and Quality Assurance

A strong test suite is the backbone of a maintainable project. It gives you confidence to refactor and extend code without breaking existing functionality.

* **Unit Tests:** Write unit tests for all critical logic. Each function or class method (that contains non-trivial logic) should have corresponding tests covering typical cases and edge cases. Use **pytest** for a clean and powerful testing experience. Tests should run quickly and not depend on external services or state (use mocks or stubs for database calls, network requests, etc. in unit tests).

* **Integration Tests:** In addition to unit tests, have some integration tests that cover the interaction between components. For example, if your project has a web API, write tests that start the server (maybe in a test mode) and call the API endpoints, verifying the end-to-end behavior (these might involve a test database or other resources). Integration tests are usually fewer and slower than unit tests, but they catch issues with how parts of the system work together.

* **Test Coverage:** Aim for a high coverage percentage (commonly, 70% or more of lines executed by tests). Coverage tools (like pytest-cov with Coverage.py) can report how much of your code is exercised by tests. Be cautious though: 100% coverage doesn’t guarantee bug-free code, but low coverage definitely means parts of your codebase are untested and likely to hide bugs. Focus on covering the core logic and any complex or critical sections of code.

* **Testability:** Design your code with testing in mind:

* Functions that return results are easier to test than ones that print or interactively ask for input.

* If a function does I/O (reads/writes files, calls an API), structure it so that the I/O part can be isolated or overridden in tests. (For example, have a function that takes a filename and returns data – in tests, you could point it to a temp file or monkeypatch a file reading function.)

* Use dependency injection (as above) to insert mock objects during tests.

* **Continuous Testing:** Automate running tests using a CI pipeline (more on this later). Every push or pull request should trigger the test suite so you catch failures early. It’s much easier to fix a bug right when you introduced it, rather than weeks later after more code has been written on top of it.

* **Use Fixtures and Factories:** With pytest, leverage fixtures to set up common test preconditions (e.g., sample data, temp directories) and use factory libraries (like Factory Boy) or simple helper functions to create test objects. This reduces duplication in your tests (don’t Repeat Yourself applies to tests too).

* **Behavior-Driven or Test-Driven Development (optional):** Depending on the team preference, you can adopt BDD or TDD practices. BDD (Behavior-Driven Development) involves writing tests in a more natural language style (possibly using a framework like pytest-bdd or behave) focusing on user stories. TDD (Test-Driven Development) involves writing tests before the implementation. While not mandatory, these practices can lead to better-designed, well-tested code if done consistently.

**Example:** To run tests with coverage and ensure a minimum coverage threshold (e.g., 75%), you could use a command like:

```bash
uv run pytest -vv --cov=src/your_package --cov-report=term --cov-fail-under=75
```

This will run tests verbosely, show a coverage report in the terminal, and exit with an error if coverage is below 75%. In a CI environment, that would fail the build, ensuring that test coverage doesn't drop over time.

## 4. Documentation

Well-documented code and project resources are crucial for onboarding new contributors (and helping your future self):

* **Docstrings:** Every public module, function, class, and method should have a docstring describing what it does, its arguments, return value, and any exceptions it might raise. Adopting a consistent style like **Google style docstrings** (as shown below) or NumPy style makes them easy to read and parse by documentation tools.

  *Example of a Google-style docstring:*

```python
def add_user(username: str, is_admin: bool = False) -> bool:
    """Add a new user to the system.

    Args:
        username: The username of the new account.
        is_admin: Whether the new user should have admin privileges. Defaults to False.

    Returns:
        True if the user was added successfully, False if the username already exists.

    Raises:
        ValueError: If the username is an empty string.
    """
    if not username:
        raise ValueError("Username cannot be empty")
    # ... function logic ...
    return True
```

* The docstring clearly explains what the function does, what each parameter is for, the meaning of the return value, and what exceptions could occur. This is invaluable for users of the code and for automatically generating documentation.

* **In-line Comments:** Use comments sparingly to explain *why* something is done, especially if the code isn’t self-evident. Do not use comments to explain what the code is doing (if the code isn’t clear, refactor it rather than add a comment). But if there's an important rationale or a complex algorithm, a comment or a docstring explanation is very helpful.

* **Type Annotations:** Use Python’s type hints on function signatures and important variables. This makes the code self-documenting to some extent (tools and readers can immediately see the expected types) and helps catch errors early with static analysis (like mypy). For example, if a function is supposed to return a Dict\[str, int\] but returns a list by mistake, a type checker can warn you.

* **Project Documentation (mkdocs):** For larger projects, consider maintaining a docs site:

* Use **MkDocs** with the **Material for MkDocs** theme to create a user-friendly documentation site. This can include pages for installation, usage examples, an API reference (auto-generated from docstrings with the **mkdocstrings** plugin), and a contributors guide.

* Store documentation source files (Markdown) in a dedicated folder (e.g., docs/ or src/\<your\_package\>/docs/). Follow a structure so it's easy to navigate (for example, a Usage section with subpages for basic and advanced usage, an API Reference section grouping modules).

* The Material theme supports great features like search, syntax highlighting, and dark mode. We prefer to enable a **dark mode** by default (the theme’s palette setting can use a dark scheme like slate or even incorporate the *Catppuccin Mocha* color palette for a customized look).

* **mkdocstrings:** This plugin can pull docstrings from your code to build reference docs automatically. It’s configurable to show function signatures, source code, etc. in the docs. This ensures your documentation is always up-to-date with your code.

* **Example mkdocs.yml snippet:**

```yaml
site_name: MyProject
theme:
  name: material
  palette:
    - scheme: slate  # dark theme
      primary: indigo
      accent: indigo
plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          options:
            show_if_no_docstring: true
nav:
  - Home: index.md
  - Installation: installation.md
  - Usage:
      - Basic Usage: usage/basic.md
      - Advanced Features: usage/advanced.md
  - API Reference: api_reference.md
  - Contributing: contributing.md
```

* This sets up a basic structure. The nav defines the pages in the navigation bar. The theme palette slate is a built-in dark scheme; for a custom dark theme like Catppuccin, additional configuration or custom CSS may be needed.

* **Building docs:** Once configured, you can build the docs with mkdocs build, which will generate a static site (by default into a site/ or docs/ directory as configured). Host this via GitHub Pages or a similar static site host for easy access.

* **README.md:** Don’t neglect the repository’s README. It should contain:

* A high-level overview of the project (what it does, why it’s useful).

* Installation instructions (how to install the package or set up a development environment).

* Basic usage example or quickstart.

* Instructions for running tests or contributing, if applicable.

* License information.

* Badges for things like CI status or coverage are optional but can be added for visibility.

The README is often the first thing potential users or contributors see, so keep it clear and informative.

By providing good documentation and guides, you reduce the “bus factor” (the risk that knowledge lives only in one person’s head) and make the project accessible to others.

## 5. Tooling and Automation

Leverage tools and automation to maintain quality and reduce manual effort:

* **Linters and Static Analysis:** Set up a linter to catch issues like unused variables, undefined names, or common mistakes. **Ruff** is an excellent choice as it’s very fast and combines many linter capabilities (it can replace Flake8, pyflakes, and more). You can configure it via pyproject.toml to enable/disable specific rules. Also use **mypy** (or Pyright) for static type checking to catch type mismatches or incorrect usage of functions early.

* **Code Formatting:** Use **Black** for automatic code formatting (or an equivalent formatter). This eliminates debates about style and makes diffs cleaner. Developer tools (editors, CI) can run Black so that code is always formatted before being committed. Black’s defaults (like 88 char lines) are fine, but if needed, configure the line length in pyproject.toml to your project’s choice.

* **Import Sorting:** Use **isort** or Ruff’s built-in import sorter to keep imports ordered consistently. This improves readability and avoids merge conflicts where two people add imports in different orders.

* **Pre-commit Hooks:** Set up **pre-commit** hooks to automatically run formatting and linting before each commit. This ensures that no code that fails linting or formatting checks even gets committed to the repository. A typical .pre-commit-config.yaml might include hooks for black, ruff, isort, mypy, etc. Once configured, developers should run pre-commit install once, and then the hooks will run on each commit.

* **Continuous Integration (CI):** Use a CI service (like GitHub Actions, GitLab CI, etc.) to run tests and checks on every push:

* The CI should set up the environment (install the package in an isolated environment with dev dependencies).

* Run linters and type checkers.

* Run the test suite (possibly with coverage) and fail if any test fails or if coverage drops below a threshold.

* This prevents broken code from making it into the main branch.

* **Continuous Delivery (CD):** Automate deployments or releases:

* For libraries or packages, you can use CI workflows to publish to PyPI when you push a tagged commit (for example, pushing a tag v1.0.0 triggers a job to build and upload to PyPI). Modern practice is to use PyPI’s trusted publishing with OpenID Connect, which avoids storing credentials in CI secrets.

* For applications, you might build and push a Docker image to a registry on each release, or deploy to a server/environment automatically.

* **Example – GitHub Actions CI Workflow:**
  Create a file `.github/workflows/test.yml` in your repo with the following (adapt as needed):

```yaml
name: CI - Lint and Test
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install -U pip
          pip install .[dev]  # install package with dev dependencies
      - name: Lint and Type Check
        run: |
          ruff .
          mypy .
      - name: Run Tests
        run: |
          pytest --cov=src/your_package --cov-report=term-missing --cov-fail-under=80
```

* This workflow checks out the code, sets up Python, installs your package (including dev/test dependencies), then lints, type-checks, and runs tests with coverage.

* **Example – GitHub Actions Publish Workflow:**
  A separate file (e.g., `.github/workflows/publish.yml`) can handle publishing to PyPI when a new tag is pushed:

```yaml
name: Publish Package
on:
  push:
    tags: ['v*.*.*']  # triggers on version tags like v1.2.3
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # needed for OIDC
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Build and Publish
        run: |
          pip install build
          python -m build  # build wheel and sdist
          pip install twine
          python -m twine upload --non-interactive dist/*
        env:
          TWINE_USERNAME: __token__  # if using API token (classic method)
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

* In this example, we either use an API token stored in GitHub Secrets, or we could use PyPI’s trusted publisher (in which case Twine could be replaced by the official PyPI publish action using OIDC, which requires no password).

* **Dev Environment Consistency:** Use a tool to manage dependencies and environments:

* If using **Poetry** or **Hatch**, they will handle virtual environments and locking dependencies.

* If using **pip** and requirements files, ensure there’s a requirements.txt or requirements-dev.txt that pin versions for reproducibility.

* Our team often uses **Astral UV** (uv), a fast Rust-based package manager that integrates with pyproject.toml. This is why in some CI steps you see uv commands (e.g., uv pip install which ensures installation in the right environment).

* Regardless of tool, document how to set up the environment in the README (e.g., "run poetry install" or "run pip install -r requirements.txt").

Automating these aspects means fewer human errors and a faster development workflow. It allows developers to focus on writing code and tests, while the tooling takes care of enforcement of standards and catching issues early.

## 6. Security and Performance Considerations

Even if security and performance are not the primary focus initially, keeping them in mind can save a lot of trouble:

* **Security Best Practices:**

* **No Hardcoded Secrets:** Absolutely avoid putting passwords, API keys, tokens, or any sensitive credentials in the code. Use environment variables, configuration files (that are not committed to version control), or secret management services. For example, a database URL should come from an env var or a config file, not be directly in the source.

* **Secure Configuration:** Handle configuration (like debug modes, secret keys, etc.) via secure means. For instance, if using Django/Flask, don't enable debug or verbose logging in production. Use HTTPS for any external service communication if applicable.

* **Input Validation:** Any external input (user input, external API data, file contents) should be treated as potentially malicious or malformed. Validate inputs and use proper error handling. For web apps, use frameworks' validation features or libraries like Pydantic to enforce types/constraints.

* **Use Tools:** Run **Bandit** (a static security analyzer) on your codebase. It will catch common issues (use of eval, weak cryptography, usage of assert in non-test code, etc.). Also keep an eye on dependency vulnerabilities (tools like pip-audit or GitHub’s Dependabot can alert you to known vulnerable versions of libraries).

* **Least Privilege:** If your application interacts with a system or database, ensure it only has the permissions it needs. E.g., if it writes to a certain directory, don’t run it as a superuser; if it connects to a database, use a user with limited privileges.

* **Performance Optimizations:**

* **Algorithmic Efficiency:** Be mindful of the complexity of your algorithms. For instance, using a list for membership tests repeatedly is O(n) each time; using a set or dict can reduce that to O(1) on average. If you process large amounts of data, consider using streaming/generator patterns to avoid loading everything into memory at once.

* **Profiling:** If performance is critical, use profiling tools (like Python’s built-in cProfile or third-party profilers) to find bottlenecks. Often, 10% of the code might be taking 90% of the runtime. Focus optimization efforts there.

* **Concurrency:** For I/O-bound tasks (network calls, file I/O), consider using asyncio (with async/await) or multi-threading to handle multiple operations concurrently. For CPU-bound tasks, consider using multiprocessing or offloading heavy computations to specialized libraries (like NumPy, which uses C under the hood).

* **Caching:** If certain expensive computations or external calls are repeated, implement caching. This could be as simple as an in-memory cache (using functools.lru_cache for pure functions) or using a service like Redis for caching between runs.

* **Memory Usage:** Be cautious with very large data structures. Use generators for reading large files or processing streams of data so you don't hold everything in memory. If processing millions of items, process them in chunks rather than all at once.

* **Optimize After Measuring:** Premature optimization can complicate code without real benefit. Write clear code first; if you suspect a part is slow, add tests around it and then try optimizing with different approaches. Verify the improvement with benchmarks.

Security and performance often require trade-offs (e.g., more security checks can slightly slow down performance, using more memory can speed up algorithms, etc.). Aim for a balanced approach: **secure by default**, and **fast enough** for the requirements (with the ability to scale or optimize further if needed).

## 7. Maintainability and Extensibility

A codebase is a living thing — requirements change, new features are added, and people come and go. Designing for maintainability ensures the project can evolve without degrading:

* **Modular Design:** We’ve emphasized this before, but it’s crucial: a modular project (with clear separation of components) means you can work on or replace one part without breaking others. New features often fit naturally as new modules or classes, rather than entangled changes across the codebase.

* **Extensible Code via Plugins or Config:** If applicable, design the system to allow extension without modifying the core. For example, if you have a tool that could support multiple formats or backends, consider a plugin registry or a way to register new implementations (even if initially you only have one). This is related to the Open/Closed principle — adding new functionality by adding new code, not by altering existing code, reduces risk.

* **Avoid Technical Debt:** Don't postpone fixing known issues for too long. It's okay to mark something as TODO or use a # FIXME comment, but track these and address them. Otherwise, they accumulate (technical debt) and become harder to resolve.

* **Code Reviews:** Always have another pair of eyes (or more) on changes. Code reviews help maintain consistency, catch bugs or design issues early, and serve as knowledge transfer. Encourage a positive review culture where feedback is constructive.

* **Backward Compatibility:** If your project is a library or API used by others, try to maintain backward compatibility in public interfaces. If a breaking change is necessary, document it clearly in release notes and consider using deprecation warnings first (e.g., show a warning for one version before removing a feature in the next).

* **Versioning and Releases:** Follow **Semantic Versioning** (Major.Minor.Patch):
  * Increment the **major** version for incompatible API changes,
  * **minor** version for adding functionality in a backward-compatible manner, and
  * **patch** version for backward-compatible bug fixes.
  
  This communicates the impact of updates to users. Also, tag releases in your version control and maybe maintain a CHANGELOG.md listing changes for each version.

* **Minimal Dependencies:** Each dependency is an external factor you don’t control. Prefer standard library solutions if they meet your needs. When you do use a third-party package, ensure it’s well-maintained and widely used. Periodically review if all dependencies are still needed (sometimes a dependency was added for a feature that later gets removed, etc.).

* **Documentation for Developers:** In addition to user docs, have documentation for contributors or future maintainers:
  * Explain the overall architecture (a short paragraph or diagram of how components interact).

* Describe any tricky parts of the codebase or historical context if relevant.

* Provide setup instructions for development environment and running tests (so a new developer can get started quickly).

* If using unconventional tools or patterns (say, a specific package manager like uv, or a custom code generation step), make sure to cover that in the contributing docs.

A maintainable project is one that newcomers can understand and start contributing to with minimal friction. It also means bugs can be fixed and features added without fear of breaking everything. By keeping the code clean, modular, and well-documented, you set the project up for long-term success.

## 8. Project-Specific Conventions and Preferences

> **Note:** The following are specific preferences and conventions adopted by our team for consistency. While they align with general best practices, they also reflect choices that might be subjective or specific to our workflows.

* **Use pathlib for Paths:** Prefer pathlib.Path over using os.path and string file paths. Path objects make path manipulations clearer (e.g., Path("data") / "file.txt" concatenates paths) and reduce bugs with OS differences. Plus, many libraries accept Path objects directly.

* **FastAPI over Flask:** For web APIs or services, we lean towards **FastAPI** rather than Flask. FastAPI offers modern features like asynchronous request handling, data validation with Pydantic, automatic interactive docs, and better performance out of the box.

* **Open-Source Friendly Licenses:** We value using and contributing to open-source. When adding dependencies or choosing libraries, we give preference to those under **copyleft licenses** like GPL or AGPL (to encourage sharing improvements) unless there’s a strong reason otherwise. In any case, any open-source license is preferred over proprietary code. Similarly, our own projects should clearly be licensed (e.g., MIT, Apache 2.0, or GPL) to signal openness.

* **Use Modern Python Tools:** We use tools like **uv** (Astral's Unified Python tool) for managing environments and dependencies due to its speed and convenience. For example, instead of pip install, you might see uv pip install, and uv can manage virtual environments (uv venv) and add packages (uv add package[name]). This is in line with using modern, efficient tooling. If not using uv, tools like Poetry or Hatch are also great for dependency management and should be preferred over manually juggling pip and requirements files.

* **Simplicity over Complexity:** We favor simple functions and straightforward code. Whenever possible, use a simple function (with clear input and output) instead of a class that maintains state. Use classes and design patterns only when they provide clear structure or benefit. For example, a small utility could just be a function or two, rather than a class with static methods.

* **Dark Mode and Aesthetics:** On a lighter note, we prefer dark mode in our development tools and documentation. Our documentation and even some UI components (if applicable) use a dark theme, often inspired by the *Catppuccin Mocha* color palette for a pleasant aesthetic. While this doesn't affect code quality, it's a team preference to keep in mind for things like documentation theming or UI design.

* **CLI and API Design:** If the project provides a CLI, ensure it’s user-friendly (use a library like Click or Typer to handle commands, help text, and argument parsing). For APIs, follow RESTful or other agreed conventions consistently. The key is to make interfaces (whether CLI commands or API endpoints) intuitive and consistent.

These preferences help maintain a consistent developer experience and project philosophy. New team members should familiarize themselves with these conventions to ensure their contributions align with the rest of the project.

## 9. Summary Checklist for Reviewing a Python Project

Use the following checklist to quickly assess the quality of a Python project or to ensure you haven't missed anything in your own project. Add this to the elements added to the `.work/agent/issues/<priority>.md` file for easy reference, following the format specified earlier.

* [ ] **Code Style:** Is the code formatted according to PEP 8 (or the project's style guide) consistently? (Check with Black/Ruff). Are names meaningful and consistent?

* [ ] **Design & Principles:** Are there any obvious violations of DRY (duplicate code blocks)? Is the code kept simple where possible (no over-engineering)? Do functions and classes each handle a single responsibility?

* [ ] **Architecture:** Is the project structured into logical modules/packages? Is there a clear separation between different layers (e.g., UI vs. logic vs. data)? If the project has grown, does the architecture still hold up (or is it turning into spaghetti code)?

* [ ] **Documentation:** Do all public-facing functions and classes have docstrings? Is there a well-written README or documentation site that explains how to use and develop the project? Are there comments where needed to explain non-obvious parts of code?

* [ ] **Type Hints:** Are function parameters and return types annotated? If you run a type checker, does it report any issues? (This can catch subtle bugs.)

* [ ] **Testing:** Is there a test suite? Does it cover the core logic of the application? What's the approximate test coverage? Do tests cover edge cases and failure cases, not just the happy path?

* [ ] **CI/CD:** Is there a continuous integration set up to run tests and linters on new commits or pull requests? (Look for GitHub Actions, Travis CI, etc. configs in the repo). If this is a package, is there a workflow to publish new releases (e.g., to PyPI)?

* [ ] **Security:** No credentials in the repo (check for things like AWS keys, database URLs with passwords, etc.). Does the code avoid dangerous functions or patterns (like eval on unknown input)? Are dependencies relatively up-to-date to include security patches?

* [ ] **Performance:** Any obvious inefficiencies (e.g., doing expensive operations in a tight loop that could be done outside it, or using the wrong data structure for a job)? If the project is data-heavy, does it utilize libraries like NumPy/pandas where appropriate? Are there places where a lot of data is loaded into memory that could be streamed?

* [ ] **Dependencies:** Does the project use a standard way to manage dependencies (requirements.txt, pyproject.toml with Poetry/Hatch, etc.)? Can a new developer install the project easily? Are there any very outdated or unmaintained dependencies that might be a liability?

* [ ] **Maintainability:** Is the codebase relatively easy to navigate? (E.g., can you find the definition of a given functionality without too much hassle?) Are functions and classes reasonably short and focused? Do you spot any large "god classes" or overly long functions that should be refactored?

* [ ] **Extensibility:** If a new feature is to be added, does the structure allow it without major refactoring? (For instance, adding a new command to a CLI, or supporting a new data source, should ideally slot in by adding new modules or classes, rather than modifying many existing ones.)

Going through this checklist can reveal areas for improvement. Addressing these will lead to a cleaner, more robust, and more enjoyable project to work on.

## Anti-patterns

- Never import directly from src, ie. never do `from src.package import X`, always do `from package import X`
- avoid adding part of a library or module to the name of a class, ie. never create a class called `SQLModelProjectEntity` because it uses SQLModel internally, instead use `ProjectEntity` for better clarity and readability.