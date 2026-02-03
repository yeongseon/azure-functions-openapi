# Contributing Guide

We welcome contributions to the `azure-functions-openapi` project!

## Branch Strategy

We use **GitHub Flow**:

```
main ← feature/xxx
      ↑
  production
```

### Branch Types

| Branch Type | Purpose | Naming Convention |
|-------------|---------|-------------------|
| `main` | Production-ready code | `main` |
| `feat/*` | New features and enhancements | `feat/description` |
| `fix/*` | Bug fixes and corrections | `fix/description` |
| `docs/*` | Documentation changes | `docs/description` |
| `chore/*` | Maintenance and tooling | `chore/description` |
| `ci/*` | CI/CD and workflow changes | `ci/description` |

### Development Flow

1. **Development**: Create branch from `main`
2. **Testing**: Push branch → Automatic CI tests
3. **Production**: PR merge → Automatic deployment

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feat/your-feature-name
```

### 2. Write Code & Tests
```bash
make format      # Format code with black
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests
make cov         # Run tests with coverage
```

### 3. Push and Create Pull Request
```bash
git push origin feat/your-feature-name
# Create PR on GitHub
```

### 4. Automatic Production Deployment
- PR이 main에 병합되면 자동으로 production에 배포됨
- PR 댓글에서 배포 상태 확인 가능

## Project Commands

```bash
make format      # Format code with black
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests
make cov         # Run tests with coverage
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

## Branch Management

### Automatic Branch Cleanup
- **Stale Branches**: Branches older than 90 days without activity are automatically cleaned up
- **Stale Issues**: Issues and PRs older than 60 days without activity are automatically closed
- **Protection**: Main branch has protection rules requiring PR reviews and status checks

### Branch Longevity
- **Active Development**: Keep branches updated with main branch changes
- **Regular Cleanup**: Delete merged branches locally after PR is merged
- **Naming Consistency**: Follow the standardized naming conventions consistently

### Example Branch Management
```bash
# Update your feature branch with latest main changes
git checkout feat/your-feature-name
git pull origin main
git merge main

# Delete local branch after merge
git checkout main
git branch -d feat/your-feature-name

# Delete remote branch
git push origin --delete feat/your-feature-name
```

## Deployment

### Automatic Production Deployment
- **Trigger**: PR merge to main
- **URL**: `https://production-{repo-name}.azurewebsites.net`
- **Process**: Automatic deployment after PR approval

## Code of Conduct

Be respectful and inclusive. See our [Code of Conduct](CODE_OF_CONDUCT.md) for details.
