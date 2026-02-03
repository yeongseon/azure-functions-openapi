# Incident Response Guide

This guide describes how to respond to security incidents in this project.

## Triage

- Confirm the report is valid and reproducible
- Identify affected versions and components
- Classify severity

## Containment

- Limit exposure (disable endpoints, revoke tokens, rotate secrets)
- Communicate internally on status and next steps

## Remediation

- Implement the fix with tests
- Release a patch version
- Update documentation and advisories

## Communication

- Notify users via release notes or security advisory
- Provide mitigation steps if immediate upgrades are not possible

## Post-Incident Review

- Document root cause and resolution
- Add regression tests
- Update security guidance and automation
