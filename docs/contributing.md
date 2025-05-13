# Contributing Guide

We welcome contributions to the `azure-functions-openapi` project!

## How to Contribute

1. **Fork the Repository**
2. **Create a New Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Write Code & Tests**
   - Run `make test` to ensure everything passes.
   - Follow code style using `black`, `ruff`, and `mypy`.

4. **Commit Your Changes**
   ```bash
   git commit -m "feat: describe your feature"
   ```

5. **Push and Create a Pull Request**

## Project Commands

```bash
make format      # Format code with black
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Prefix Types

| Type        | Description                               |
|-------------|-------------------------------------------|
| `feat:`     | New feature                               |
| `fix:`      | Bug fix                                   |
| `docs:`     | Documentation changes only                |
| `style:`    | Code formatting, no logic changes         |
| `refactor:` | Code refactoring without behavior changes |
| `test:`     | Adding or modifying tests                 |
| `chore:`    | Tooling, dependencies, CI/CD, versioning  |

### Examples

```bash
git commit -m "feat: add OpenAPI 3.1 support"
git commit -m "fix: handle empty request body gracefully"
git commit -m "docs: improve quickstart documentation"
git commit -m "refactor: extract schema builder logic"
git commit -m "chore: update dev dependencies"
```

> ✅ Use imperative present tense ("add", not "added").
> ✅ Keep the message concise and relevant to the change.

## Code of Conduct

Be respectful and inclusive. See the [Contributor Covenant](https://www.contributor-covenant.org/) for details.
