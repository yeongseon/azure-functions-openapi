# Release Process

This document describes the release workflow and versioning strategy.

## Versioning

The project follows semantic versioning (MAJOR.MINOR.PATCH).

- MAJOR: breaking changes
- MINOR: new features, backward compatible
- PATCH: bug fixes and security updates

Pre-release versions use `-alpha`, `-beta`, or `-rc` suffixes (for example `1.2.0-rc.1`).

## Release Checklist

Use `.github/RELEASE_CHECKLIST.md` during releases.

## Release Steps

1. Update version using `scripts/version_bump.sh`.
2. Update changelog using `scripts/changelog.sh`.
3. Create a release PR and verify CI.
4. Tag the release as `vX.Y.Z` after merge.
5. The `release.yml` workflow publishes to PyPI on tag push.

## Hotfix Process

1. Create a `fix/<topic>` branch from `main`.
2. Apply the fix with tests.
3. Bump PATCH version.
4. Merge and tag the patch release.

## Branch Protection Notes

- `main` should require PR reviews and CI checks.
- Tag creation should be restricted to maintainers.
