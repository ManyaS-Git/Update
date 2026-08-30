# Architecture

The MVP is deliberately a two-application monorepo. Next.js owns presentation and interaction; FastAPI owns normalized data, qualification, analytics and intelligence responses. Demo mode precomputes aggregates so page rendering does not run NLP.

Collectors implement `fetch_posts`, `fetch_comments` and `normalize`. Normalized content feeds CSQE before sentiment, audience, trend and network services. Provider protocols keep platform, multilingual model and LLM choices replaceable.

PostgreSQL is the production persistence target and SQLite is the local fallback. Durable tables should represent topics, platforms, posts/comments, public profile signals, sentiment results, probabilistic audience inferences, trend snapshots, communities/edges, briefs and analysis runs. Raw platform metadata should be minimized and isolated.

The operator route `/sources` reports connector/model truth, starts bounded ingestion runs and provides a multilingual classification lab. Each stored comment receives independent sentiment, stance, safety, language, conversation-theme, influence and signal-quality results with confidence/evidence metadata.

For production volume, move ingestion and local MuRIL inference to a durable worker queue. The current bounded synchronous job is deliberate for a single-node prototype; streaming, queues, graph databases and analytical stores should be introduced only when measured load justifies them.
