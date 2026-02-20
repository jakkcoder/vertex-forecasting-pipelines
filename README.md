# Vertex AI Forecasting Pipelines

Vertex AI pipelines for forecasting workloads.

## Local development

```bash
uv sync
uv run python pipelines/src/run_pipeline.py --env dev
```

## CI/CD (Buildkite)

Pushes to `main` automatically deploy to Vertex AI. See [.buildkite/README.md](.buildkite/README.md) for setup.
