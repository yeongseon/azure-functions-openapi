# Deployment Guide

## Automatic Deployment

- Trigger: merged pull request to `main`
- Workflow: `.github/workflows/deploy-production.yml`
- Target app: `production-<repository-name>`

## Manual Deployment (`workflow_dispatch`)

Use manual deployment for hotfixes, incident recovery, or controlled redeploys.

### How to run

1. Open GitHub Actions.
2. Select **Deploy to Production** workflow.
3. Click **Run workflow**.
4. Set optional inputs:
   - `app_name`: override target Function App name
   - `package_path`: override package path (default `dist/`)
5. Start the workflow and review logs.

### Authorization requirements

- Write access to the repository.
- Access to production environment secrets.
- Approval rules configured in GitHub Environments (recommended).

### When to use manual deployment

- Emergency redeploy of a known-good build.
- Hotfix deployment outside normal PR timing.
- Operational recovery after transient Azure failures.

## Rollback quick steps

For detailed rollback guidance, see `docs/rollback.md`.

1. Identify the last known-good commit or release tag.
2. Build artifacts from that revision.
3. Run manual deployment with the known-good package.
4. Verify key user flows and platform health indicators after deployment.
