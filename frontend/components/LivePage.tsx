/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {
  BarChart3,
  Bookmark,
  CheckCircle,
  Flame,
  Heart,
  LoaderCircle,
  MessageCircle,
  Radio,
  Repeat2,
  Share2,
  TrendingUp,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { SocialPost, Story } from "@/types";
import { getPosts, getStories, setBookmark } from "@/lib/api";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

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
          {post.sentiment && (
            <span
              style={{
                marginLeft: "auto",
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
        <Link className="post-text" href={href}>
          {story.title}
        </Link>
        {story.summary && <p className="post-summary">{story.summary}</p>}
        {story.image && (
          <Link className="post-media" href={href} aria-label={`Open analysis for ${story.title}`}>
            {remote ? (
              <img
                src={story.image}
                alt={story.title}
                style={{ objectPosition: story.imagePosition ?? "center" }}
              />
            ) : (
              <Image
                src={story.image}
                alt={story.title}
                fill
                sizes="(max-width:700px) 92vw, 560px"
                style={{ objectPosition: story.imagePosition ?? "center" }}
              />
            )}
          </Link>
        )}
        <div className="post-actions">
          <Link href={href} className="post-action">
            <MessageCircle size={17} />
            <span>Discuss</span>
          </Link>
          <button className="post-action" type="button">
            <Repeat2 size={17} />
            <span>Share</span>
          </button>
          <Link href={href} className="post-action">
            <BarChart3 size={17} />
            <span>Analysis</span>
          </Link>
          <button
            className={saved ? "post-action saved" : "post-action"}
            type="button"
            onClick={save}
            aria-pressed={saved}
          >
            <Bookmark size={17} fill={saved ? "currentColor" : "none"} />
          </button>
        </div>
      </div>
    </article>
  );
}

export function LivePage() {
  const [tab, setTab] = useState<"social" | "stories">("social");
  const [posts, setPosts] = useState<SocialPost[] | null>(null);
  const [stories, setStories] = useState<Story[] | null>(null);
  const [sort, setSort] = useState<"top" | "latest">("top");

  useEffect(() => {
    getPosts(40)
      .then(setPosts)
      .catch(() => setPosts([]));
    getStories()
      .then(setStories)
      .catch(() => setStories([]));
  }, []);

  const sortedPosts = useMemo(() => {
    if (!posts) return [];
    const list = [...posts];
    if (sort === "latest") {
      return list.sort((a, b) => (b.timestamp > a.timestamp ? 1 : -1));
    }
    return list.sort((a, b) => b.likes + b.shares - (a.likes + a.shares));
  }, [posts, sort]);

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
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
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

        {tab === "social" ? (
          posts === null ? (
            <div className="page-state">
              <LoaderCircle className="spin" /> Streaming live social media posts...
            </div>
          ) : sortedPosts.length ? (
            <div className="live-feed">
              {sortedPosts.map((post) => (
                <SocialPostCard key={post.id} post={post} />
              ))}
            </div>
          ) : (
            <div className="data-empty large-empty">
              <Radio />
              <strong>No social posts streamed yet</strong>
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
      </main>
    </div>
  );
}
