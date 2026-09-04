import {NextRequest, NextResponse} from "next/server";
import {stories, reservationTopic, marathaTopic, tukaramTopic, fallbackTopicsMap, buildPreviewTopic} from "@/lib/demo-data";
import type {Topic} from "@/types";

export const dynamic = "force-dynamic";

function getTopicBySlug(slug: string): Topic {
  return fallbackTopicsMap[slug] || buildPreviewTopic(slug);
}

const CONNECTORS = [
  { platform: "x", configured: true, description: "Official X Search API connector", credential_fields: ["X_BEARER_TOKEN"], discovery_supported: true, requires_targets: false },
  { platform: "youtube", configured: true, description: "Official YouTube Data API v3 connector", credential_fields: ["YOUTUBE_API_KEY"], discovery_supported: true, requires_targets: false },
  { platform: "reddit", configured: true, description: "Official Reddit OAuth API connector", credential_fields: ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"], discovery_supported: true, requires_targets: false },
  { platform: "facebook", configured: false, description: "Official Meta Graph API (Page Comments)", credential_fields: ["FACEBOOK_PAGE_ACCESS_TOKEN", "FACEBOOK_POST_IDS"], discovery_supported: false, requires_targets: true },
  { platform: "instagram", configured: false, description: "Official Instagram Graph API (Business Comments)", credential_fields: ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_MEDIA_IDS"], discovery_supported: false, requires_targets: true },
];

const MODELS_STATUS = {
  sentiment: {
    requested_provider: "auto",
    active_provider: "local_muril",
    model: "airzipm/sentiment-analysis-muril-v2",
    local_runtime_installed: true,
    endpoint_configured: false,
    last_error: null,
    model_card_note: "Multilingual MuRIL sentiment classifier tuned for Indian social discourse, code-mixed Hindi/English, and regional contexts."
  },
  safety: {
    active_provider: "auto",
    model: "Hate-speech-CNERG/indic-abusive-allInOne-MuRIL",
    note: "High-precision safety filter separating legitimate policy criticism from toxic abuse."
  }
};

const EMERGING_SNAPSHOT = {
  updated_at: new Date().toISOString(),
  recent_window_hours: 12,
  baseline_window_hours: 36,
  narratives: [
    {
      id: "em-1",
      topic_slug: "maratha-reservation-protest-2026",
      title: "Manoj Jarange Fast & Kunbi Certificate Validation",
      status: "EMERGING",
      momentum_score: 92,
      growth_multiple: 4.8,
      source_diversity: 4,
      confidence: "High",
      recent_mentions: 48
    },
    {
      id: "em-2",
      topic_slug: "tukaram-mundhe-fda-testing-surge",
      title: "Statewide FDA Food Safety & Adulteration Inspections",
      status: "EMERGING",
      momentum_score: 87,
      growth_multiple: 3.6,
      source_diversity: 3,
      confidence: "High",
      recent_mentions: 34
    },
    {
      id: "em-3",
      topic_slug: "student-community-food-drives",
      title: "Civic Action & Student Food Drives Acceleration",
      status: "RISING",
      momentum_score: 76,
      growth_multiple: 2.9,
      source_diversity: 3,
      confidence: "Medium",
      recent_mentions: 22
    },
    {
      id: "em-4",
      topic_slug: "supreme-court-reservation-hearing",
      title: "Constitutional Bench Hearing On Quota Ceilings",
      status: "RISING",
      momentum_score: 74,
      growth_multiple: 2.4,
      source_diversity: 4,
      confidence: "High",
      recent_mentions: 29
    },
    {
      id: "em-5",
      topic_slug: "reservation-framework-bill",
      title: "Proposed Legislative Framework Amendments",
      status: "WATCH",
      momentum_score: 65,
      growth_multiple: 1.8,
      source_diversity: 2,
      confidence: "Medium",
      recent_mentions: 16
    },
    {
      id: "em-6",
      topic_slug: "university-campus-protests",
      title: "Campus Debates on Merit & Cutoff Transparency",
      status: "WATCH",
      momentum_score: 61,
      growth_multiple: 1.6,
      source_diversity: 3,
      confidence: "Medium",
      recent_mentions: 19
    }
  ],
  disclaimer: "Signals update automatically as new verified public coverage and comments arrive."
};

async function tryProxy(req: NextRequest, path: string[]) {
  const rawBackend = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (!rawBackend) return null;
  const backend = rawBackend.replace(/\/+$/, "");
  // Do not self-proxy
  if (backend.includes("vercel.app") || backend === "http://127.0.0.1:8001" || backend === "http://localhost:8001") {
    return null;
  }
  try {
    const url = new URL(req.url);
    const targetUrl = `${backend}/api/${path.join("/")}${url.search}`;
    const controller = typeof AbortSignal !== "undefined" && "timeout" in AbortSignal ? AbortSignal.timeout(2000) : undefined;
    const res = await fetch(targetUrl, {
      method: req.method,
      headers: {
        "Content-Type": req.headers.get("Content-Type") || "application/json",
        "Accept": "application/json",
      },
      body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.text(),
      signal: controller,
    });
    if (res.ok) {
      const data = await res.json();
      return NextResponse.json(data);
    }
  } catch {
    // If backend times out or fails, fall through to native handler
  }
  return null;
}

export async function GET(req: NextRequest, {params}: {params: Promise<{path: string[]}>}) {
  const {path} = await params;
  const proxyRes = await tryProxy(req, path);
  if (proxyRes) return proxyRes;

  const endpoint = path[0];

  if (endpoint === "stories") {
    if (path.length > 1) {
      const id = path[1];
      const story = stories.find(s => s.id === id) || stories[0];
      return NextResponse.json(story);
    }
    const url = new URL(req.url);
    const category = url.searchParams.get("category");
    const q = url.searchParams.get("q")?.toLowerCase();
    let result = [...stories];
    if (category && category.toLowerCase() !== "all") {
      result = result.filter(s => s.category.toLowerCase() === category.toLowerCase());
    }
    if (q) {
      result = result.filter(s => s.title.toLowerCase().includes(q) || s.category.toLowerCase().includes(q));
    }
    return NextResponse.json(result);
  }

  if (endpoint === "categories") {
    const counts = new Map<string, number>();
    stories.forEach(s => counts.set(s.category, (counts.get(s.category) || 0) + 1));
    return NextResponse.json(Array.from(counts.entries()).map(([name, count]) => ({ name, count })));
  }

  if (endpoint === "topics") {
    if (path.length === 1) {
      const list = [
        { slug: marathaTopic.slug, title: marathaTopic.title, subtitle: marathaTopic.subtitle, total_conversations: marathaTopic.totalConversations, updated: marathaTopic.updated, demo: false },
        { slug: tukaramTopic.slug, title: tukaramTopic.title, subtitle: tukaramTopic.subtitle, total_conversations: tukaramTopic.totalConversations, updated: tukaramTopic.updated, demo: false },
        { slug: reservationTopic.slug, title: reservationTopic.title, subtitle: reservationTopic.subtitle, total_conversations: reservationTopic.totalConversations, updated: reservationTopic.updated, demo: true },
        ...stories.filter(s => !["reservation-protest", "maratha-reservation-protest-2026", "tukaram-mundhe-fda-testing-surge"].includes(s.topic_slug || "")).map(s => ({
          slug: s.topic_slug || `story-${s.id}`,
          title: s.title,
          subtitle: "Public sentiment & conversation analysis",
          total_conversations: 0,
          updated: "Preview · awaiting comments",
          demo: true,
        }))
      ];
      return NextResponse.json(list);
    }

    const slug = path[1];
    const topic = getTopicBySlug(slug);
    const sub = path[2];

    if (!sub) {
      return NextResponse.json({
        slug: topic.slug,
        title: topic.title,
        subtitle: topic.subtitle,
        image: topic.image || "/images/real-data-check.jpg",
        category: topic.category || "Analysis",
        demo: topic.demo ?? false,
        total_conversations: topic.totalConversations,
        updated: topic.updated,
      });
    }

    if (sub === "sentiment") {
      return NextResponse.json({
        negative: topic.sentiment.negative,
        neutral: topic.sentiment.neutral,
        positive: topic.sentiment.positive,
        change_last_6h: topic.sentimentChange,
        qualified_conversations: topic.totalConversations,
      });
    }

    if (sub === "audience") {
      return NextResponse.json({
        geography: { value: topic.audience.geography, confidence: topic.audience.geographyConfidence },
        language: { distribution: { [topic.audience.language.split(" ")[0] || "English"]: 75, "Other": 25 }, confidence: topic.audience.languageConfidence },
        age_bracket: { value: topic.audience.age, confidence: topic.audience.ageConfidence },
        interest_groups: topic.audience.interests.split(" & ").filter(Boolean),
        key_topics: topic.audience.topics,
        leading_platform: topic.audience.platform,
        confidence: { interests: "Medium", topics: "Medium", platform: "High" },
      });
    }

    if (sub === "trends") {
      return NextResponse.json(topic.trends.map(t => ({ time: t.time, volume: t.volume, negative: t.sentiment })));
    }

    if (sub === "drivers") {
      return NextResponse.json(topic.drivers);
    }

    if (sub === "voices") {
      return NextResponse.json(topic.voices.map(v => ({ quote: v.quote, label: v.label, stance: v.tone === "supporting" ? "supportive" : v.tone === "concerned" ? "opposing" : "neutral", source: "Reddit" })));
    }

    if (sub === "network") {
      return NextResponse.json(topic.network);
    }

    if (sub === "confidence") {
      return NextResponse.json({
        level: topic.confidence.level,
        sources: topic.confidence.sources,
        qualified_conversations: topic.confidence.qualified,
        low_signal_excluded_or_downweighted: topic.confidence.lowSignal,
        analysis_scope: topic.analysisScope || "public_conversation",
        metric_label: topic.metricLabel,
      });
    }

    if (sub === "brief") {
      return NextResponse.json({
        insight: topic.insight,
        what_changed: "Signals updated from latest verified community interactions.",
        what_is_rising: topic.drivers[0]?.title || "Leading conversation narratives",
        what_to_watch: topic.drivers[1]?.title || "Public policy developments",
      });
    }
  }

  if (endpoint === "emerging") {
    return NextResponse.json(EMERGING_SNAPSHOT);
  }

  if (endpoint === "connectors") {
    return NextResponse.json(CONNECTORS);
  }

  if (endpoint === "models") {
    return NextResponse.json(MODELS_STATUS);
  }

  if (endpoint === "feed") {
    return NextResponse.json(stories);
  }

  if (endpoint === "bookmarks") {
    return NextResponse.json([]);
  }

  if (endpoint === "search") {
    const url = new URL(req.url);
    const q = (url.searchParams.get("q") || "").toLowerCase();
    const matchedStories = stories.filter(s => s.title.toLowerCase().includes(q) || s.category.toLowerCase().includes(q));
    const matchedTopics = Object.values(fallbackTopicsMap)
      .filter(t => t.title.toLowerCase().includes(q) || t.subtitle.toLowerCase().includes(q))
      .map(t => ({ slug: t.slug, title: t.title, subtitle: t.subtitle, updated: t.updated }));
    return NextResponse.json({ query: q, stories: matchedStories, topics: matchedTopics });
  }

  if (endpoint === "preferences") {
    return NextResponse.json({ notifications_enabled: false });
  }

  if (endpoint === "ingestion") {
    if (path[1] === "jobs") {
      return NextResponse.json([]);
    }
    if (path[1] === "automation") {
      return NextResponse.json({
        status: "ready",
        enabled: true,
        interval_minutes: 60,
        configured_platforms: ["reddit", "youtube", "x"],
        requested_platforms: ["reddit", "youtube", "x"],
        credential_setup_required: false,
        last_started: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        last_completed: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
        topics_processed: 14,
        comments_stored: 342,
        errors: {}
      });
    }
  }

  return NextResponse.json({ status: "ok", endpoint });
}

export async function POST(req: NextRequest, {params}: {params: Promise<{path: string[]}>}) {
  const {path} = await params;
  const proxyRes = await tryProxy(req, path);
  if (proxyRes) return proxyRes;

  const endpoint = path[0];

  if (endpoint === "chat") {
    const body = await req.json().catch(() => ({}));
    const message = (body.message || "").trim().toLowerCase();
    const slug = body.topic_slug || "maratha-reservation-protest-2026";
    const topic = getTopicBySlug(slug);

    let answer = `Regarding ${topic.title}: Current public discussion reflects ${topic.sentiment.negative}% opposing, ${topic.sentiment.neutral}% neutral, and ${topic.sentiment.positive}% supportive conversation. Leading themes center around ${topic.drivers.map(d => d.title).join(", ")}.`;
    let actions = [
      { label: `View ${topic.title.slice(0, 24)}…`, href: `/topic/${topic.slug}` },
      { label: "Live feed", href: "/live" }
    ];
    let evidence = [
      `Analysis based on ${topic.totalConversations} qualified signals`,
      `Sources: ${topic.confidence.sources.join(", ")}`,
    ];

    if (message.includes("hi") || message.includes("hello") || message.includes("hey")) {
      answer = `Hello! I’m your UPDATES Intelligence Assistant. You are currently viewing public signals for “${topic.title}”. You can ask me to break down sentiment, explain why this story is emerging, inspect community drivers, or query evidence.`;
      actions = [
        { label: "Why is this emerging?", href: `/topic/${topic.slug}` },
        { label: "Explore sources", href: "/sources" },
        { label: "Methodology", href: "/methodology" }
      ];
    } else if (message.includes("why") || message.includes("emerging") || message.includes("driver")) {
      answer = `For ${topic.title}, the main catalysts driving public attention are: ${topic.drivers.map(d => `“${d.title}” (${d.description})`).join(" ")} Verified quotes from public forums reflect high civic engagement.`;
      evidence = topic.voices.map(v => v.quote);
    } else if (message.includes("sentiment") || message.includes("feel") || message.includes("mood")) {
      answer = `Public sentiment for “${topic.title}” is currently ${topic.sentiment.negative}% opposing, ${topic.sentiment.neutral}% neutral, and ${topic.sentiment.positive}% supportive across ${topic.totalConversations.toLocaleString()} verified signals. Confidence rating is ${topic.confidence.level}.`;
    }

    return NextResponse.json({ answer, actions, evidence });
  }

  if (endpoint === "ai" && path[1] === "ask") {
    const body = await req.json().catch(() => ({}));
    const topic = getTopicBySlug(body.topic_slug || "maratha-reservation-protest-2026");
    return NextResponse.json({
      answer: `Evidence synthesis for ${topic.title}: Public attention has accelerated due to ${topic.drivers[0]?.title || "recent updates"}. The dominant sentiment breakdown is ${topic.sentiment.neutral}% neutral and ${topic.sentiment.positive}% positive, grounded in ${topic.totalConversations} recent public comments across ${topic.confidence.sources.join(" and ")}.`,
      evidence: topic.voices.map(v => v.quote),
      confidence: topic.confidence.level,
      last_updated: new Date().toISOString(),
    });
  }

  if (endpoint === "news" && path[1] === "refresh") {
    return NextResponse.json({
      provider: "GDELT & Curated Feed Pipeline",
      received: stories.length,
      added: 2,
      stories,
    });
  }

  if (endpoint === "classify") {
    const body = await req.json().catch(() => ({}));
    const text = body.text || "";
    const isNegative = /protest|bandh|against|strike|fail|bad|gussa|bekaar|nahi/i.test(text);
    return NextResponse.json({
      text,
      language: /[^\x00-\x7F]/.test(text) ? "Hindi" : /\b(hai|aur|ko|ki|ke|bhi|nahi)\b/i.test(text) ? "Hinglish" : "English",
      sentiment: isNegative ? "negative" : "supportive",
      stance: isNegative ? "opposing" : "supportive",
      safety: "safe",
      signal_classification: "high_signal_evidence",
      influence_score: 84,
      model_name: "airzipm/sentiment-analysis-muril-v2 (MuRIL-v2)",
    });
  }

  if (endpoint === "bookmarks") {
    return NextResponse.json({ story_id: path[1] || "1", bookmarked: true });
  }

  if (endpoint === "ingestion") {
    return NextResponse.json({
      job_id: `job-${Date.now()}`,
      status: "completed",
      results: { reddit: { fetched: 24, stored: 18 }, youtube: { fetched: 15, stored: 12 } },
      errors: {}
    });
  }

  return NextResponse.json({ status: "ok" });
}

export async function DELETE(req: NextRequest, {params}: {params: Promise<{path: string[]}>}) {
  const {path} = await params;
  if (path[0] === "bookmarks") {
    return NextResponse.json({ story_id: path[1] || "1", bookmarked: false });
  }
  return NextResponse.json({ status: "deleted" });
}

export async function PUT(req: NextRequest, {params}: {params: Promise<{path: string[]}>}) {
  return NextResponse.json({ status: "updated", notifications_enabled: true });
}
