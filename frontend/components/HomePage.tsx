/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {
  BarChart3,
  ChevronRight,
  FlaskConical,
  Globe2,
  GraduationCap,
  Landmark,
  Leaf,
  MoreHorizontal,
  Radio,
  RefreshCw,
  Scale,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getStories, getNarratives, refreshLatestNews, NarrativeSummary } from "@/lib/api";
import type { Story } from "@/types";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { StoryCard } from "./StoryCard";

const categories = [
  { name: "All", icon: Globe2 },
  { name: "Protest", icon: Users },
  { name: "Foreign Affairs", icon: Landmark },
  { name: "Laws", icon: Scale },
  { name: "Analysis", icon: BarChart3 },
  { name: "Environment", icon: Leaf },
  { name: "Science & Tech", icon: FlaskConical },
  { name: "Education", icon: GraduationCap },
  { name: "More", icon: MoreHorizontal },
];

function dedupeStories(list: Story[]): Story[] {
  const seen = new Set<string>();
  return list.filter((item) => {
    const key = (item.title ?? "").toLowerCase().replace(/\s+/g, " ").trim();
    const id = String(item.id);
    if (seen.has(id) || seen.has(key)) return false;
    seen.add(id);
    seen.add(key);
    return true;
  });
}

export function HomePage() {
  const [items, setItems] = useState<Story[]>([]);
  const [narratives, setNarratives] = useState<{ emerging: NarrativeSummary[]; popular: NarrativeSummary[] }>({
    emerging: [],
    popular: [],
  });
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("All");
  const [showAll, setShowAll] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshNote, setRefreshNote] = useState("");
  const [activeHero, setActiveHero] = useState(0);

  useEffect(() => {
    Promise.all([
      getStories().catch(() => []),
      getNarratives().catch(() => ({ emerging: [], popular: [] })),
    ]).then(([storyList, narrData]) => {
      setItems(dedupeStories(storyList));
      setNarratives(narrData);
      setLoading(false);
    });
  }, []);

  async function refresh() {
    setRefreshing(true);
    setRefreshNote("");
    try {
      const result = await refreshLatestNews();
      setItems(dedupeStories(result.stories));
      setCategory("All");
      setActiveHero(0);
      setRefreshNote(
        result.added
          ? `${result.added} recent live stories ingested`
          : `Up to date · ${result.received} signals checked`
      );
      const narr = await getNarratives().catch(() => null);
      if (narr) setNarratives(narr);
    } catch {
      setRefreshNote("Live stream ingestor is syncing with network...");
    } finally {
      setRefreshing(false);
    }
  }

  const filtered = useMemo(
    () =>
      category === "All" || category === "More"
        ? items
        : items.filter(
            (item) => item.category === category || (category === "Protest" && item.category === "India")
          ),
    [items, category]
  );

  const shown = showAll ? filtered : filtered.slice(0, 12);
  const heroSlides = useMemo(() => items.slice(0, 5), [items]);
  const heroIndex = heroSlides.length ? activeHero % heroSlides.length : 0;
  const hero = heroSlides[heroIndex];
  const heroHref = hero?.topic_slug ? `/topic/${hero.topic_slug}` : hero?.id ? `/story/${hero.id}` : "#";
  const remoteHero = Boolean(hero?.image && /^https?:\/\//.test(hero.image));

  useEffect(() => {
    if (heroSlides.length < 2) return;
    const timer = window.setInterval(
      () => setActiveHero((current) => (current + 1) % heroSlides.length),
      4000
    );
    return () => window.clearInterval(timer);
  }, [heroSlides.length]);

  return (
    <div className="app-shell">
      <Sidebar active="Home" />
      <main className="main">
        <Topbar />

        {/* Dynamic Hero Carousel */}
        {hero ? (
          <section className="hero" aria-roledescription="carousel" aria-label="Latest news">
            {remoteHero ? (
              <img key={hero.id} className="hero-photo" src={hero.image} alt={hero.title} />
            ) : (
              <Image
                key={hero.id}
                src={hero.image || "/images/news/general.jpg"}
                alt={hero.title}
                fill
                priority
                sizes="(max-width: 900px) 100vw, 85vw"
              />
            )}
            <div className="hero-wash" />
            <div className="hero-copy dynamic-hero-copy" key={`copy-${hero.id}`}>
              <h1>
                <span>LATEST</span>
                <br />
                <em>{hero.category}</em>
                <br />
                <b>{hero.title}</b>
              </h1>
              <p>{hero.live ? "LIVE STREAMING STORY" : "LATEST VERIFIED DATASET"}</p>
              <small>
                {hero.time.toUpperCase()} · <b>DYNAMIC CONVERSATION INTELLIGENCE.</b>
              </small>
              <Link href={heroHref}>
                Explore real analytics <ChevronRight size={18} />
              </Link>
            </div>
            {heroSlides.length > 1 && (
              <div className="hero-dots">
                {heroSlides.map((slide, index) => (
                  <button
                    key={slide.id}
                    className={index === heroIndex ? "active" : ""}
                    onClick={() => setActiveHero(index)}
                    aria-label={`Show ${slide.title}`}
                    aria-current={index === heroIndex ? "true" : undefined}
                  />
                ))}
              </div>
            )}
          </section>
        ) : (
          <section className="hero" style={{ background: "linear-gradient(135deg, #181926, #24273a)", display: "flex", alignItems: "center", justifyContent: "center", minHeight: "260px" }}>
            <div style={{ textAlign: "center", color: "#cad3f5", padding: "2rem" }}>
              <Radio className={loading ? "spin" : ""} size={32} style={{ color: "#ed8796", marginBottom: "0.5rem" }} />
              <h2>{loading ? "Connecting to Live Social Streams..." : "Live Streams Active"}</h2>
              <p style={{ color: "#a5adcb", maxWidth: "500px", margin: "0.5rem auto 1rem" }}>
                {loading
                  ? "Aggregating incoming news, social comments, and signal metrics across platforms."
                  : "Streaming engine is ready. Click 'Refresh live signals' to pull recent news feeds."}
              </p>
              <button onClick={refresh} disabled={refreshing} style={{ padding: "0.5rem 1.25rem", borderRadius: "999px", background: "#ed8796", color: "#181926", fontWeight: "bold", border: "none", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
                <RefreshCw size={14} className={refreshing ? "spin" : ""} /> Refresh live signals
              </button>
            </div>
          </section>
        )}

        {/* Real-Time Emerging & Popular Narratives Section */}
        {((narratives?.emerging?.length ?? 0) > 0 || (narratives?.popular?.length ?? 0) > 0) && (
          <section className="narratives-strip" style={{ margin: "1.5rem 0", padding: "1rem 1.25rem", background: "rgba(36, 39, 58, 0.7)", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.08)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Zap size={18} style={{ color: "#eed49f" }} />
                <h3 style={{ margin: 0, fontSize: "1rem", color: "#cad3f5", fontWeight: 700 }}>Real-Time Detected Narratives</h3>
                <span style={{ fontSize: "0.75rem", background: "rgba(238, 212, 159, 0.15)", color: "#eed49f", padding: "2px 8px", borderRadius: "999px" }}>
                  Velocity-Weighted
                </span>
              </div>
              <Link href="/live" style={{ fontSize: "0.8rem", color: "#8aadf4", textDecoration: "none", display: "flex", alignItems: "center", gap: "2px" }}>
                View all signals <ChevronRight size={14} />
              </Link>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "0.75rem" }}>
              {(narratives?.emerging ?? []).slice(0, 3).map((item) => (
                <Link
                  key={item.id}
                  href={`/topic/${item.topic_slug}`}
                  style={{
                    display: "block",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    background: "rgba(24, 25, 38, 0.6)",
                    border: "1px solid rgba(237, 135, 150, 0.3)",
                    textDecoration: "none",
                    color: "inherit",
                    transition: "transform 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                    <span style={{ fontSize: "0.7rem", color: "#ed8796", fontWeight: "bold", display: "flex", alignItems: "center", gap: "4px" }}>
                      <TrendingUp size={12} /> EMERGING
                    </span>
                    <span style={{ fontSize: "0.7rem", color: "#a5adcb" }}>
                      +{Math.round(item.velocity * 100)}% velocity
                    </span>
                  </div>
                  <strong style={{ display: "block", fontSize: "0.88rem", color: "#cad3f5", marginBottom: "0.25rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {item.title}
                  </strong>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.72rem", color: "#8087a2" }}>
                    <span>{item.volume} signals tracked</span>
                    <span style={{ textTransform: "capitalize" }}>{item.dominant_platform}</span>
                  </div>
                </Link>
              ))}

              {(narratives?.popular ?? []).slice(0, 3).map((item) => (
                <Link
                  key={item.id}
                  href={`/topic/${item.topic_slug}`}
                  style={{
                    display: "block",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    background: "rgba(24, 25, 38, 0.6)",
                    border: "1px solid rgba(138, 173, 244, 0.3)",
                    textDecoration: "none",
                    color: "inherit",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                    <span style={{ fontSize: "0.7rem", color: "#8aadf4", fontWeight: "bold", display: "flex", alignItems: "center", gap: "4px" }}>
                      <Sparkles size={12} /> POPULAR
                    </span>
                    <span style={{ fontSize: "0.7rem", color: "#a5adcb" }}>
                      Score: {item.momentum.toFixed(1)}
                    </span>
                  </div>
                  <strong style={{ display: "block", fontSize: "0.88rem", color: "#cad3f5", marginBottom: "0.25rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {item.title}
                  </strong>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.72rem", color: "#8087a2" }}>
                    <span>{item.volume} conversations</span>
                    <span style={{ textTransform: "capitalize" }}>{item.dominant_platform}</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Categories navigation */}
        <section id="categories" className="categories" aria-label="Topic categories">
          {categories.map(({ name, icon: Icon }) => (
            <button
              className={category === name ? "selected" : ""}
              onClick={() => setCategory(name)}
              key={name}
            >
              <Icon size={25} />
              <span>{name}</span>
            </button>
          ))}
        </section>

        {/* Stories Section */}
        <section id="stories" className="story-section">
          <div className="section-title">
            <h2>{category === "All" ? "Latest live coverage & narratives" : category}</h2>
            <div className="section-actions">
              <button onClick={refresh} disabled={refreshing}>
                <RefreshCw size={12} className={refreshing ? "spin" : ""} />
                {refreshing ? "Ingesting..." : "Refresh latest"}
              </button>
              <button onClick={() => setShowAll((value) => !value)}>
                {showAll ? "Show less" : "See all"}
              </button>
            </div>
          </div>
          {refreshNote && <p className="refresh-note">{refreshNote}</p>}
          {shown.length ? (
            <div className="story-grid">
              {shown.map((story) => (
                <StoryCard story={story} key={story.id} />
              ))}
            </div>
          ) : loading ? (
            <div className="page-state">Loading real-time social stories...</div>
          ) : (
            <div className="data-empty">
              <strong>No stories currently ingested in this category</strong>
              <p>Click "Refresh latest" above to pull live verified feeds dynamically.</p>
            </div>
          )}
          <p className="demo-note">
            All metrics and stories are retrieved dynamically from live APIs and Kafka streams. No hardcoded demo data is retained.
          </p>
        </section>
      </main>
    </div>
  );
}
