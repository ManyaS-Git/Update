"use client";
import Link from "next/link";
import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import type { Story } from "@/types";
import { searchContent } from "@/lib/api";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { StoryCard } from "./StoryCard";

export function SearchPage({ query }: { query: string }) {
  const [items, setItems] = useState<Story[]>([]);
  const [topics, setTopics] = useState<{ slug: string; title: string; subtitle: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!query) {
      setLoading(false);
      return;
    }
    searchContent(query)
      .then((result) => {
        setItems(result.stories || []);
        setTopics(result.topics || []);
      })
      .catch(() => {
        setItems([]);
        setTopics([]);
      })
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <Topbar />
        <header className="utility-header">
          <Search />
          <div>
            <span>SEARCH RESULTS</span>
            <h1>{query ? `Results for “${query}”` : "Search UPDATES"}</h1>
            <p>Real-time search across indexed stories, social topics, and public discussions.</p>
          </div>
        </header>
        {topics.map((topic) => (
          <Link className="topic-result" href={`/topic/${topic.slug}`} key={topic.slug}>
            <strong>{topic.title}</strong>
            <span>{topic.subtitle}</span>
          </Link>
        ))}
        {loading ? (
          <div className="page-state">Searching intelligence index…</div>
        ) : items.length ? (
          <div className="story-grid utility-grid">
            {items.map((item) => (
              <StoryCard key={item.id} story={item} />
            ))}
          </div>
        ) : (
          <div className="data-empty large-empty">
            <Search />
            <strong>No matching stories found</strong>
            <p>Try searching for a different keyword, category, or public issue.</p>
          </div>
        )}
      </main>
    </div>
  );
}
