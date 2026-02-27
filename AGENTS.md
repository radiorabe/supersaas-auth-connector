# Agents

This file provides guidance for AI agents and LLM tools working with this repository.

## Project Overview

SuperSaaS Auth Connector bridges [Keycloak](https://www.keycloak.org/) OIDC authentication
with [SuperSaaS](https://www.supersaas.com/) user management. It is a small [Starlette](https://www.starlette.io/)
application delivered as a container image. When a user authenticates via Keycloak, the connector
creates a corresponding user account in SuperSaaS (if it does not already exist) and then forwards
the user directly into SuperSaaS via the SuperSaaS login API.

Key dependencies:

- `starlette` — ASGI web framework
- `uvicorn` — ASGI server
- `python-keycloak` — Keycloak OIDC client
- `supersaas-api-client` — SuperSaaS REST API client
- `starlette-context` — per-request context storage

## Development Setup

```bash
python -mvenv venv
. venv/bin/activate
python -mpip install poetry
poetry install
```

## Running Tests and Linting

```bash
poetry run pytest          # run full test suite (includes ruff, mypy, doctests, coverage)
ruff check                 # lint only
ruff format                # format only
```

The test suite enforces 100% code coverage, type-checks with mypy, and runs ruff as part of
`pytest`. All Markdown files (including this one) are scanned for Python doctests by pytest's
`--doctest-glob='*.md'` option — do **not** add `>>>` doctest blocks to Markdown files unless
they are valid, self-contained doctests.

## Architecture

```
sac/
  settings.py   – Starlette Config-based settings loaded from environment variables
  app.py        – Starlette application, middleware, and route handlers
tests/
  test_app.py   – Integration tests using Starlette TestClient
```

The application has four routes:

| Path | Purpose |
|------|---------|
| `/` | Catch-all, redirects to `/supersaas` |
| `/oidc/callback` | OIDC callback handler, redirects to `/supersaas` after token exchange |
| `/supersaas` | Creates user in SuperSaaS and redirects to SuperSaaS login URL |
| `/logout` | Front-channel logout via Keycloak logout URL |

`_AuthenticationMiddleware` intercepts every request: it exchanges the OIDC code for a token on
the callback route, stores the token in the session, and fetches `userinfo` from Keycloak so that
route handlers have access to `request.state.user`.

## Coding Conventions

- Follow [ruff](https://docs.astral.sh/ruff/) lint rules (`select = ["ALL"]` with a few explicit
  ignores listed in `ruff.toml`). Run `ruff check` and `ruff format` before committing.
- All public symbols must have docstrings (pydocstyle rules are enforced by ruff). Private helpers
  (prefixed with `_`) require docstrings too because `D` rules apply globally outside of `tests/`.
- Use full type annotations everywhere; mypy is run in strict mode via `pytest-mypy`.
- Use conventional commit messages — see [Release Management](#release-management).

## Release Management

Releases are automated via [go-semantic-release](https://go-semantic-release.xyz/llms.txt) and
triggered by conventional commits merged to `main`. The format is:

```
<type>[optional scope]: <description>
```

| Type | Release effect |
|------|---------------|
| `fix:` | PATCH bump |
| `feat:` | MINOR bump |
| footer `BREAKING CHANGE:` | MAJOR bump |
| others (`chore:`, `docs:`, `refactor:`, …) | no release |

## LLM / AI Resources

The following `/llms.txt` files provide machine-readable documentation for the key tools and
services used in this project. Fetch them when you need authoritative reference information.

| Resource | URL |
|----------|-----|
| SuperSaaS API and platform | <https://www.supersaas.com/llms.txt> |
| Ruff linter and formatter | <https://docs.astral.sh/ruff/llms.txt> |
| Uvicorn ASGI server | <https://www.uvicorn.org/llms.txt> |
| GitHub Docs | <https://docs.github.com/llms.txt> |
