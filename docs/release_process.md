# Release Process

This document outlines the steps to release a new version of **azure-functions-openapi** to PyPI and update the changelog using the existing Makefile and Hatch-based workflows.

---

## 🧾 Step 1: Bump Version and Generate Changelog

Use Makefile targets to bump the version and update the changelog:

```bash
make release-patch     # Patch release (e.g., v0.10.0 → v0.10.1)
make release-minor     # Minor release (e.g., v0.10.1 → v0.11.0)
make release-major     # Major release (e.g., v0.11.0 → v1.0.0)
```

Each command will:

1. Update the version in `src/azure_functions_openapi/__init__.py`
2. Generate or update `CHANGELOG.md` via `git-cliff`
3. Commit the version bump and changelog
4. Create a Git tag (e.g., `v0.11.0`) and push to `main`

> Make sure your `main` branch is up-to-date before running these commands.

---

## 📝 Changelog Generation

The changelog is generated automatically by [git-cliff](https://git-cliff.org/) from conventional commit messages.

### Configuration

- `cliff.toml` — defines commit grouping, emoji categories, and output format
- `Makefile` — `make changelog` runs `git-cliff -o CHANGELOG.md`

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/) for proper changelog grouping:

| Prefix | Changelog Category |
|--------|--------------------|
| `feat:` | 🚀 Features |
| `fix:` | 🐛 Bug Fixes |
| `docs:` | 📚 Documentation |
| `refactor:` | 🚜 Refactor |
| `style:` | 🎨 Styling |
| `test:` | 🧪 Testing |
| `perf:` | ⚡ Performance |
| `ci:` / `chore:` | ⚙️ Miscellaneous Tasks |
| `build:` | 💼 Other |

Use scopes for more context: `fix(openapi): preserve explicit 200 response`

### Manual Changelog Regeneration

```bash
make changelog           # Regenerate CHANGELOG.md from all tags
make commit-changelog    # Stage and commit the updated changelog
```

---

## 📦 Step 2: Build and Test the Package

```bash
make build
```

To test the local build:

```bash
pip install dist/azure_functions_openapi-<version>-py3-none-any.whl
```

---

## 🚀 Step 3: Publish to PyPI

```bash
make publish-pypi
```

- Uses `hatch publish` under the hood
- Relies on `~/.pypirc` for authentication (must contain PyPI token)

---

## 🔁 Step 4: (Optional) Publish to TestPyPI

```bash
make publish-test
```

To install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ azure-functions-openapi
```

---

## ✅ Summary of Makefile Commands

| Task | Command |
|------|---------|
| Version bump + changelog | `make release-patch` / `release-minor` / `release-major` |
| Build distributions | `make build` |
| Publish to PyPI | `make publish-pypi` |
| Publish to TestPyPI | `make publish-test` |
| Regenerate changelog only | `make changelog` |
| Show current version | `make version` |

---

## 🔗 Related

- [CHANGELOG.md](https://github.com/yeongseon/azure-functions-openapi/blob/main/CHANGELOG.md)
- [Development Guide](development.md)
- [Contributing](contributing.md)
- [PyPI Publishing with Hatch](https://hatch.pypa.io/latest/publishing/)
