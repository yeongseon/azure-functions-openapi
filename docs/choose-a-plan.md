# Choose an Azure Functions Hosting Plan

This guide helps you pick the right hosting plan **before you deploy anything**.
You do not need prior Azure experience — just a working Python project and an Azure account.

## Who this guide is for

You know Python, pip, and maybe Flask or FastAPI.
You may have used AWS Lambda or Google Cloud Functions, or you may have never touched cloud infrastructure at all.
Either way, this page gives you everything you need to make a confident plan choice.

## If you know AWS Lambda or Google Cloud Functions

Azure Functions is Microsoft's equivalent. The mental model maps like this:

| Concept | AWS | GCP | Azure |
|---|---|---|---|
| A single handler/endpoint | Lambda function | Cloud Function | **Function** (a route, timer, or trigger handler) |
| A deployable unit that groups handlers | — | — | **Function App** (one deployed app, many functions inside) |
| How your code runs and scales | Lambda configuration | Cloud Function configuration | **Hosting plan** (controls scaling, timeout, cold start, cost) |
| A billing/lifecycle boundary | AWS Account + Tags | GCP Project | **Resource Group** (a folder you can delete to clean up everything) |

If you have never used any of these, don't worry. The next section explains the Azure terms from scratch.

## The Azure terms you need

| Term | What it means |
|---|---|
| **Function** | A single HTTP endpoint, timer job, or event handler. Like a FastAPI route or a Flask view. |
| **Function App** | A deployed application that contains one or more functions. Like a Flask/FastAPI app that has multiple routes. You deploy once and all your functions go live together. |
| **Hosting plan** | The compute model that runs your Function App. It controls how your code scales, how long it can run, cold-start behavior, and cost shape. |
| **Resource Group** | A container for related Azure resources. Think of it as a folder. When you are done testing, delete the resource group and everything inside it goes away. |
| **Storage Account** | Azure Functions needs a storage account to manage internal state (triggers, logs, deployment packages). You create one, hand it to the Function App, and forget about it. |
| **Application Insights** | Optional monitoring service. Azure CLI creates one automatically when you create a Function App. You can use it to see logs, traces, and performance data. |

## What a hosting plan actually decides

Your choice of plan affects four things:

1. **Timeout** — How long a single function invocation can run before Azure kills it
2. **Cold start** — How fast your app responds after being idle
3. **Scaling** — How many instances spin up under load
4. **Cost** — Whether you pay per-invocation, per-second, or a fixed monthly amount

The Python code you write does **not** change between plans. Only the infrastructure commands change.

## The plans

Azure Functions offers several hosting plans. These docs cover three:

### Flex Consumption (recommended for most users)

- **Best for**: Learning, prototyping, lightweight HTTP APIs, low-traffic production
- **Timeout**: 30 minutes default (configurable)
- **Cold start**: Moderate (a few seconds after idle)
- **Scaling**: Automatic, scale-to-zero when idle
- **Cost**: Pay only when your code runs. Lowest entry cost. Scale-to-zero means $0 when idle.
- **Avoid if**: Your app has a large dependency footprint (>500 MB) or you need sub-second cold starts

### Premium (EP1 / EP2 / EP3)

- **Best for**: LLM/AI workloads, latency-sensitive APIs, apps with large dependencies
- **Timeout**: 30 minutes default, unlimited maximum
- **Cold start**: Minimal (always-warm instances available)
- **Scaling**: Automatic with pre-warmed instances
- **Cost**: Moderate baseline cost even when idle. You pay for at least one always-on instance.
- **Avoid if**: You are just learning and want to minimize cost

### Dedicated (App Service Plan — B1 / S1 / P1v2)

- **Best for**: Organizations already using App Service, predictable fixed-cost budgeting
- **Timeout**: 30 minutes default, unlimited maximum
- **Cold start**: None (always running)
- **Scaling**: Manual or autoscale rules (not automatic like Consumption/Premium)
- **Cost**: Fixed monthly cost regardless of usage. Cheapest SKU (B1) starts around $13/month.
- **Avoid if**: You want scale-to-zero or automatic scaling

> **Note**: Older Azure documentation may reference "Consumption" plan (classic). Flex Consumption is its successor and is recommended for new projects.

## Quick recommendation

```text
Start here:
 └─ Are you running LLM / AI agent workloads?
     ├─ YES → Premium (EP1)
     └─ NO
         └─ Do you need predictable cold starts (< 1 second)?
             ├─ YES → Premium (EP1)
             └─ NO
                 └─ Do you already run Azure App Service with fixed capacity?
                     ├─ YES → Dedicated (B1 or higher)
                     └─ NO → Flex Consumption ✅ (start here)
```

**For most users**: Start with **Flex Consumption**. It costs nothing when idle, handles most workloads well, and you can switch plans later without changing your code.

**For LLM/AI workloads** (like `azure-functions-langgraph`): Start with **Premium EP1**. LLM calls can take 30+ seconds, and cold starts frustrate users. Premium gives you always-warm instances and no hard timeout ceiling.

## Cost at a glance

| Plan | Idle cost | Per-request cost | Best mental model |
|---|---|---|---|
| Flex Consumption | $0 (scale-to-zero) | Pay per execution + GB-seconds | Like a taxi — pay only when riding |
| Premium (EP1) | ~$100-150/month (1 instance) | Included in base cost | Like a car lease — monthly payment, always available |
| Dedicated (B1) | ~$13/month | Included in base cost | Like renting a server — fixed monthly, always on |

> These are approximate. Actual costs depend on region, usage, and configuration.
> For exact pricing, see [Azure Functions pricing](https://azure.microsoft.com/pricing/details/functions/).

## Complete deployment commands by plan

Every example below uses these shared variables. Replace the placeholder values with your own:

```bash
RESOURCE_GROUP="rg-my-app"
LOCATION="koreacentral"
STORAGE_ACCOUNT="stmyapp$(date +%s | tail -c 6)"  # Must be globally unique, lowercase, no hyphens, 3–24 characters
FUNCTIONAPP_NAME="func-my-app"
```

### Step 1: Sign in and set subscription (all plans)

```bash
az login
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"
```

### Step 2: Create a resource group (all plans)

A resource group is a folder for your Azure resources. Delete it later to clean up everything.

```bash
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
```

### Step 3: Create a storage account (all plans)

Azure Functions requires a storage account for internal state management.

```bash
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Standard_LRS
```

### Step 4: Create the Function App

This is where the plans differ. **Copy the entire block for your chosen plan.**

#### Option A: Flex Consumption (recommended)

```bash
az functionapp create \
  --name "$FUNCTIONAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --storage-account "$STORAGE_ACCOUNT" \
  --flexconsumption-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.11
```

> No separate plan creation needed. Azure manages the compute automatically.

#### Option B: Premium (EP1)

```bash
# First, create the Premium plan
az functionapp plan create \
  --name "${FUNCTIONAPP_NAME}-plan" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku EP1 \
  --is-linux

# Then, create the Function App on that plan
az functionapp create \
  --name "$FUNCTIONAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --storage-account "$STORAGE_ACCOUNT" \
  --plan "${FUNCTIONAPP_NAME}-plan" \
  --runtime python \
  --runtime-version 3.11 \
  --os-type Linux
```

#### Option C: Dedicated (App Service Plan — B1)

```bash
# First, create the App Service plan
az appservice plan create \
  --name "${FUNCTIONAPP_NAME}-plan" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku B1 \
  --is-linux

# Then, create the Function App on that plan
az functionapp create \
  --name "$FUNCTIONAPP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --storage-account "$STORAGE_ACCOUNT" \
  --plan "${FUNCTIONAPP_NAME}-plan" \
  --runtime python \
  --runtime-version 3.11 \
  --os-type Linux
```

### Step 5: Deploy your code (all plans)

```bash
func azure functionapp publish "$FUNCTIONAPP_NAME"
```

### Step 6: Clean up (all plans)

Delete the resource group to remove **all** resources (Function App, plan, storage, monitoring):

```bash
az group delete --name "$RESOURCE_GROUP" --yes --no-wait
```

> ⚠️ **Cost reminder**: Azure resources cost money until deleted. Always clean up after testing.

## When to switch plans

Plan choice is not permanent. Common triggers to revisit:

| Situation | Consider switching to |
|---|---|
| Idle cost is too high on Premium | Flex Consumption |
| Cold starts are hurting user experience | Premium |
| LLM calls are timing out on Flex | Premium |
| Your team already manages App Service | Dedicated |
| You need VNet integration | Premium or Dedicated |

Switching plans does not require code changes — only infrastructure commands.

## Why these repos recommend different defaults

Most `azure-functions-*` repos default to **Flex Consumption** because:
- Lowest cost for learning and testing
- Zero idle cost (scale-to-zero)
- Simple provisioning (no plan creation step)
- Sufficient timeout (30 min) for most HTTP workloads

**Exception**: `azure-functions-langgraph` defaults to **Premium** because:
- LLM/agent invocations can take 30+ seconds
- Cold starts degrade the AI agent user experience
- Dependency footprint is larger (LangGraph + LLM SDKs)
- Premium's always-warm instances ensure predictable first response

## Learn more

- [Azure Functions hosting options](https://learn.microsoft.com/azure/azure-functions/functions-scale) — Official plan comparison
- [Azure Functions pricing](https://azure.microsoft.com/pricing/details/functions/) — Current pricing details
- [Azure Functions Python developer guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python) — Python-specific reference
- [Flex Consumption plan](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan) — Flex Consumption details
- [Azure Functions Premium plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan) — Premium plan details

## See Also

- [Deployment Guide](deployment.md) — Step-by-step deployment for this specific package
