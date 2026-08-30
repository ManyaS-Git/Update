# UPDATES

**AI-Powered Social Intelligence & Narrative Analytics Platform**

UPDATES is a presentation-ready prototype for **Smart India Hackathon 2026 — SIH 26152: Social Media Analytics**. It turns large volumes of noisy public conversation into concise, evidence-backed intelligence: what people are saying, why a narrative is changing, which aggregate communities are involved, how discussion is spreading, and what deserves attention.

> We do not just tell you what is trending. UPDATES explains what people are saying, why the conversation is changing, which communities are driving it, how it is spreading, and what deserves attention — backed by evidence and confidence.

## The problem

Raw public conversation is multilingual, repetitive, context-dependent and fragmented across platforms. Sending every comment directly to a three-label sentiment model produces weak intelligence. Existing social listening views can show volume and sentiment, but decision-makers also need qualified evidence, time-aware narratives, aggregate audience context, propagation signals and a clear explanation.

## Our solution

UPDATES combines:

- modular, policy-aware collection and normalized records;
- **CSQE**, a Contextual Signal Qualification Engine that scores relevance and noise before analytics;
- context-aware English, Hindi and Hinglish sentiment/stance architecture;
- explainable trend and narrative acceleration;
- probabilistic, aggregate audience intelligence with evidence and confidence;
- interaction-network analysis without unsupported causation claims;
- an evidence-grounded AI Analyst and daily/event intelligence brief.

The two-minute demo flow is: discovery homepage → reservation-protest intelligence → evidence and confidence → ask the AI Analyst → expand propagation analysis → explain CSQE.

## Architecture

```text
Public platform adapters / mock collectors
                  ↓
       normalization + timeline
                  ↓
    CSQE signal qualification engine
                  ↓
 contextual multilingual NLP and stance
                  ↓
 trends + aggregate audience + network
                  ↓
 evidence layer + intelligence brief
                  ↓
        FastAPI typed REST API
                  ↓
          Next.js 16 interface
```

Heavy analysis is separated from page requests. Demo mode serves precomputed aggregate statistics; real collectors can later feed background analysis jobs.

## Key features

- Reference-matched professional discovery homepage with persistent search and stories
- Topic intelligence for `/topic/reservation-protest`
- 55% opposing, 27% neutral and 18% supportive sentiment view
- Clear geography, language, broad age bracket, interest group, topic and platform evidence
- Conversation drivers, anonymized representative voices and confidence totals
- One focused conversation-volume chart
- Working, deterministic mock AI Analyst without paid keys
- Expandable aggregate propagation view
- Downloadable prototype intelligence brief
- Persistent SQLite/PostgreSQL-ready topics, stories, bookmarks, preferences and analysis runs
- Working saved-stories, personal feed, search, story detail and settings routes
- Credential-aware X, YouTube, Reddit, Facebook Page and Instagram professional-account comment collectors
- Local MuRIL sentiment for English, Hindi and Hinglish, with independent stance, safety and signal-quality labels
- `/sources` operations screen for connector truth, ingestion jobs and multilingual classification tests
- Methodology, privacy, uncertainty and API-limitations page
- Graceful frontend demo fallback when the backend is unavailable

## CSQE

`backend/app/services/csqe.py` assigns every record a signal-quality score and explanation. It recognizes empty/emoji-only content, contextless one-word replies, repetition patterns, semantic substance and topic relevance. Low-signal records are not deleted; downstream high-confidence analytics exclude or down-weight them.

Example: `BINOD` → low signal, because it contributes insufficient semantic context. A direct policy opinion receives a substantially higher score.

## Context-aware multilingual sentiment

`SentimentService` depends on a provider protocol, not a single model. The demo provider returns sentiment, stance, emotion, language, confidence and whether conversation context was used. This interface is designed for a later fine-tuned MuRIL-compatible Hugging Face provider; a raw pretrained model is not represented as solving the product labels.

## Audience, trend and network intelligence

- Audience results are aggregate and attach confidence plus evidence types. Age is a broad probabilistic bracket, not a verified identity fact. Income, exact age and exact location are not inferred.
- Trend labels are explainable (`STABLE`, `RISING`, `FAST_RISING`, `DECLINING`) and based on timestamped volume growth and acceleration.
- NetworkX supports interaction graphs and centrality. The UI describes the earliest **observed** and primary amplifying clusters; it does not claim proven origin or causation.

## AI Analyst

Questions are answered from structured topic analytics and evidence rather than as a generic chatbot. `MockAIProvider` makes the demo work without API keys. The provider protocol can be replaced with a hosted LLM later; secrets belong in environment variables.

## Technology stack

**Frontend:** Next.js 16, App Router, TypeScript, Tailwind CSS, npm, Recharts  
**Backend:** Python, FastAPI, Pydantic, SQLAlchemy  
**Database:** PostgreSQL target, SQLite development fallback  
**AI/NLP:** Hugging Face Transformers / MuRIL-compatible provider architecture, CSQE, contextual sentiment pipeline  
**Analytics:** NetworkX and explainable trend services  
**Visualization:** Recharts; a lightweight aggregate network view that can later move to Cytoscape.js

## Repository structure

```text
frontend/   Next.js UI, reusable components, typed demo data and API client
backend/    FastAPI routes, collectors, schemas, services, seed data and tests
docs/       Architecture, methodology and platform-access limitations
```

## Installation and local development

Prerequisites: Node.js 20+ with npm, and Python 3.11+.

Backend:

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Install the local MuRIL runtime (recommended for real multilingual inference)
pip install -r requirements-ml.txt
uvicorn app.main:app --reload
```

API documentation is available at `http://localhost:8000/docs`.

Frontend (in another terminal):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. In this workspace, browser interactions use `http://127.0.0.1:8001` by default (port 8000 may be occupied by an older preview) and fall back to local demo state if the API is offline. Set `NEXT_PUBLIC_API_URL` to override the backend address.

## Demo mode and environment

`DEMO_MODE=true` uses representative records and aggregate seed statistics. It does **not** generate 52,480 database rows. No paid API or LLM key is required. The optional local ML requirements download the MuRIL checkpoint on first classification and cache it under `backend/.hf-cache`.

Copy `.env.example` to `.env` and add only the credentials for platforms you are approved to access. X, YouTube and Reddit support query discovery. Facebook and Instagram deliberately require authorised post/media IDs; they do not perform unrestricted public discovery. Open `/sources` to see connector and model truth before running a job.

The repository includes only variables that map to planned adapters. Never commit secrets. In non-demo mode, a collector should only be enabled after its credentials, permitted scopes and platform-policy obligations are satisfied.

## API

Core endpoints include `/health`, topic analytics, `/api/stories`, `/api/search`, `/api/feed`, `/api/bookmarks`, `/api/preferences`, downloadable reports, `POST /api/ai/ask`, and persistent analysis runs. Social-intelligence endpoints include `/api/connectors`, `/api/models/status`, `/api/classify`, `/api/classify/batch`, `/api/ingestion/run`, `/api/ingestion/jobs`, `/api/comments`, and `/api/comments/summary`.

## Testing

```bash
cd frontend && npm run build && npm run lint
cd backend && pytest
```

Tests cover CSQE, sentiment response structure, trend classification, health and topic APIs.

## Data collection limitations

The repository never implies unrestricted platform access. X recent search requires an eligible API tier; YouTube consumes project quota; Reddit requires explicit API approval; and Facebook/Instagram access is limited to content authorised for the configured Page or professional account. See `docs/api-limitations.md` for the exact boundaries and source links.

## Privacy and ethics

UPDATES prefers aggregate audience intelligence, shows confidence, avoids unnecessary personal information, anonymizes representative voices, and does not infer income, exact age, exact address or unreliable gender attributes. Probabilistic inference must never be treated as verified identity information. Human interpretation remains necessary because models can be wrong.

## Future roadmap

Fine-tuned multilingual providers and more Indian languages; credentialed platform adapters; queued/background analysis; durable Postgres storage; report PDF generation; stronger community detection; historical trajectory models; and, only when scale requires them, Kafka/Redis/Celery/Neo4j or analytical storage.

## Team contributions

Keep collectors isolated behind `BaseCollector`, NLP behind provider interfaces, API responses typed, and UI components focused. Add tests for every analytics change, document confidence assumptions, avoid secrets and fabricated access, and keep the two-minute judge flow working.

## Screenshot placeholders

- `docs/screenshots/home.png` — discovery experience
- `docs/screenshots/topic.png` — intelligence experience

These placeholders can be captured during the team’s final presentation pass.
