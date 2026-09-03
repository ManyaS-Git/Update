export type SentimentKey = "negative" | "neutral" | "positive";

export interface Story {
  id: string;
  title: string;
  category: string;
  time: string;
  published_at?: string;
  image: string;
  imagePosition?: string;
  live?: boolean;
  summary?: string;
  topic_slug?: string;
  source_status?: string;
  bookmarked?: boolean;
}

export interface TrendPoint {
  time: string;
  volume: number;
  sentiment: number;
}

export interface Driver {
  title: string;
  description: string;
  status: "Top concern" | "Rising" | "Stable";
}

export interface PublicVoice {
  quote: string;
  label: string;
  tone: "supporting" | "concerned" | "neutral";
}

export interface Topic {
  slug: string;
  title: string;
  subtitle: string;
  image?: string;
  category?: string;
  preview?: boolean;
  totalConversations: number;
  updated: string;
  sentiment: Record<SentimentKey, number>;
  sentimentChange: number;
  insight: string;
  audience: {
    geography: string;
    language: string;
    age: string;
    ageConfidence: string;
    interests: string;
    topics: string[];
    platform: string;
  };
  drivers: Driver[];
  voices: PublicVoice[];
  trends: TrendPoint[];
  confidence: {
    sources: string[];
    qualified: number;
    lowSignal: number;
    level: string;
  };
  network: {
    nodes: { id: string; label: string; group: string; size: number }[];
    edges: { source: string; target: string; weight: number }[];
  };
}

export interface SocialPost {
  id: string;
  platform: string;
  author: string;
  author_id?: string;
  content: string;
  timestamp: string;
  published_at?: string;
  likes: number;
  comments: number;
  shares: number;
  views?: number;
  is_verified: boolean;
  topic_slug?: string;
  sentiment?: "positive" | "negative" | "neutral";
  sentiment_confidence?: number;
  url?: string;
  language?: string;
  emotion?: string;
  stance?: string;
  signal_quality?: number;
}

export interface InsightCard {
  insight_id: string;
  topic_slug: string;
  priority_score: number;
  category: string;
  title: string;
  insight: string;
  evidence: string[];
  why_it_matters: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  source_signals: string[];
  model_name: string;
}

export interface ModelTransparencyItem {
  model: string;
  purpose: string;
  status: string;
  confidence: string;
  details: string;
}

export interface PropagationStep {
  platform: string;
  first_seen: string;
  delay_minutes: number;
  volume: number;
  engagement: number;
}

export interface PropagationData {
  origin_platform: string | null;
  origin_timestamp: string | null;
  path_summary: string;
  platforms_involved: string[];
  steps: PropagationStep[];
  has_sufficient_timeline_evidence: boolean;
}

export interface IntelligenceBrief {
  title: string;
  generated_at: string;
  executive_summary: string[];
  emerging_narratives: {
    topic_id: number;
    label: string;
    volume: number;
    momentum_score: number;
    status: string;
    keywords: string[];
  }[];
  sentiment_overview: Record<string, number>;
  emotion_overview: Record<string, number>;
  stance_overview: {
    support_pct: number;
    oppose_pct: number;
    neutral_pct: number;
    unclear_pct: number;
  };
  audience_demographics: {
    inferred_age_bracket: string;
    dominant_language: string;
    estimated_professional_interest: string;
  };
  influencers: {
    author: string;
    pagerank_score: number;
    rank: number;
    group: string;
    platform: string;
  }[];
  network_summary: {
    total_nodes: number;
    total_edges: number;
    lead_amplifier: string;
  };
  risk_signals: {
    level: string;
    score: number;
    reason: string;
    trend: string;
  }[];
  cross_platform_movement: {
    origin: string;
    timeline_summary: string;
    steps: PropagationStep[];
  };
  key_evidence: string[];
  analyst_assessment: string;
  recommended_attention: string;
}
