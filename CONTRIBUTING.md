# Contributing Guide

We welcome contributions to the `azure-functions-openapi` project.

## Branch Strategy

Use GitHub Flow and branch from `main`.

Recommended branch prefixes:

- `feat/` for new features
- `fix/` for bug fixes
- `docs/` for documentation-only changes
- `chore/` for tooling and maintenance
- `ci/` for workflow updates

## Development Workflow

1. Create a branch from `main`.
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feat/your-feature-name
   ```
2. Write code and tests.
3. Run the local quality gate.
   ```bash
   make check-all
   ```
4. Push and create a pull request.
   ```bash
   git push origin feat/your-feature-name
   ```

## Project Commands

```bash
make format      # Format code with ruff
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests
make cov         # Run tests with coverage
make check-all   # Run the full local gate
```

## Example Coverage Policy

Examples are part of the supported API experience and should stay verified.

- Keep one representative example for the minimal OpenAPI workflow.
- Keep one complex example for multi-endpoint and schema-heavy behavior.
- Add or update smoke tests whenever an example changes.
- Prefer lightweight smoke coverage over infrastructure-heavy end-to-end tests.

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Examples

```bash
git commit -m "feat: add OpenAPI 3.1 support"
git commit -m "fix: handle empty request body gracefully"
git commit -m "docs: improve quickstart documentation"
git commit -m "refactor: extract schema builder logic"
git commit -m "chore: update dev dependencies"
```

Use imperative present tense and keep the message concise.

## Deployment

- A merge to `main` triggers the production deployment workflow.
- Deployment status can be tracked from the related GitHub Actions run.

## Code of Conduct

Be respectful and inclusive. See our [Code of Conduct](CODE_OF_CONDUCT.md) for details.
