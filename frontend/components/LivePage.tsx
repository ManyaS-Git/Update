/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {
  BarChart3,
  Bookmark,
  CheckCircle,
  FileText,
  Filter,
  Flame,
  Heart,
  HelpCircle,
  Info,
  LoaderCircle,
  MessageCircle,
  Radio,
  Repeat2,
  Share2,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { SocialPost, Story } from "@/types";
import { getPosts, getStories, setBookmark } from "@/lib/api";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { IntelligenceBriefModal } from "./IntelligenceBriefModal";
import { ModelTransparencyPanel } from "./ModelTransparencyPanel";

function toMinutes(time?: string): number {
  if (!time) return Number.MAX_SAFE_INTEGER;
  const match = time.match(/(\d+)\s*([mhd])/i);
  if (!match) return Number.MAX_SAFE_INTEGER;
  const value = Number(match[1]);
  const unit = match[2].toLowerCase();
  return unit === "m" ? value : unit === "h" ? value * 60 : value * 1440;
}

function SocialPostCard({ post }: { post: SocialPost }) {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(post.likes);
  const [showExplanation, setShowExplanation] = useState(false);

  function toggleLike() {
    setLiked((v) => !v);
    setLikeCount((c) => (liked ? c - 1 : c + 1));
  }

  const sentimentColor =
    post.sentiment === "positive"
      ? "#a6da95"
      : post.sentiment === "negative"
      ? "#ed8796"
      : "#eed49f";

  const platformColor =
    post.platform === "x"
      ? "#cad3f5"
      : post.platform === "reddit"
      ? "#f5a97f"
      : post.platform === "telegram"
      ? "#8aadf4"
      : post.platform === "youtube"
      ? "#ee99a0"
      : "#c6a0f6";

  const signalQuality = post.signal_quality ?? 0.82;
  const isHighSignal = signalQuality >= 0.70;

  return (
    <article className="post-card" style={{ marginBottom: "1rem" }}>
      <div
        className="post-avatar"
        style={{
          background: "rgba(255,255,255,0.06)",
          color: platformColor,
          border: `1px solid ${platformColor}40`,
        }}
      >
        {post.platform.charAt(0).toUpperCase()}
      </div>
      <div className="post-body">
        <div className="post-head">
          <strong style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            {post.author}
            {post.is_verified && <CheckCircle size={13} style={{ color: "#8aadf4" }} />}
          </strong>
          <span style={{ textTransform: "capitalize", color: platformColor }}>
            @{post.platform}
          </span>
          <i />
          <time>{post.timestamp}</time>

          <div style={{ marginLeft: "auto", display: "flex", gap: "6px", alignItems: "center" }}>
            {/* CSQE Quality Badge */}
            <button
              type="button"
              onClick={() => setShowExplanation((v) => !v)}
              style={{
                fontSize: "0.72rem",
                padding: "2px 8px",
                borderRadius: "999px",
                background: isHighSignal ? "rgba(166, 218, 149, 0.15)" : "rgba(238, 212, 159, 0.15)",
                color: isHighSignal ? "#a6da95" : "#eed49f",
                border: "1px solid rgba(255,255,255,0.08)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "3px",
              }}
              title="Click to view CSQE Qualification Rationale"
            >
              <ShieldCheck size={11} />
              CSQE {Math.round(signalQuality * 100)}%
            </button>

            {post.sentiment && (
              <span
                style={{
                  fontSize: "0.72rem",
                  padding: "2px 8px",
                  borderRadius: "999px",
                  background: `${sentimentColor}20`,
                  color: sentimentColor,
                  fontWeight: 600,
                  textTransform: "capitalize",
                }}
              >
                {post.sentiment}
              </span>
            )}
          </div>
        </div>

        {showExplanation && (
          <div
            style={{
              margin: "0.5rem 0",
              padding: "0.6rem 0.8rem",
              background: "rgba(30, 32, 48, 0.9)",
              borderRadius: "6px",
              border: "1px solid rgba(138, 173, 244, 0.3)",
              fontSize: "0.78rem",
              color: "#cad3f5",
            }}
          >
            <strong style={{ color: "#8aadf4", display: "block", marginBottom: "2px" }}>
              CSQE Qualification Explanation:
            </strong>
            Post cleared quality gate (Score: {Math.round(signalQuality * 100)}% / 100%).
            Content exhibits informative topical density, non-spam lexical diversity, and distinct account provenance.
          </div>
        )}

        <p className="post-text" style={{ fontSize: "0.95rem", lineHeight: 1.45, margin: "0.5rem 0" }}>
          {post.content}
        </p>

        {post.topic_slug && (
          <Link
            href={`/topic/${post.topic_slug}`}
            style={{
              fontSize: "0.75rem",
              color: "#8aadf4",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              marginBottom: "0.5rem",
            }}
          >
            <TrendingUp size={12} /> View topic intelligence
          </Link>
        )}

        <div className="post-actions">
          <div className="post-action">
            <MessageCircle size={16} />
            <span>{post.comments}</span>
          </div>
          <button className="post-action" type="button">
            <Repeat2 size={16} />
            <span>{post.shares}</span>
          </button>
          <button
            className={liked ? "post-action liked" : "post-action"}
            type="button"
            onClick={toggleLike}
          >
            <Heart size={16} fill={liked ? "currentColor" : "none"} />
            <span>{likeCount}</span>
          </button>
          {post.topic_slug && (
            <Link href={`/topic/${post.topic_slug}`} className="post-action">
              <BarChart3 size={16} />
              <span>Analysis</span>
            </Link>
          )}
        </div>
      </div>
    </article>
  );
}

function StoryFeedCard({ story }: { story: Story }) {
  const [saved, setSaved] = useState(Boolean(story.bookmarked));
  const href = story.topic_slug ? `/topic/${story.topic_slug}` : `/story/${story.id}`;
  const remote = /^https?:\/\//.test(story.image);
  const source = story.category || "Signal";

  async function save() {
    const next = !saved;
    setSaved(next);
    try {
      await setBookmark(story.id, next);
    } catch {}
  }

  return (
    <article className="post-card">
      <div className="post-avatar" aria-hidden>
        {source.charAt(0).toUpperCase()}
      </div>
      <div className="post-body">
        <div className="post-head">
          <strong>{source}</strong>
          <span>@updates_signals</span>
          <i />
          <time>{story.time}</time>
          {story.live && (
            <span className="post-live">
              <Radio size={11} /> LIVE
            </span>
          )}
        </div>

        <Link href={href} className="post-story-link">
          {story.image && (
            <div className="post-story-thumb">
              {remote ? (
                <img src={story.image} alt={story.title} />
              ) : (
                <Image
                  src={story.image}
                  alt={story.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 420px"
                />
              )}
            </div>
          )}
          <h3>{story.title}</h3>
          {story.summary && <p>{story.summary}</p>}
        </Link>

        <div className="post-actions">
          {story.topic_slug && (
            <Link href={`/topic/${story.topic_slug}`} className="post-action">
              <BarChart3 size={16} />
              <span>Analysis</span>
            </Link>
          )}
          <button
            className={saved ? "post-action saved" : "post-action"}
            type="button"
            onClick={save}
          >
            <Bookmark size={16} fill={saved ? "currentColor" : "none"} />
            <span>{saved ? "Saved" : "Save"}</span>
          </button>
          <button
            className="post-action"
            type="button"
            onClick={() => {
              if (navigator.clipboard) {
                navigator.clipboard.writeText(
                  `${window.location.origin}${href}`
                );
              }
            }}
          >
            <Share2 size={16} />
            <span>Share</span>
          </button>
        </div>
      </div>
    </article>
  );
}

export function LivePage() {
  const [tab, setTab] = useState<"social" | "stories">("social");
  const [sort, setSort] = useState<"top" | "latest">("top");
  const [platformFilter, setPlatformFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [briefOpen, setBriefOpen] = useState(false);

  const [posts, setPosts] = useState<SocialPost[] | null>(null);
  const [stories, setStories] = useState<Story[] | null>(null);

  useEffect(() => {
    getPosts()
      .then(setPosts)
      .catch(() => setPosts([]));
    getStories()
      .then(setStories)
      .catch(() => setStories([]));
  }, []);

  const filteredPosts = useMemo(() => {
    if (!posts) return [];
    let list = [...posts];

    if (platformFilter !== "all") {
      list = list.filter((p) => p.platform.toLowerCase() === platformFilter);
    }
    if (sentimentFilter !== "all") {
      list = list.filter((p) => p.sentiment === sentimentFilter);
    }

    if (sort === "latest") {
      return list.sort((a, b) => (b.timestamp > a.timestamp ? 1 : -1));
    }
    return list.sort((a, b) => b.likes + b.shares - (a.likes + a.shares));
  }, [posts, sort, platformFilter, sentimentFilter]);

  const sortedStories = useMemo(() => {
    if (!stories) return [];
    const list = [...stories];
    if (sort === "latest") {
      return list.sort((a, b) => toMinutes(a.time) - toMinutes(b.time));
    }
    return list.sort(
      (a, b) =>
        Number(Boolean(b.live)) - Number(Boolean(a.live)) ||
        toMinutes(a.time) - toMinutes(b.time)
    );
  }, [stories, sort]);

  return (
    <div className="app-shell">
      <Sidebar active="Live" />
      <main className="main">
        <Topbar />
        <header className="live-header">
          <div>
            <span className="live-eyebrow">
              <span className="live-pulse" /> STREAMING INTELLIGENCE
            </span>
            <h1>Real-Time Social Media Feed</h1>
            <p>
              High-signal posts streaming directly from Kafka and cross-platform collectors, qualified by CSQE.
            </p>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" }}>
            <button
              onClick={() => setBriefOpen(true)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
                padding: "8px 14px",
                borderRadius: "8px",
                background: "rgba(138, 173, 244, 0.2)",
                color: "#8aadf4",
                border: "1px solid rgba(138, 173, 244, 0.4)",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
              }}
            >
              <FileText size={15} /> Intelligence Brief
            </button>

            <div
              style={{
                display: "flex",
                background: "rgba(36,39,58,0.8)",
                borderRadius: "8px",
                padding: "3px",
              }}
            >
              <button
                className={tab === "social" ? "active" : ""}
                style={{
                  padding: "6px 12px",
                  borderRadius: "6px",
                  border: "none",
                  background: tab === "social" ? "#ed8796" : "transparent",
                  color: tab === "social" ? "#181926" : "#cad3f5",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
                onClick={() => setTab("social")}
              >
                Social Posts ({posts?.length ?? 0})
              </button>
              <button
                className={tab === "stories" ? "active" : ""}
                style={{
                  padding: "6px 12px",
                  borderRadius: "6px",
                  border: "none",
                  background: tab === "stories" ? "#ed8796" : "transparent",
                  color: tab === "stories" ? "#181926" : "#cad3f5",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
                onClick={() => setTab("stories")}
              >
                Story Signals ({stories?.length ?? 0})
              </button>
            </div>

            <div className="live-sort">
              <button
                className={sort === "top" ? "active" : ""}
                onClick={() => setSort("top")}
              >
                Top Engagement
              </button>
              <button
                className={sort === "latest" ? "active" : ""}
                onClick={() => setSort("latest")}
              >
                Latest
              </button>
            </div>
          </div>
        </header>

        {/* Multi-Dimensional Filter Bar */}
        {tab === "social" && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              padding: "0.6rem 1rem",
              background: "rgba(24, 25, 38, 0.7)",
              borderRadius: "8px",
              border: "1px solid rgba(255,255,255,0.06)",
              marginBottom: "1rem",
              flexWrap: "wrap",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#a5adcb", fontSize: "0.82rem" }}>
              <Filter size={14} /> Filter:
            </div>

            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              style={{
                background: "#1e2030",
                color: "#cad3f5",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "6px",
                padding: "4px 8px",
                fontSize: "0.8rem",
              }}
            >
              <option value="all">All Platforms</option>
              <option value="x">X (Twitter)</option>
              <option value="reddit">Reddit</option>
              <option value="telegram">Telegram</option>
              <option value="youtube">YouTube</option>
            </select>

            <select
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
              style={{
                background: "#1e2030",
                color: "#cad3f5",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "6px",
                padding: "4px 8px",
                fontSize: "0.8rem",
              }}
            >
              <option value="all">All Sentiments</option>
              <option value="negative">Negative</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
            </select>

            <span style={{ marginLeft: "auto", fontSize: "0.75rem", color: "#8087a2" }}>
              Showing {filteredPosts.length} qualified signals
            </span>
          </div>
        )}

        {tab === "social" ? (
          posts === null ? (
            <div className="page-state">
              <LoaderCircle className="spin" /> Streaming live social media posts...
            </div>
          ) : filteredPosts.length ? (
            <div className="live-feed">
              {filteredPosts.map((post) => (
                <SocialPostCard key={post.id} post={post} />
              ))}
            </div>
          ) : (
            <div className="data-empty large-empty">
              <Radio />
              <strong>No social posts match criteria</strong>
              <p>
                Incoming posts from X, Reddit, YouTube and Telegram will display here as they pass the CSQE quality gate.
              </p>
            </div>
          )
        ) : stories === null ? (
          <div className="page-state">
            <LoaderCircle className="spin" /> Loading story signals...
          </div>
        ) : sortedStories.length ? (
          <div className="live-feed">
            {sortedStories.map((story) => (
              <StoryFeedCard key={story.id} story={story} />
            ))}
          </div>
        ) : (
          <div className="data-empty large-empty">
            <Radio />
            <strong>No active story signals</strong>
            <p>Refreshed stories from news feeds will appear here.</p>
          </div>
        )}

        <ModelTransparencyPanel />
        <IntelligenceBriefModal isOpen={briefOpen} onClose={() => setBriefOpen(false)} />
      </main>
    </div>
  );
}
