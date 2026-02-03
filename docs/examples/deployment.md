# Deployment Example

Provides a minimal deployment checklist for Azure Functions.

## Key Concepts

- Local testing
- Publish to Azure

## Sample Commands

```bash
func start
func azure functionapp publish <FUNCTION-APP-NAME> --python
```

## Notes

- Ensure `AZURE_FUNCTIONS_ENVIRONMENT` is set appropriately.
- Use CI/CD workflows for repeatable deployments.
