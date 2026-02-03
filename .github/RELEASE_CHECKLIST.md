# Release Checklist

- [ ] Verify CI is green on `main`
- [ ] Update version via `scripts/version_bump.sh`
- [ ] Update changelog (for example `make changelog`)
- [ ] Review documentation updates (if applicable)
- [ ] Tag release `vX.Y.Z`
- [ ] Verify PyPI publish succeeded
- [ ] Publish GitHub Release notes
