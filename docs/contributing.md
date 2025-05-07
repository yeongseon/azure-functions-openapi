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

## Code of Conduct

Be respectful and inclusive. See the [Contributor Covenant](https://www.contributor-covenant.org/) for details.
