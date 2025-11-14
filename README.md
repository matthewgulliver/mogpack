# Mogpack

**Reusable Python development tooling and configuration package with strict quality standards**

Mogpack provides a curated set of development dependencies and enforced quality standards for Python projects through [Nitpick](https://nitpick.rtfd.io/).

## What's Included

When you install mogpack, you get:

### Development Tools
- **nitpick** - Configuration enforcement
- **pytest** - Testing framework with testdox and coverage plugins
- **mypy** - Strict type checking with Pydantic plugin
- **ruff** - Fast Python linter and formatter
- **mutmut** - Mutation testing
- **pre-commit** - Git hook framework
- **testcontainers** - Docker-based integration testing
- **assertpy** - Fluent assertion library
- **mkdocs** - Documentation generation with Material theme

### Enforced Standards

Mogpack enforces the following configuration in your `pyproject.toml`:

- **MyPy**: Strict mode with Pydantic plugin support
- **Pytest**: Tests in `tests/`, testdox output, coverage enabled, 4 test markers (domain, app, contract, e2e)
- **Coverage**: 95% minimum coverage, branch coverage enabled, excludes tests
- **Ruff**: Python 3.10+ target, 100 char line length, comprehensive linting rules
- **Mutmut**: Mutation testing for `src/` directory

## Installation

### Quick Start

```bash
# Install mogpack as a dev dependency
uv add --dev mogpack

# Or with pip
pip install mogpack

# Initialize mogpack in your project
mogpack init

# Apply the configuration
nitpick fix

# Verify everything is configured
nitpick check
```

## Usage

### Initialize a New Project

```bash
# Create your project structure
mkdir my-project && cd my-project
mkdir -p src/my_project tests
touch src/my_project/__init__.py tests/__init__.py

# Create a basic pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# Install and initialize mogpack
uv add --dev mogpack
mogpack init
nitpick fix
```

### What `mogpack init` Does

The `mogpack init` command adds the following to your `pyproject.toml`:

```toml
[tool.nitpick]
style = ["github://matthewgulliver/mogpack@main/nitpick-style.toml"]
ignore_styles = []
```

This tells Nitpick to enforce the mogpack style, which ensures your project has all the necessary tool configurations.

### Using a Specific Version

You can pin to a specific version of the mogpack style:

```bash
# Use a specific tag
mogpack init --ref v0.1.0

# Use a specific commit
mogpack init --ref abc123

# Use a branch
mogpack init --ref develop
```

### Manual Configuration

If you prefer to configure manually, add this to your `pyproject.toml`:

```toml
[tool.nitpick]
style = ["github://matthewgulliver/mogpack@main/nitpick-style.toml"]
ignore_styles = []
```

Then run:

```bash
nitpick fix
nitpick check
```

## What Nitpick Will Configure

After running `nitpick fix`, your `pyproject.toml` will include:

```toml
[tool.mypy]
plugins = "pydantic.mypy"
files = ["src"]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--testdox", "--cov"]
markers = ["domain:", "app:", "contract:", "e2e"]

[tool.coverage.run]
source = ["src"]
branch = true
omit = ["tests/*", "*/conftest.py"]

[tool.coverage.report]
show_missing = true
fail_under = 95

[tool.coverage.html]
directory = "htmlcov"

[tool.ruff]
target-version = "py310"
line-length = 100
fix = true

[tool.ruff.lint]
select = ["YTT", "S", "B", "A", "C4", "T10", "SIM", "I", "C90", "E", "W", "F", "PGH", "UP", "RUF", "TRY"]

[tool.mutmut]
debug = true
paths_to_mutate = ["src/"]
do_not_mutate = ["*__init__*"]
pytest_add_cli_args_test_selection = ["-m", "not (paid or slow or e2e)"]
```

## Workflow Integration

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/andreoliwa/nitpick
    rev: v0.38.0
    hooks:
      - id: nitpick-check

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.5
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.18.2
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
```

Then install:

```bash
pre-commit install
```

### CI/CD

Example GitHub Actions workflow:

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install mogpack
          nitpick fix

      - name: Run quality checks
        run: |
          nitpick check
          ruff check .
          mypy .
          pytest
```

## Philosophy

Mogpack enforces opinionated quality standards:

- **Strict type checking**: No `any` types, strict null checks
- **High test coverage**: 95% minimum with branch coverage
- **Comprehensive linting**: 16 Ruff rule categories enabled
- **Behavior-driven testing**: Test markers for different testing levels
- **Mutation testing**: Verify your tests actually catch bugs

These standards ensure consistent, high-quality Python code across all your projects.

## License

MIT

## Contributing

Issues and pull requests welcome at [github.com/matthewgulliver/mogpack](https://github.com/matthewgulliver/mogpack)