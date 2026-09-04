# Infrastructure safety audit

Date: 2026-09-04

## Result

The infrastructure foundation is safe to merge but **not ready to enable Kafka, GraphSAGE, or sarcasm in production** until the deployment gates below are satisfied. The existing direct application pipeline remains the default and all infrastructure features are disabled or unavailable by default.

## Verified

- Full backend regression suite: 33 passed.
- Docker Compose YAML parses and defines only PostgreSQL and Kafka services.
- No API keys, private keys, GitHub tokens, AWS keys, or OpenAI-style secrets were found in project files.
- Kafka publishes versioned envelopes to raw, normalized, and qualified topics only when explicitly enabled.
- Kafka uses idempotent `acks=all` production and reports connection errors; it does not simulate delivery.
- Failed Kafka publication is reported and attempts a dead-letter event without stopping the proven direct database pipeline.
- PostgreSQL and Kafka bind to localhost in the local Compose configuration.
- Sarcasm output remains `null` unless a validated HTTPS/localhost inference endpoint is configured.
- Network analysis uses real NetworkX PageRank when a graph exists.
- GraphSAGE reports `not_run`; no GraphSAGE result is fabricated.
- Offline Hugging Face model loading does not retry the public network unless `HF_ALLOW_MODEL_DOWNLOAD=true` is explicitly set.
- Explicit opposing stance cannot be silently returned as positive sentiment by the fallback model.
- `/api/infrastructure/status` exposes database, Kafka, model-runtime, and feature-readiness state.

## Blockers before activation

- Docker is not installed in the current development environment.
- `aiokafka` is not installed in the current application environment.
- PostgreSQL data migration from the current SQLite database has not been executed.
- Kafka TLS/SASL credentials and hosted broker endpoints are not configured.
- `torch-geometric` and an evaluated interaction-graph training dataset are not available for GraphSAGE.
- No validated sarcasm inference endpoint is configured.
- BERTopic is not installed and no topic-model quality gate has been run on sufficient real collected text.

## Required production checks

Provision secret-managed credentials, encrypted Kafka transport, PostgreSQL backups, bounded raw-event retention, consumer lag monitoring, broker alerts, schema compatibility tests, staging parity tests, platform-policy review, and a rollback exercise before enabling streaming in production.
