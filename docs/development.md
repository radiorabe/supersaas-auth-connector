# Development

This guide covers everything you need to build, test, and iterate on the SuperSaaS Auth
Connector locally.

## Prerequisites

- Python 3.12 or later
- [Poetry](https://python-poetry.org/) (installed globally or via `pipx`)

## Setup

```bash
# Clone the repository
git clone https://github.com/radiorabe/supersaas-auth-connector.git
cd supersaas-auth-connector

# Create a virtual environment and install all dependencies
python -m venv .venv
. .venv/bin/activate
python -m pip install poetry
poetry install
```

## Running Tests

The full test suite includes unit/integration tests, type checking (mypy), linting (ruff),
and a 100 % coverage gate:

```bash
poetry run pytest
```

To run a subset of tests or get verbose output:

```bash
# Verbose, stop on first failure
poetry run pytest -x -v

# Run a specific test file
poetry run pytest tests/test_app.py
```

### What the test suite checks

| Check | Tool | Config |
|---|---|---|
| Tests + coverage (100 % required) | pytest + pytest-cov | `pyproject.toml` |
| Type checking | mypy (strict) | `pyproject.toml` |
| Linting | ruff | `ruff.toml` |
| Doctest blocks in Markdown | pytest `--doctest-glob` | `pyproject.toml` |

!!! warning
    Do not add `>>>` doctest blocks to Markdown files unless they are valid,
    self-contained doctests — the test suite will execute them.

## Linting and Formatting

```bash
# Check for lint errors
ruff check

# Auto-fix lint errors where possible
ruff check --fix

# Format code
ruff format
```

The ruff configuration (`ruff.toml`) enforces nearly all ruff rules (`select = ["ALL"]`)
with a small set of explicit ignores. All public **and** private symbols require docstrings.

## Type Checking

mypy is run in strict mode by pytest via `pytest-mypy`. Run it standalone:

```bash
poetry run mypy sac/
```

## Building the Container Image

The container image is built by CI using Docker build-push-action. To build it locally:

```bash
docker build -t supersaas-auth-connector:dev .
docker run --rm -p 8000:8000 \
  -e SUPERSAAS_API_TOKEN=test \
  supersaas-auth-connector:dev
```

## Release Management

Releases are automated by
[go-semantic-release](https://go-semantic-release.xyz/)
triggered by conventional commits merged to `main`.

Use [Conventional Commits](https://www.conventionalcommits.org/) in your commit messages:

| Prefix | Release effect |
|---|---|
| `fix:` | PATCH version bump |
| `feat:` | MINOR version bump |
| `BREAKING CHANGE:` footer | MAJOR version bump |
| `chore:`, `docs:`, `refactor:`, … | No release |

If a commit does not follow the convention, fix the message during **Squash and Merge**
on the pull request.

## Project Layout

```
sac/
  __init__.py   – package marker
  app.py        – Starlette app, middleware, and route handlers
  settings.py   – Starlette Config settings from environment variables
  py.typed      – PEP 561 marker

tests/
  test_app.py   – integration tests using Starlette TestClient

docs/           – MkDocs documentation source
Dockerfile      – container image definition
pyproject.toml  – project metadata and dev dependencies
mkdocs.yaml     – documentation site configuration
ruff.toml       – ruff lint configuration
```
