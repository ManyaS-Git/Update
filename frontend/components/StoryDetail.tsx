"use client";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Bookmark, LoaderCircle, Share2 } from "lucide-react";
import { useEffect, useState } from "react";
import { getStory, setBookmark } from "@/lib/api";
import type { Story } from "@/types";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function StoryDetail({ id }: { id: string }) {
  const [story, setStory] = useState<Story | null>(null);
  const [missing, setMissing] = useState(false);
  const [shared, setShared] = useState(false);

  useEffect(() => {
    getStory(id)
      .then(setStory)
      .catch(() => setMissing(true));
  }, [id]);

  async function bookmark() {
    if (!story) return;
    const next = !story.bookmarked;
    setStory({ ...story, bookmarked: next });
    try {
      await setBookmark(story.id, next);
    } catch {}
  }

  async function share() {
    if (navigator.share) {
      await navigator.share({ title: story?.title, url: location.href });
    } else {
      await navigator.clipboard.writeText(location.href);
    }
    setShared(true);
    setTimeout(() => setShared(false), 1600);
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main">
        <Topbar />
        {!story && !missing ? (
          <div className="page-state">
            <LoaderCircle className="spin" /> Loading story…
          </div>
        ) : missing ? (
          <div className="data-empty large-empty">
            <strong>Story not found</strong>
            <Link href="/">Return home</Link>
          </div>
        ) : (
          story && (
            <article className="article-page">
              <Link className="back-link" href="/">
                <ArrowLeft size={15} /> Back to stories
              </Link>
              <div className="article-hero">
                <Image src={story.image || "/images/news/general.jpg"} alt={story.title} fill priority sizes="80vw" />
              </div>
              <div className="article-body">
                <span className="article-category">{story.category}</span>
                <h1>{story.title}</h1>
                <p className="article-meta">{story.time} · Verified source stream</p>
                <p className="article-lead">
                  {story.summary ?? "This story is connected to the real-time social conversation intelligence dashboard."}
                </p>
                <div className="article-actions">
                  <button onClick={bookmark}>
                    <Bookmark size={16} fill={story.bookmarked ? "currentColor" : "none"} />
                    {story.bookmarked ? "Saved" : "Save"}
                  </button>
                  <button onClick={share}>
                    <Share2 size={16} />
                    {shared ? "Link copied" : "Share"}
                  </button>
                  {story.topic_slug && (
                    <Link href={`/topic/${story.topic_slug}`}>View conversation analysis</Link>
                  )}
                </div>
              </div>
            </article>
          )
        )}
      </main>
    </div>
  );
}
