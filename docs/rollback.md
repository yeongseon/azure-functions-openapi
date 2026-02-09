# Rollback Guide

Use this guide when a production deployment causes service degradation.

## Rollback Triggers

- Health check failure after deployment.
- Elevated error rate or latency.
- Broken critical endpoint behavior.
- Security or data integrity concern.

## Manual Rollback Procedure

1. Identify the last known-good commit SHA or release tag.
2. Check out that revision and build artifacts.
3. Trigger **Deploy to Production** workflow manually.
4. Set `app_name` (if needed) and `package_path` to the rollback artifact.
5. Validate `/api/openapi.json` and key user flows after deployment.
6. Post incident details in the related PR/issue.

## Rollback Checklist

- [ ] Confirm incident scope and impact.
- [ ] Notify team and pause further deployments.
- [ ] Execute rollback deployment.
- [ ] Verify key user paths and platform health indicators.
- [ ] Capture root cause and add regression tests.

## Optional Automation Guidance

Automated rollback can be added later by combining:

- failed deployment verification in workflow
- deployment slot swap strategy
- release artifact pinning
