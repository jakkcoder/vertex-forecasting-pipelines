# Buildkite CI/CD Setup

This directory contains the Buildkite pipeline configuration for automatically deploying Vertex AI pipelines on push to `main`.

## Prerequisites

1. **Buildkite account** – [buildkite.com](https://buildkite.com)
2. **Buildkite agent** – Running on a machine with network access to GCP
3. **GCP service account** – With permissions to run Vertex AI pipelines

## Setup

### 1. Create a Buildkite pipeline

1. In Buildkite: **Pipelines** → **New pipeline**
2. Connect your Git repository (GitHub, GitLab, etc.)
3. Set **Pipeline configuration path**: `.buildkite/pipeline.yml`
4. Configure **Branch filtering** (optional): only `main` for deploy steps

### 2. Add GCP credentials as a secret

**Option A: Service account JSON (recommended for simplicity)**

1. Create or use a service account with:
   - `roles/aiplatform.user`
   - `roles/storage.objectAdmin` (for pipeline root bucket)
   - `roles/iam.serviceAccountUser` (to run as pipeline SA)
2. Download the JSON key
3. In Buildkite: **Pipeline** → **Settings** → **Environment**
4. Add secret: `GCP_SA_KEY` = full JSON content (paste the entire file)

**Option B: Key file on agent**

If your Buildkite agent runs on GCP with a service account, or has a key file mounted:

1. Set `GOOGLE_APPLICATION_CREDENTIALS` in the agent’s environment to the key file path
2. The pipeline will use it automatically (no `GCP_SA_KEY` needed)

**Option C: Workload Identity Federation (keyless, more secure)**

Use the [gcp-workload-identity-federation](https://github.com/buildkite-plugins/gcp-workload-identity-federation-buildkite-plugin) plugin for keyless auth.

### 3. Install uv on the agent

The pipeline uses [uv](https://github.com/astral-sh/uv) for Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or ensure `uv` is available in the agent’s `PATH`.

### 4. Trigger on push

By default, Buildkite triggers on every push. To deploy only on `main`:

- The deploy step already has `branches: main`
- Configure the pipeline to build only on `main`, or on all branches (validate on all, deploy on main)

## Pipeline steps

| Step | Description |
|------|-------------|
| **Setup** | Install uv, sync dependencies |
| **Validate** | Compile pipeline to verify it builds |
| **Deploy** | Run pipeline on Vertex AI (main branch only) |

## Environment variables

| Variable | Description |
|----------|-------------|
| `PIPELINE_ENV` | Target environment: `dev`, `stage`, or `prod` (default: `dev`) |
| `GCP_SA_KEY` | Service account JSON content (secret) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to key file (if not using `GCP_SA_KEY`) |

## Deploying to stage/prod

Set `PIPELINE_ENV` in Buildkite:

- **Pipeline Settings** → **Environment** → Add `PIPELINE_ENV=stage` or `PIPELINE_ENV=prod`
- Or use different Buildkite pipelines for each environment
