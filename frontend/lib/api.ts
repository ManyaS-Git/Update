import type { Driver, PublicVoice, Story, Topic, TrendPoint, SocialPost } from "@/types";

export const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";

const titleCase = (value: string) =>
  value.toLowerCase().replace(/(^|_)(\w)/g, (_, space, letter) => `${space ? " " : ""}${letter.toUpperCase()}`);

const slugToTitle = (slug: string) =>
  slug.replace(/-/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

/** Clean placeholder schema when awaiting data collection — no hardcoded demo values. */
export function buildBlankTopic(slug: string, title?: string): Topic {
  const effectiveTitle = title || slugToTitle(slug);
  return {
    slug,
    title: effectiveTitle,
    subtitle: "Real-time conversation intelligence",
    preview: true,
    totalConversations: 0,
    updated: "Awaiting stream signals",
    sentiment: { negative: 0, neutral: 0, positive: 0 },
    sentimentChange: 0,
    insight: `Intelligence for “${effectiveTitle}” will dynamically populate as live social and news streams enter the pipeline.`,
    audience: {
      geography: "Awaiting live location signals",
      language: "Awaiting streaming data",
      age: "Not available from public metadata",
      ageConfidence: "Unavailable",
      interests: "Awaiting keyword clustering",
      topics: [],
      platform: "Awaiting live connector data",
    },
    drivers: [],
    voices: [],
    trends: [],
    confidence: {
      sources: [],
      qualified: 0,
      lowSignal: 0,
      level: "Awaiting Data",
    },
    network: { nodes: [], edges: [] },
  };
}

async function getJson<T>(path: string): Promise<T> {
  const url = `${API_URL}${path}`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

type Meta = {
  slug: string;
  title: string;
  subtitle: string;
  image?: string;
  category?: string;
  demo?: boolean;
  total_conversations: number;
  updated: string;
};

type Sentiment = {
  negative: number;
  neutral: number;
  positive: number;
  change_last_6h: number;
  qualified_conversations?: number;
};

type Audience = {
  geography: { value: string };
  language: { distribution: Record<string, number> };
  age_bracket: { value: string; confidence: string };
  interest_groups: string[];
  key_topics?: string[];
  leading_platform?: string;
};

type TrendApi = { time: string; volume: number; negative: number }[];
type DriverApi = { title: string; description: string; status: string }[];
type VoiceApi = { quote: string; label: string; stance?: string; source?: string }[];
type Confidence = {
  level: string;
  sources: string[];
  qualified_conversations: number;
  low_signal_excluded_or_downweighted: number;
};
type Brief = { insight: string; what_changed?: string; what_is_rising?: string; what_to_watch?: string };
type Network = {
  nodes: { id: string; label: string; centrality?: number; group?: string; size?: number }[];
  edges: { source: string; target: string; weight: number }[];
};

/** Aggregates the independent backend analytics endpoints into the unified Topic model. */
export async function getTopic(slug: string): Promise<Topic | null> {
  try {
    const [meta, sentiment, audience, trends, drivers, voices, network, confidence, brief] = await Promise.all([
      getJson<Meta>(`/api/topics/${slug}`),
      getJson<Sentiment>(`/api/topics/${slug}/sentiment`),
      getJson<Audience>(`/api/topics/${slug}/audience`),
      getJson<TrendApi>(`/api/topics/${slug}/trends`),
      getJson<DriverApi>(`/api/topics/${slug}/drivers`),
      getJson<VoiceApi>(`/api/topics/${slug}/voices`),
      getJson<Network>(`/api/topics/${slug}/network`),
      getJson<Confidence>(`/api/topics/${slug}/confidence`),
      getJson<Brief>(`/api/topics/${slug}/brief`),
    ]);

    const language =
      Object.entries(audience.language.distribution).sort((a, b) => b[1] - a[1])[0]?.[0] ??
      "Awaiting streaming data";

    const mappedTrends: TrendPoint[] = trends.map((point) => ({
      time: point.time,
      volume: point.volume,
      sentiment: point.negative,
    }));

    const mappedDrivers: Driver[] = drivers.map((driver) => ({
      title: driver.title,
      description: driver.description,
      status: titleCase(driver.status) as Driver["status"],
    }));

    const mappedVoices: PublicVoice[] = voices.map((voice) => ({
      quote: voice.quote,
      label: voice.source ? `${voice.label} · ${voice.source}` : voice.label,
      tone:
        voice.stance === "supportive"
          ? "supporting"
          : voice.stance === "opposing"
          ? "concerned"
          : "neutral",
    }));

    const rawAge = audience.age_bracket.value ?? "";
    const age = rawAge && /^\d/.test(rawAge) ? `${rawAge} years` : rawAge;

    return {
      slug: meta.slug,
      title: meta.title,
      subtitle: meta.subtitle,
      image: meta.image,
      category: meta.category,
      preview: Boolean(meta.demo && meta.total_conversations === 0),
      totalConversations: meta.total_conversations,
      updated: meta.updated,
      sentiment: {
        negative: sentiment.negative,
        neutral: sentiment.neutral,
        positive: sentiment.positive,
      },
      sentimentChange: sentiment.change_last_6h,
      insight: brief.insight,
      audience: {
        geography: audience.geography.value,
        language,
        age,
        ageConfidence: audience.age_bracket.confidence,
        interests: audience.interest_groups.join(" & ") || "Awaiting signals",
        topics: audience.key_topics ?? [],
        platform: audience.leading_platform ?? "Multi-platform",
      },
      drivers: mappedDrivers,
      voices: mappedVoices,
      trends: mappedTrends,
      confidence: {
        sources: confidence.sources,
        qualified: confidence.qualified_conversations,
        lowSignal: confidence.low_signal_excluded_or_downweighted,
        level: confidence.level,
      },
      network: {
        nodes: (network.nodes || []).map((node) => ({
          id: node.id,
          label: node.label,
          group: node.group ?? "dynamic",
          size: node.size ?? Math.max(20, Math.round((node.centrality ?? 0.5) * 50)),
        })),
        edges: network.edges || [],
      },
    };
  } catch {
    return buildBlankTopic(slug);
  }
}

export async function askAnalyst(topicSlug: string, question: string) {
  const response = await fetch(`${CLIENT_API_URL}/api/ai/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic_slug: topicSlug, question }),
  });
  if (!response.ok) throw new Error("The analyst is temporarily unavailable");
  return response.json() as Promise<{
    answer: string;
    evidence: string[];
    confidence: string;
    last_updated: string;
  }>;
}

async function clientJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${CLIENT_API_URL}${path}`, init);
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

export const getStories = (path = "/api/stories") => clientJson<Story[]>(path);
export const refreshLatestNews = (limit = 12) =>
  clientJson<{ provider: string; received: number; added: number; stories: Story[] }>(
    `/api/news/refresh?limit=${limit}`,
    { method: "POST" }
  );
export const getStory = (id: string) => clientJson<Story>(`/api/stories/${id}`);
export const getBookmarks = () => clientJson<Story[]>("/api/bookmarks");
export const getFeed = () => clientJson<Story[]>("/api/feed");
export const searchContent = (query: string) =>
  clientJson<{
    query: string;
    stories: Story[];
    topics: { slug: string; title: string; subtitle: string; updated: string }[];
  }>(`/api/search?q=${encodeURIComponent(query)}`);
export const setBookmark = (id: string, enabled: boolean) =>
  clientJson<{ story_id: string; bookmarked: boolean }>(`/api/bookmarks/${id}`, {
    method: enabled ? "POST" : "DELETE",
  });
export const getPreferences = () =>
  clientJson<{ notifications_enabled: boolean }>("/api/preferences");
export const setNotifications = (enabled: boolean) =>
  clientJson<{ notifications_enabled: boolean }>("/api/preferences/notifications", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled }),
  });

export interface ConnectorStatus {
  platform: string;
  configured: boolean;
  description: string;
  credential_fields: string[];
  discovery_supported: boolean;
  requires_targets: boolean;
}

export interface IngestionJob {
  job_id: string;
  topic_slug: string;
  platforms: string[];
  query: string;
  status: string;
  results: Record<string, { fetched: number; stored: number }>;
  errors: Record<string, string>;
  started_at: string;
  completed_at: string | null;
}

export interface TopicSummary {
  slug: string;
  title: string;
  subtitle: string;
  total_conversations: number;
  updated: string;
  demo: boolean;
}

export interface NarrativeSummary {
  id: number;
  topic_slug: string;
  title: string;
  classification: "emerging" | "popular" | "declining";
  velocity: number;
  momentum: number;
  volume: number;
  sentiment_balance: number;
  dominant_platform: string;
  last_updated: string;
}

export interface NarrativesResponse {
  emerging: NarrativeSummary[];
  popular: NarrativeSummary[];
}

export interface KafkaStatusResponse {
  status: "connected" | "degraded" | "unavailable";
  bootstrap_servers: string;
  topics: {
    social_raw: string;
    social_high_signal: string;
    social_analytics: string;
  };
  in_memory_fallback: {
    active: boolean;
    queue_size: number;
  };
}

export interface TopicAnalysisResponse {
  topic: string;
  total_signals: number;
  high_signal_ratio: number;
  sentiment: {
    positive: number;
    negative: number;
    neutral: number;
  };
  top_keywords: {
    term: string;
    c_tfidf: number;
  }[];
  recent_high_signal_samples: {
    text: string;
    platform: string;
    signal_quality: number;
    sentiment: string;
  }[];
}

export interface AutomationStatus {
  status: string;
  enabled: boolean;
  interval_minutes: number;
  configured_platforms: string[];
  requested_platforms: string[];
  credential_setup_required: boolean;
  last_started: string | null;
  last_completed: string | null;
  topics_processed: number;
  comments_stored: number;
  errors: Record<string, unknown>;
}

export const getConnectors = () => clientJson<ConnectorStatus[]>("/api/connectors");
export const getTopics = () => clientJson<TopicSummary[]>("/api/topics");
export const getNarratives = () => clientJson<NarrativesResponse>("/api/topics/narratives");
export const getPosts = (limit = 30, topic?: string) =>
  clientJson<SocialPost[]>(`/api/posts?limit=${limit}${topic ? `&topic=${encodeURIComponent(topic)}` : ""}`);
export const getKafkaStatus = () => clientJson<KafkaStatusResponse>("/api/kafka/status");
export const analyzeTopicQuery = (query: string, max_items = 25) =>
  clientJson<TopicAnalysisResponse>("/api/analyze/topic", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, max_items }),
  });
export const getModelStatus = () =>
  clientJson<{
    sentiment: {
      requested_provider: string;
      active_provider: string;
      model: string;
      local_runtime_installed: boolean;
      endpoint_configured: boolean;
      last_error: string | null;
      model_card_note: string;
    };
    safety: { active_provider: string; model: string; note: string };
  }>("/api/models/status");
export const getIngestionJobs = () => clientJson<IngestionJob[]>("/api/ingestion/jobs");
export const getAutomationStatus = () => clientJson<AutomationStatus>("/api/ingestion/automation/status");
export const runAutomationNow = () => clientJson<AutomationStatus>("/api/ingestion/automation/run-now", { method: "POST" });
export const runIngestion = (payload: {
  topic_slug: string;
  query: string;
  platforms: string[];
  targets: Record<string, string[]>;
  max_items: number;
}) =>
  clientJson<{
    job_id: string;
    status: string;
    results: Record<string, { fetched: number; stored: number }>;
    errors: Record<string, string>;
  }>("/api/ingestion/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
export const getCommentSummary = () => clientJson<Record<string, unknown>>("/api/comments/summary");
export const classifyComment = (text: string) =>
  clientJson<Record<string, unknown>>("/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, context: "public discourse", platform: "manual" }),
  });
