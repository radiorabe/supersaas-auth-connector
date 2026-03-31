# Contributing

Thank you for your interest in contributing to SuperSaaS Auth Connector!
This guide explains how to report issues, propose changes, and submit pull requests.

## Reporting Issues

Open an issue on [GitHub](https://github.com/radiorabe/supersaas-auth-connector/issues) if you:

- Find a bug or unexpected behaviour
- Have a feature request or improvement idea
- Encounter documentation that is unclear or incorrect

Please include as much context as possible: the version you are running, relevant
environment variable values (redact secrets!), and the steps needed to reproduce the issue.

## Pull Requests

1. **Fork** the repository and create a feature branch from `main`.
2. Make your changes following the coding conventions below.
3. Add or update tests so that **coverage remains at 100 %**.
4. Run the full test suite and linter before opening a PR:
   ```bash
   poetry run pytest
   ruff check
   ruff format --check
   ```
5. Open a pull request against `main`. Use a
   [Conventional Commit](https://www.conventionalcommits.org/) subject line — this drives
   automated releases.

## Coding Conventions

- **Ruff** (`select = ["ALL"]`) is the linter and formatter. Run `ruff check --fix` and
  `ruff format` before committing.
- **All symbols** (public and private) must have docstrings — pydocstyle rules are enforced
  globally outside of `tests/`.
- **Full type annotations** everywhere. mypy is run in strict mode.
- **No `>>>` doctest blocks in Markdown** unless they are valid, self-contained doctests
  (the test suite executes them).

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

| Type | Effect |
|---|---|
| `fix:` | PATCH release |
| `feat:` | MINOR release |
| `BREAKING CHANGE:` footer | MAJOR release |
| `chore:`, `docs:`, `refactor:`, `ci:` | No release |

## CI/CD

The GitHub Actions workflows are based on
[RaBe shared actions](https://radiorabe.github.io/actions/):

| Workflow | Trigger | Purpose |
|---|---|---|
| `test.yaml` | Pull request | Runs pytest (includes mypy and ruff) |
| `release.yaml` | Push to `main` / tags | Builds and publishes the container image |
| `release-mkdocs` | Push to `main` | Builds and deploys this documentation site |
| `schedule.yaml` | Weekly schedule | Rebuilds the container image for base-image updates |
| `semantic-release.yaml` | Push to `main` | Creates GitHub releases from conventional commits |

## Documentation

Documentation lives in `docs/` and is built with
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/). To preview locally:

```bash
poetry install --with docs
poetry run mkdocs serve
```

Open `http://127.0.0.1:8000` in your browser. The site hot-reloads as you edit the
Markdown files.

When adding new pages, register them in the `nav:` section of `mkdocs.yaml`.

## License

By contributing you agree that your contributions will be licensed under the
[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.html).
