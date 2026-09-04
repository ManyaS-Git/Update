# Production infrastructure rollout

The existing direct database pipeline remains the default. Kafka is never simulated: it reports disabled, connected, or a concrete error through `GET /api/infrastructure/status`.

## Local services

Docker is required but was not installed in the development environment when this layer was created.

```bash
docker compose -f docker-compose.infrastructure.yml up -d
cd backend
.venv/bin/pip install -r requirements-infrastructure.txt
```

Use a private local `.env` (never commit it):

```dotenv
DATABASE_URL=postgresql+psycopg://updates:updates-local-only@127.0.0.1:5432/updates
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
```

For hosted Kafka, use TLS/SASL and secret-manager supplied credentials:

```dotenv
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=...
KAFKA_SASL_PASSWORD=...
```

## Safe activation gates

1. Back up the current SQLite database.
2. Provision PostgreSQL and test `SELECT 1`.
3. Migrate existing records explicitly; changing `DATABASE_URL` does not copy SQLite data.
4. Start Kafka and create/verify the configured topics.
5. Install `requirements-infrastructure.txt`.
6. Enable Kafka only after `/api/infrastructure/status` reports the client and broker ready.
7. Run ingestion in a staging environment and verify idempotency, dead-letter behavior, offsets, and aggregate parity.
8. Keep the direct pipeline available until streaming output matches it.

## Model gates

- Sarcasm remains `unavailable` until `SARCASM_INFERENCE_ENDPOINT_URL` points to a validated model service. There is no heuristic fallback.
- Graph analytics use real NetworkX PageRank now.
- GraphSAGE remains `not_run` until `torch-geometric` is installed and a sufficiently connected, evaluated interaction graph exists.
- BERTopic remains unavailable until its runtime is installed and real collected text passes minimum-size and cluster-quality gates.

## Required audit

Before production activation, verify credentials are secret-managed, Kafka uses encrypted transport, PostgreSQL backups and retention are configured, API rate limits are tested, platform terms permit collection, raw-event retention is bounded, and no private profile fields are emitted to analytics surfaces.
