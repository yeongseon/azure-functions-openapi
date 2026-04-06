# Deployment Guide
This guide walks through deploying two `azure-functions-openapi` examples to Azure Functions (`todo_crud` and `with_validation`) and verifying runtime behavior, OpenAPI endpoints, and Swagger UI headers. It also includes CLI-based spec generation for CI workflows. Outputs are representative examples, not guaranteed byte-for-byte.
## Prerequisites
| Requirement | Minimum | Notes |
|---|---|---|
| Azure subscription | Active | Use `<YOUR_SUBSCRIPTION_ID>` |
| Azure CLI (`az`) | Current | `az --version` |
| Azure Functions Core Tools (`func`) | v4 | `func --version` |
| Python | 3.10+ | Deploy runtime shown is Python 3.11 |
| `azure-functions-openapi` | v0.16.0 | Install in each example environment |

Install dependencies in each example project before deploy:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install azure-functions-openapi==0.16.0
```

Representative output:

```bash
Requirement already satisfied: pip in ./.venv/lib/python3.11/site-packages (25.0)
Collecting azure-functions
Collecting azure-functions-openapi==0.16.0
Collecting pydantic
Successfully installed azure-functions-1.24.0 azure-functions-openapi-0.16.0 pydantic-2.11.3
```

## Example 1: `todo_crud`
The `todo_crud` example uses an in-memory store (`TODOS = []`) and starts empty on cold start. The first created item gets `id=1`.
### Provision Azure resources

```bash
az account set --subscription <YOUR_SUBSCRIPTION_ID>
az group create --name <YOUR_RESOURCE_GROUP_TODO> --location eastus
az storage account create --name <YOUR_STORAGE_ACCOUNT_TODO> --resource-group <YOUR_RESOURCE_GROUP_TODO> --location eastus --sku Standard_LRS --kind StorageV2
az functionapp create --name <YOUR_FUNCTION_APP_TODO> --resource-group <YOUR_RESOURCE_GROUP_TODO> --storage-account <YOUR_STORAGE_ACCOUNT_TODO> --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
```

Representative output:

```json
{"name":"<YOUR_RESOURCE_GROUP_TODO>","location":"eastus","properties":{"provisioningState":"Succeeded"}}
{"name":"<YOUR_STORAGE_ACCOUNT_TODO>","kind":"StorageV2","provisioningState":"Succeeded"}
{"name":"<YOUR_FUNCTION_APP_TODO>","defaultHostName":"<YOUR_FUNCTION_APP_TODO>.azurewebsites.net","provisioningState":"Succeeded","state":"Running"}
```

### Configure app settings

```bash
az storage account show-connection-string --name <YOUR_STORAGE_ACCOUNT_TODO> --resource-group <YOUR_RESOURCE_GROUP_TODO> --query connectionString --output tsv
az functionapp config appsettings set --name <YOUR_FUNCTION_APP_TODO> --resource-group <YOUR_RESOURCE_GROUP_TODO> --settings AZURE_STORAGE_CONNECTION_STRING="<YOUR_STORAGE_CONNECTION_STRING_TODO>"
```

Representative output:

```text
<YOUR_STORAGE_CONNECTION_STRING_TODO>
```

```json
{"appSettings":[{"name":"AZURE_STORAGE_CONNECTION_STRING","slotSetting":false,"value":""},{"name":"FUNCTIONS_EXTENSION_VERSION","slotSetting":false,"value":"~4"},{"name":"FUNCTIONS_WORKER_RUNTIME","slotSetting":false,"value":"python"}]}

### Publish

From `examples/todo_crud`:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_TODO>
```

Representative output:

```text
Getting site publishing info...
[2026-04-06T10:27:41.021Z] Starting the function app deployment...
Uploading package...
Uploading 4.12 MB [#############################################################################]
Deployment completed successfully.
Syncing triggers...
Functions in <YOUR_FUNCTION_APP_TODO>:
    create_todo - [httpTrigger]
    list_todos - [httpTrigger]
    get_todo - [httpTrigger]
    update_todo - [httpTrigger]
    delete_todo - [httpTrigger]
    openapi_spec - [httpTrigger]
    openapi_yaml_spec - [httpTrigger]
    swagger_ui - [httpTrigger]
Deployment successful.
```

### Verify endpoints

```bash
export BASE_URL_TODO="https://<YOUR_FUNCTION_APP_TODO>.azurewebsites.net"
```

#### `POST /api/create_todo`

```bash
curl -s -i -X POST "$BASE_URL_TODO/api/create_todo" -H "Content-Type: application/json" -d '{"title":"Buy groceries"}'
```

Representative response:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{"id":1,"title":"Buy groceries","done":false}
```

#### `GET /api/list_todos`

```bash
curl -s -i "$BASE_URL_TODO/api/list_todos"
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"todos":[{"id":1,"title":"Buy groceries","done":false}]}
```

#### `GET /api/get_todo?id=1`

```bash
curl -s -i "$BASE_URL_TODO/api/get_todo?id=1"
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1,"title":"Buy groceries","done":false}
```

#### `PUT /api/update_todo`

```bash
curl -s -i -X PUT "$BASE_URL_TODO/api/update_todo" -H "Content-Type: application/json" -d '{"id":1,"title":"Buy groceries","done":true}'
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1,"title":"Buy groceries","done":true}
```

#### `DELETE /api/delete_todo?id=1`

```bash
curl -s -i -X DELETE "$BASE_URL_TODO/api/delete_todo?id=1"
```

Representative response:

```http
HTTP/1.1 204 No Content
Content-Type: text/plain; charset=utf-8
```

#### `GET /api/openapi.json`

`get_openapi_json()` is called without args in this example, so defaults apply (`title="API"`, `version="1.0.0"`).

```bash
curl -s -i "$BASE_URL_TODO/api/openapi.json"
```

Representative response (truncated):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "openapi": "3.0.0",
  "info": {"title": "API", "version": "1.0.0"},
  "paths": {
    "/api/create_todo": {"post": {"operationId": "createTodo"}},
    "/api/list_todos": {"get": {"operationId": "listTodos"}}
  }
}
```

#### `GET /api/openapi.yaml`

```bash
curl -s -i "$BASE_URL_TODO/api/openapi.yaml"
```

Representative response (truncated):

```http
HTTP/1.1 200 OK
Content-Type: application/x-yaml

openapi: 3.0.0
info: {title: API, version: 1.0.0}
paths:
  /api/create_todo: {post: {operationId: createTodo}}
  /api/list_todos: {get: {operationId: listTodos}}
```

#### `GET /api/docs`

```bash
curl -s -i "$BASE_URL_TODO/api/docs"
```

Representative response (headers + HTML start):

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-<NONCE>' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains
Cache-Control: no-cache, no-store, must-revalidate

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>API Documentation</title>
```

## Example 2: `with_validation`
The `with_validation` example uses `azure-functions-validation` (`@validate_http`) and an in-memory user store (`USERS = []`). It starts empty on cold start, so the first created user gets `id=1`.
### Provision Azure resources

```bash
az account set --subscription <YOUR_SUBSCRIPTION_ID>
az group create --name <YOUR_RESOURCE_GROUP_VALIDATION> --location eastus
az storage account create --name <YOUR_STORAGE_ACCOUNT_VALIDATION> --resource-group <YOUR_RESOURCE_GROUP_VALIDATION> --location eastus --sku Standard_LRS --kind StorageV2
az functionapp create --name <YOUR_FUNCTION_APP_VALIDATION> --resource-group <YOUR_RESOURCE_GROUP_VALIDATION> --storage-account <YOUR_STORAGE_ACCOUNT_VALIDATION> --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4
```

Representative output:

```json
{"name":"<YOUR_RESOURCE_GROUP_VALIDATION>","location":"eastus","properties":{"provisioningState":"Succeeded"}}
{"name":"<YOUR_STORAGE_ACCOUNT_VALIDATION>","kind":"StorageV2","provisioningState":"Succeeded"}
{"name":"<YOUR_FUNCTION_APP_VALIDATION>","defaultHostName":"<YOUR_FUNCTION_APP_VALIDATION>.azurewebsites.net","provisioningState":"Succeeded","state":"Running"}
```

### Configure app settings

```bash
az storage account show-connection-string --name <YOUR_STORAGE_ACCOUNT_VALIDATION> --resource-group <YOUR_RESOURCE_GROUP_VALIDATION> --query connectionString --output tsv
az functionapp config appsettings set --name <YOUR_FUNCTION_APP_VALIDATION> --resource-group <YOUR_RESOURCE_GROUP_VALIDATION> --settings AZURE_STORAGE_CONNECTION_STRING="<YOUR_STORAGE_CONNECTION_STRING_VALIDATION>"
```

Representative output:

```text
<YOUR_STORAGE_CONNECTION_STRING_VALIDATION>
```

```json
{"appSettings":[{"name":"AZURE_STORAGE_CONNECTION_STRING","slotSetting":false,"value":""},{"name":"FUNCTIONS_EXTENSION_VERSION","slotSetting":false,"value":"~4"},{"name":"FUNCTIONS_WORKER_RUNTIME","slotSetting":false,"value":"python"}]}

### Publish

From `examples/with_validation`:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_VALIDATION>
```

Representative output:

```text
Getting site publishing info...
[2026-04-06T10:47:13.207Z] Starting the function app deployment...
Uploading package...
Uploading 4.07 MB [#############################################################################]
Deployment completed successfully.
Syncing triggers...
Functions in <YOUR_FUNCTION_APP_VALIDATION>:
    create_user - [httpTrigger]
    get_user - [httpTrigger]
    openapi_spec - [httpTrigger]
    openapi_yaml_spec - [httpTrigger]
    swagger_ui - [httpTrigger]
Deployment successful.
```

### Verify endpoints

```bash
export BASE_URL_VALIDATION="https://<YOUR_FUNCTION_APP_VALIDATION>.azurewebsites.net"
```

#### `POST /api/users`

`create_user` is decorated with `@validate_http`; at runtime this returns `200 OK` by default even though the OpenAPI `response` block lists `201`.

```bash
curl -s -i -X POST "$BASE_URL_VALIDATION/api/users" -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1,"name":"Alice","email":"alice@example.com"}
```

#### `GET /api/users/1`

```bash
curl -s -i "$BASE_URL_VALIDATION/api/users/1"
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":1,"name":"Alice","email":"alice@example.com"}
```

#### `POST /api/users` (invalid payload)

```bash
curl -s -i -X POST "$BASE_URL_VALIDATION/api/users" -H "Content-Type: application/json" -d '{"name":"Alice"}'
```

Representative response (from `azure-functions-validation`):

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{"detail":[{"loc":["email"],"msg":"Field required","type":"missing"}]}
```

## CLI spec generation
Use the CLI to generate a static OpenAPI artifact during CI without manually calling API routes:
```bash
azure-functions-openapi generate --app-path ./function_app.py --format json --output ./openapi.json
```

Representative output:

```text
Generating OpenAPI spec from ./function_app.py
Detected Azure Functions routes and OpenAPI decorators
Wrote OpenAPI JSON to ./openapi.json
```

You can also output YAML:

```bash
azure-functions-openapi generate --app-path ./function_app.py --format yaml --output ./openapi.yaml
```

Representative output:

```text
Generating OpenAPI spec from ./function_app.py
Wrote OpenAPI YAML to ./openapi.yaml
```

For full CLI options and flags, see [`docs/cli.md`](./cli.md).

## Cleanup
```bash
az group delete --name <YOUR_RESOURCE_GROUP_TODO> --yes --no-wait
az group delete --name <YOUR_RESOURCE_GROUP_VALIDATION> --yes --no-wait
```

Representative output:

```text
{"status":"Accepted"}
{"status":"Accepted"}
```

## Sources

- [Azure Functions Python quickstart](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python)
- [Azure Functions Core Tools publish reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-core-tools-reference#func-azure-functionapp-publish)
- [Function App settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings)

## See Also

- [`azure-functions-validation`](https://github.com/yeongseon/azure-functions-validation)
- [`azure-functions-scaffold`](https://github.com/yeongseon/azure-functions-scaffold)
- [`docs/cli.md`](./cli.md)
