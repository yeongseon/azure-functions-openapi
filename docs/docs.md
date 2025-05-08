# Documentation Site with MkDocs

This project uses [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme to build and deploy its documentation site.

## Requirements

To build and serve the documentation locally, install the following:

```bash
pip install mkdocs mkdocs-material
```

## Local Preview

To run the documentation site locally:

```bash
mkdocs serve
```

Visit `http://localhost:8000` in your browser to preview the documentation.

## Deployment

Documentation is deployed to GitHub Pages automatically using GitHub Actions.

The workflow file is located at:

```text
.github/workflows/deploy.yml
```

### Deployment Trigger

The workflow runs on every push to the `main` branch and executes the following command:

```bash
mkdocs gh-deploy --force
```

This publishes the site to the `gh-pages` branch.

## Configuration

The documentation structure and appearance are defined in `mkdocs.yml`. It includes:

- Site name and theme
- Navigation menu
- Markdown extensions
- Repository and edit links

You can customize these settings as needed.

## Tips

- Always run `mkdocs serve` before committing to validate changes.
- Use `mkdocs build` to generate the static site without serving.
- Ensure all Markdown files are included in navigation in `mkdocs.yml`.

