"use client";
import { FormEvent, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  DatabaseZap,
  FlaskConical,
  Layers,
  LoaderCircle,
  Play,
  Radio,
  RefreshCw,
  Search,
  Sparkles,
  TrendingUp,
  XCircle,
  Zap,
} from "lucide-react";
import {
  analyzeTopicQuery,
  AutomationStatus,
  classifyComment,
  ConnectorStatus,
  getAutomationStatus,
  getConnectors,
  getIngestionJobs,
  getKafkaStatus,
  getModelStatus,
  getTopics,
  IngestionJob,
  KafkaStatusResponse,
  runAutomationNow,
  runIngestion,
  TopicAnalysisResponse,
  TopicSummary,
} from "@/lib/api";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

type ModelState = Awaited<ReturnType<typeof getModelStatus>>;
const labels: Record<string, string> = {
  x: "X",
  youtube: "YouTube",
  reddit: "Reddit",
  telegram: "Telegram",
  facebook: "Facebook",
  instagram: "Instagram",
};

export function SourcesPage() {
  const [connectors, setConnectors] = useState<ConnectorStatus[]>([]);
  const [models, setModels] = useState<ModelState | null>(null);
  const [kafka, setKafka] = useState<KafkaStatusResponse | null>(null);
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [topicSlug, setTopicSlug] = useState("");
  const [automation, setAutomation] = useState<AutomationStatus | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [query, setQuery] = useState("AI and Technology Regulation");
  const [targets, setTargets] = useState<Record<string, string>>({
    facebook: "",
    instagram: "",
    youtube: "",
    reddit: "",
    telegram: "",
    x: "",
  });
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("");
  const [sample, setSample] = useState(
    "yeh policy bilkul sahi hai aur students ke liye naye opportunities layegi"
  );
  const [classification, setClassification] = useState<Record<string, unknown> | null>(null);
  const [classifying, setClassifying] = useState(false);

  // Section 17 Topic Analysis Lab
  const [interactiveQuery, setInteractiveQuery] = useState("Artificial Intelligence");
  const [interactiveResult, setInteractiveResult] = useState<TopicAnalysisResponse | null>(null);
  const [analyzingInteractive, setAnalyzingInteractive] = useState(false);

  function refresh() {
    getConnectors()
      .then((items) => {
        setConnectors(items);
        setSelected((current) =>
          current.length ? current : items.filter((item) => item.configured).map((item) => item.platform)
        );
      })
      .catch(() => setMessage("Backend is currently offline."));
    getModelStatus().then(setModels).catch(() => {});
    getKafkaStatus().then(setKafka).catch(() => {});
    getIngestionJobs().then(setJobs).catch(() => {});
    getTopics()
      .then((topicList) => {
        setTopics(topicList);
        if (topicList.length > 0 && !topicSlug) {
          setTopicSlug(topicList[0].slug);
          setQuery(topicList[0].title);
        }
      })
      .catch(() => {});
    getAutomationStatus().then(setAutomation).catch(() => {});
  }

  useEffect(refresh, []);

  function toggle(platform: string) {
    setSelected((values) =>
      values.includes(platform) ? values.filter((item) => item !== platform) : [...values, platform]
    );
  }

  async function ingest(event: FormEvent) {
    event.preventDefault();
    if (!selected.length) return setMessage("Configure and select at least one platform.");
    setRunning(true);
    setMessage("");
    try {
      const targetMap = Object.fromEntries(
        Object.entries(targets).map(([key, value]) => [
          key,
          value
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
        ])
      );
      const result = await runIngestion({
        topic_slug: topicSlug || "custom-narrative",
        query,
        platforms: selected,
        targets: targetMap,
        max_items: 100,
      });
      setMessage(
        result.status === "completed"
          ? `Job completed. ${Object.values(result.results).reduce(
              (sum, item) => sum + item.stored,
              0
            )} new comments stored and routed to Kafka streaming bus.`
          : `Job ${result.status}: ${Object.values(result.errors).join(" ")}`
      );
      refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Ingestion failed");
    } finally {
      setRunning(false);
    }
  }

  async function runAuto() {
    setRunning(true);
    try {
      const result = await runAutomationNow();
      setAutomation(result);
      setMessage(
        result.status === "blocked"
          ? "Automation is active; platform credentials or public endpoints will be queried."
          : `Automation processed ${result.topics_processed} topics and stored ${result.comments_stored} signals.`
      );
      refresh();
    } catch {
      setMessage("Automatic collection could not start.");
    } finally {
      setRunning(false);
    }
  }

  async function classify() {
    setClassifying(true);
    try {
      setClassification(await classifyComment(sample));
      getModelStatus().then(setModels).catch(() => {});
    } catch {
      setMessage("Classifier API is unavailable.");
    } finally {
      setClassifying(false);
    }
  }

  async function runInteractiveAnalysis(e: FormEvent) {
    e.preventDefault();
    if (!interactiveQuery.trim()) return;
    setAnalyzingInteractive(true);
    try {
      const res = await analyzeTopicQuery(interactiveQuery.trim(), 30);
      setInteractiveResult(res);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Topic analysis failed");
    } finally {
      setAnalyzingInteractive(false);
    }
  }

  return (
    <div className="app-shell">
      <Sidebar active="Sources" />
      <main className="main">
        <Topbar />
        <header className="utility-header">
          <DatabaseZap />
          <div>
            <span>REAL-TIME DATA & STREAMING PIPELINE</span>
            <h1>Sources, Connectors & Streaming Bus</h1>
            <p>
              Monitor multi-platform ingestion, verify real-time Kafka streaming health, and run interactive c-TF-IDF topic analysis.
            </p>
          </div>
        </header>

        {/* Kafka Streaming Bus Health Card */}
        <section
          className="panel"
          style={{
            marginBottom: "1.5rem",
            background: "rgba(36,39,58,0.7)",
            border: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Zap size={20} style={{ color: kafka?.status === "connected" ? "#a6da95" : "#eed49f" }} />
              <div>
                <h2 style={{ fontSize: "1.1rem", margin: 0 }}>Kafka Event Streaming Layer</h2>
                <small style={{ color: "#a5adcb" }}>
                  Broker: {kafka?.bootstrap_servers || "localhost:9092"} · Mode:{" "}
                  {kafka?.status === "connected" ? "Active Broker" : "Resilient In-Memory Async Stream"}
                </small>
              </div>
            </div>
            <span
              style={{
                fontSize: "0.75rem",
                padding: "4px 12px",
                borderRadius: "999px",
                fontWeight: 600,
                background:
                  kafka?.status === "connected" ? "rgba(166, 218, 149, 0.2)" : "rgba(238, 212, 159, 0.2)",
                color: kafka?.status === "connected" ? "#a6da95" : "#eed49f",
              }}
            >
              {kafka?.status?.toUpperCase() || "INITIALIZING"}
            </span>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "1rem",
              background: "rgba(24, 25, 38, 0.5)",
              padding: "1rem",
              borderRadius: "8px",
            }}
          >
            <div>
              <small style={{ color: "#8087a2", textTransform: "uppercase", fontSize: "0.7rem", fontWeight: 700 }}>
                Raw Ingestion Topic
              </small>
              <div style={{ color: "#cad3f5", fontFamily: "monospace", fontSize: "0.85rem", marginTop: "2px" }}>
                {kafka?.topics.social_raw || "social.posts.raw"}
              </div>
            </div>
            <div>
              <small style={{ color: "#8087a2", textTransform: "uppercase", fontSize: "0.7rem", fontWeight: 700 }}>
                CSQE Filtered Topic
              </small>
              <div style={{ color: "#cad3f5", fontFamily: "monospace", fontSize: "0.85rem", marginTop: "2px" }}>
                {kafka?.topics.social_high_signal || "social.posts.high_signal"}
              </div>
            </div>
            <div>
              <small style={{ color: "#8087a2", textTransform: "uppercase", fontSize: "0.7rem", fontWeight: 700 }}>
                Analytics Broadcast
              </small>
              <div style={{ color: "#cad3f5", fontFamily: "monospace", fontSize: "0.85rem", marginTop: "2px" }}>
                {kafka?.topics.social_analytics || "social.analytics"}
              </div>
            </div>
            <div>
              <small style={{ color: "#8087a2", textTransform: "uppercase", fontSize: "0.7rem", fontWeight: 700 }}>
                Queue Depth
              </small>
              <div style={{ color: "#a6da95", fontWeight: "bold", fontSize: "0.9rem", marginTop: "2px" }}>
                {kafka?.in_memory_fallback.queue_size ?? 0} queued signals
              </div>
            </div>
          </div>
        </section>

        {/* Section 17: Interactive Topic Analysis Tool */}
        <section
          className="panel"
          style={{
            marginBottom: "1.5rem",
            background: "rgba(36,39,58,0.7)",
            border: "1px solid rgba(138, 173, 244, 0.2)",
          }}
        >
          <div style={{ marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Cpu size={20} style={{ color: "#8aadf4" }} />
              <h2 style={{ fontSize: "1.1rem", margin: 0 }}>Interactive Dynamic Topic Analysis Lab</h2>
            </div>
            <p style={{ color: "#a5adcb", fontSize: "0.85rem", margin: "0.25rem 0 0" }}>
              Enter any real-world topic to dynamically extract c-TF-IDF keyword clusters, calculate CSQE signal purity, and evaluate real-time sentiment distribution.
            </p>
          </div>

          <form onSubmit={runInteractiveAnalysis} style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            <input
              type="text"
              value={interactiveQuery}
              onChange={(e) => setInteractiveQuery(e.target.value)}
              placeholder="Enter topic e.g. Quantum Computing, Renewable Energy, Inflation..."
              style={{
                flex: 1,
                padding: "0.6rem 1rem",
                borderRadius: "8px",
                background: "rgba(24,25,38,0.8)",
                border: "1px solid rgba(255,255,255,0.15)",
                color: "#cad3f5",
                fontSize: "0.9rem",
              }}
              required
            />
            <button
              type="submit"
              disabled={analyzingInteractive}
              style={{
                padding: "0.6rem 1.25rem",
                borderRadius: "8px",
                background: "#8aadf4",
                color: "#181926",
                fontWeight: "bold",
                border: "none",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.5rem",
              }}
            >
              {analyzingInteractive ? <LoaderCircle size={16} className="spin" /> : <Search size={16} />}
              {analyzingInteractive ? "Analyzing..." : "Analyze Topic"}
            </button>
          </form>

          {interactiveResult && (
            <div
              style={{
                background: "rgba(24,25,38,0.6)",
                padding: "1.25rem",
                borderRadius: "8px",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: "1rem",
                  marginBottom: "1rem",
                }}
              >
                <div>
                  <small style={{ color: "#8087a2" }}>Analyzed Signals</small>
                  <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#cad3f5" }}>
                    {interactiveResult.total_signals}
                  </div>
                </div>
                <div>
                  <small style={{ color: "#8087a2" }}>CSQE High-Signal Ratio</small>
                  <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#a6da95" }}>
                    {Math.round(interactiveResult.high_signal_ratio * 100)}%
                  </div>
                </div>
                <div>
                  <small style={{ color: "#8087a2" }}>Sentiment Breakdown</small>
                  <div style={{ fontSize: "0.85rem", color: "#cad3f5", display: "flex", gap: "8px", marginTop: "4px" }}>
                    <span style={{ color: "#a6da95" }}>{interactiveResult.sentiment.positive}% Pos</span>
                    <span style={{ color: "#eed49f" }}>{interactiveResult.sentiment.neutral}% Neu</span>
                    <span style={{ color: "#ed8796" }}>{interactiveResult.sentiment.negative}% Neg</span>
                  </div>
                </div>
              </div>

              {/* c-TF-IDF Keywords */}
              <div style={{ marginBottom: "1rem" }}>
                <strong style={{ fontSize: "0.85rem", color: "#cad3f5", display: "block", marginBottom: "0.5rem" }}>
                  Extracted c-TF-IDF Semantic Keywords:
                </strong>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {interactiveResult.top_keywords.map((kw) => (
                    <span
                      key={kw.term}
                      style={{
                        fontSize: "0.75rem",
                        padding: "3px 10px",
                        borderRadius: "999px",
                        background: "rgba(138, 173, 244, 0.15)",
                        color: "#8aadf4",
                        border: "1px solid rgba(138, 173, 244, 0.3)",
                      }}
                    >
                      {kw.term} <small style={{ opacity: 0.7 }}>({kw.c_tfidf.toFixed(2)})</small>
                    </span>
                  ))}
                </div>
              </div>

              {/* High-Signal Samples */}
              {interactiveResult.recent_high_signal_samples.length > 0 && (
                <div>
                  <strong style={{ fontSize: "0.85rem", color: "#cad3f5", display: "block", marginBottom: "0.5rem" }}>
                    Verified High-Signal Discourse Samples:
                  </strong>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {interactiveResult.recent_high_signal_samples.slice(0, 3).map((s, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: "0.5rem 0.75rem",
                          background: "rgba(36,39,58,0.5)",
                          borderRadius: "6px",
                          fontSize: "0.82rem",
                          color: "#cad3f5",
                          borderLeft: "3px solid #8aadf4",
                        }}
                      >
                        <p style={{ margin: "0 0 0.25rem 0" }}>"{s.text}"</p>
                        <div style={{ display: "flex", gap: "1rem", fontSize: "0.72rem", color: "#8087a2" }}>
                          <span style={{ textTransform: "capitalize" }}>Platform: {s.platform}</span>
                          <span>Quality: {(s.signal_quality * 100).toFixed(0)}%</span>
                          <span style={{ textTransform: "capitalize" }}>Sentiment: {s.sentiment}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Source Connectors & Ingestion Layout */}
        <div className="source-layout">
          <section className="panel source-panel">
            <div className="source-heading">
              <div>
                <h2>Official Platform Connectors</h2>
                <p>Credentials stay protected in server environment variables.</p>
              </div>
              <button onClick={refresh} aria-label="Refresh connector status">
                <RefreshCw size={16} />
              </button>
            </div>
            <div className="connector-grid">
              {connectors.map((item) => (
                <button
                  key={item.platform}
                  onClick={() => toggle(item.platform)}
                  className={`${selected.includes(item.platform) ? "selected" : ""} connector-card`}
                >
                  <span>
                    {item.configured ? <CheckCircle2 className="ready" /> : <XCircle />}
                    <strong>{labels[item.platform] ?? item.platform}</strong>
                  </span>
                  <small>{item.description}</small>
                  <em>{item.configured ? "Configured & Live" : `Needs ${item.credential_fields.join(", ")}`}</em>
                </button>
              ))}
            </div>
            <form className="ingestion-form" onSubmit={ingest}>
              <label>
                Analysis topic
                <select
                  value={topicSlug}
                  onChange={(event) => {
                    const slug = event.target.value;
                    setTopicSlug(slug);
                    const topic = topics.find((item) => item.slug === slug);
                    if (topic) setQuery(topic.title);
                  }}
                >
                  {topics.map((topic) => (
                    <option value={topic.slug} key={topic.slug}>
                      {topic.title}
                    </option>
                  ))}
                  {topics.length === 0 && <option value="custom">General Discourse</option>}
                </select>
              </label>
              <label>
                Topic query
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  required
                  minLength={2}
                />
              </label>
              {connectors
                .filter((item) => selected.includes(item.platform) && item.requires_targets)
                .map((item) => (
                  <label key={item.platform}>
                    {labels[item.platform]} post/media IDs
                    <input
                      value={targets[item.platform]}
                      onChange={(event) =>
                        setTargets((current) => ({
                          ...current,
                          [item.platform]: event.target.value,
                        }))
                      }
                      placeholder="Comma-separated authorized IDs"
                      required
                    />
                  </label>
                ))}
              <button className="red-button" disabled={running}>
                {running ? <LoaderCircle className="spin" /> : <Play />}
                {running ? "Collecting and streaming…" : "Run Selected Ingestion"}
              </button>
            </form>
            <div className="automation-strip">
              <div>
                <strong>Automatic collection daemon</strong>
                <small>
                  {automation?.enabled
                    ? `Every ${automation.interval_minutes} minutes`
                    : "Ready and active"}
                  {" · "}
                  {automation?.configured_platforms.length
                    ? automation.configured_platforms.map((item) => labels[item] ?? item).join(", ")
                    : "all public collectors active"}
                </small>
              </div>
              <button className="red-button" onClick={runAuto} disabled={running}>
                <RefreshCw size={14} /> Run collection pass now
              </button>
            </div>
            {message && (
              <div className="source-message">
                <AlertTriangle />
                {message}
              </div>
            )}
          </section>

          <section className="panel model-panel">
            <h2>Model & Classification Engine Truth Status</h2>
            {models && (
              <>
                <div className="model-status">
                  <FlaskConical />
                  <div>
                    <strong>{models.sentiment.model}</strong>
                    <span
                      className={
                        models.sentiment.active_provider === "local_muril"
                          ? "live-model"
                          : "fallback-model"
                      }
                    >
                      {models.sentiment.active_provider.replaceAll("_", " ")}
                    </span>
                  </div>
                </div>
                <p>{models.sentiment.model_card_note}</p>
                <div className="dimension-list">
                  <span>
                    <b>Sentiment</b> Sarcasm-aware (Pol-Clash) + VADER / MuRIL
                  </span>
                  <span>
                    <b>Stance</b> Support / oppose / question / neutral
                  </span>
                  <span>
                    <b>Safety</b> Clean / toxic / hate
                  </span>
                  <span>
                    <b>Language</b> Hindi (Devanagari) / Hinglish / English
                  </span>
                </div>
              </>
            )}
          </section>
        </div>

        {/* Comment Classification Lab */}
        <section className="panel classifier-lab">
          <div>
            <h2>Comment Classification & Sarcasm Lab</h2>
            <p>Test Devanagari, English or Romanised Hinglish. Sarcasm polarity-clash is evaluated before sentiment inference.</p>
          </div>
          <textarea value={sample} onChange={(event) => setSample(event.target.value)} />
          <button className="red-button" onClick={classify} disabled={classifying}>
            {classifying ? <LoaderCircle className="spin" /> : <FlaskConical />} Analyse comment
          </button>
          {classification && (
            <div className="classification-result">
              {[
                "language",
                "sentiment",
                "is_sarcastic",
                "sarcasm_confidence",
                "stance",
                "safety",
                "signal_classification",
                "signal_quality",
                "influence_score",
              ].map((key) => (
                <span key={key}>
                  <small>{key.replaceAll("_", " ")}</small>
                  <b>{String(classification[key] ?? "—")}</b>
                </span>
              ))}
              <p>Model: {String(classification.model_name)}</p>
            </div>
          )}
        </section>

        {/* Ingestion Jobs History */}
        <section className="panel jobs-panel">
          <h2>Recent Streaming & Ingestion Jobs</h2>
          {jobs.length ? (
            <div>
              {jobs.slice(0, 8).map((job) => (
                <article key={job.job_id}>
                  <span className={job.status}>{job.status}</span>
                  <strong>{job.platforms.map((item) => labels[item] ?? item).join(", ")}</strong>
                  <small>{job.query}</small>
                  <em>
                    {Object.entries(job.results)
                      .map(([platform, value]) => `${labels[platform] ?? platform}: ${value.stored}/${value.fetched}`)
                      .join(" · ") || Object.values(job.errors).join(" · ")}
                  </em>
                </article>
              ))}
            </div>
          ) : (
            <div className="data-empty">
              <strong>No manual ingestion jobs in current run</strong>
              <p>Trigger a run above to stream signals across platforms.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
