/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {ArrowDownToLine,BarChart3,BriefcaseBusiness,ChevronRight,Clock3,Database,GraduationCap,Hash,Info,Languages,MapPin,MessageCircle,Radio,Scale,Share2,ShieldCheck,TrendingUp,UsersRound} from "lucide-react";
import {useEffect, useState} from "react";
import type {Topic} from "@/types";
import {fetchTopicClient} from "@/lib/api";
import {Sidebar} from "./Sidebar";import {Topbar} from "./Topbar";import {SentimentDonut,TrendChart} from "./TopicCharts";import {AIAnalyst} from "./AIAnalyst";import {NetworkPanel} from "./NetworkPanel";import {DataSlot} from "./DataSlot";

const audienceIcons=[MapPin,Languages,UsersRound,Hash,BarChart3,MessageCircle];
const driverIcons=[Scale,GraduationCap,BriefcaseBusiness,Database];

export function TopicPage({topic: initialTopic}:{topic:Topic}){
  const [topic, setTopic] = useState<Topic>(initialTopic);
  const [voices, setVoices] = useState<Topic["voices"]>(initialTopic.voices || []);
  const [userComment, setUserComment] = useState("");
  const [userRole, setUserRole] = useState("Community Voice");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    setTopic(initialTopic);
    setVoices(initialTopic.voices || []);
  }, [initialTopic]);

  useEffect(() => {
    let active = true;
    if (initialTopic.preview || initialTopic.totalConversations === 0) {
      fetchTopicClient(initialTopic.slug).then(fresh => {
        if (active && fresh && (fresh.totalConversations > 0 || !fresh.preview)) {
          setTopic(fresh);
          if (fresh.voices && fresh.voices.length > 0) {
            setVoices(fresh.voices);
          }
        }
      }).catch(() => {});
    }
    return () => { active = false; };
  }, [initialTopic.slug, initialTopic.preview, initialTopic.totalConversations]);

  async function handleVoiceSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleanText = userComment.trim();
    if (!cleanText || submitting) return;
    setSubmitting(true);
    try {
      const res = await fetch(`/api/topics/${topic.slug}/voices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: cleanText, source: userRole })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.voice) {
          setVoices(prev => [data.voice, ...prev]);
          setTopic(prev => {
            const isSupp = data.tone === "supporting";
            const isConc = data.tone === "concerned";
            const total = prev.totalConversations + 1;
            const newPos = isSupp ? Math.min(100, prev.sentiment.positive + 2) : Math.max(0, prev.sentiment.positive - 1);
            const newNeg = isConc ? Math.min(100, prev.sentiment.negative + 2) : Math.max(0, prev.sentiment.negative - 1);
            const newNeu = Math.max(0, 100 - newPos - newNeg);
            return {
              ...prev,
              totalConversations: total,
              updated: "Live signals · Just now",
              sentiment: { positive: newPos, negative: newNeg, neutral: newNeu }
            };
          });
          setUserComment("");
          const toneName = data.tone === "supporting" ? "Supporting" : data.tone === "concerned" ? "Concerned" : "Neutral";
          setFeedback(`✓ Opinion analyzed as "${toneName}" via MuRIL AI and added live to this topic!`);
          setTimeout(() => setFeedback(null), 6000);
        }
      }
    } catch (err) {
      console.error("Failed to submit public voice:", err);
    } finally {
      setSubmitting(false);
    }
  }

  const signalOnly=topic.analysisScope==="public_attention_signals";const metricLabel=topic.metricLabel??"public conversations analysed";
  const audience=[{title:"Geography",label:"Highest observed activity",value:topic.audience.geography,meta:`Confidence: ${topic.audience.geographyConfidence??"Unavailable"}`},{title:"Language",label:"Dominant language",value:topic.audience.language,meta:`Confidence: ${topic.audience.languageConfidence??"Unavailable"}`},{title:"Age groups",label:"Most active when disclosed",value:topic.audience.age,meta:`Confidence: ${topic.audience.ageConfidence}`},{title:"Interest groups",label:"Most active inferred",value:topic.audience.interests,meta:`Confidence: ${topic.audience.interestsConfidence??"Unavailable"}`},{title:"Key topics",label:"Primary narratives",value:topic.audience.topics.join(", "),meta:`Confidence: ${topic.audience.topicsConfidence??"Unavailable"}`},{title:"Platforms",label:"Largest observed source",value:topic.audience.platform,meta:`Confidence: ${topic.audience.platformConfidence??"Unavailable"}`}];
  function download(){const text=`UPDATES Intelligence Brief\n${topic.title}\n\n${topic.insight||"No comments have been analysed for this story yet."}\n\n${topic.totalConversations.toLocaleString()} ${metricLabel}\n${topic.sentiment.negative}% opposing · ${topic.sentiment.neutral}% neutral · ${topic.sentiment.positive}% supportive\n\nEvidence and confidence labels apply.`;const url=URL.createObjectURL(new Blob([text],{type:"text/plain"}));const anchor=document.createElement("a");anchor.href=url;anchor.download=`updates-${topic.slug}-brief.txt`;anchor.click();URL.revokeObjectURL(url)}
  const remoteImage=Boolean(topic.image&&/^https?:\/\//.test(topic.image));
  return <div className="app-shell topic-shell"><Sidebar active="Live"/><main className="main"><Topbar compact/>
    <div className="breadcrumbs"><Link href="/">Home</Link><ChevronRight size={13}/><span>{topic.category??"Analysis"}</span><ChevronRight size={13}/><b>{topic.title}</b></div>
    <header className="topic-header" data-slot="topic-summary" data-endpoint="GET /api/topics/{slug}"><div className="topic-title"><div className="topic-thumb">{remoteImage?<img src={topic.image} alt={topic.title}/>:<Image src={topic.image??"/images/real-data-check.jpg"} alt={topic.title} fill sizes="130px"/>}</div><div><h1>{topic.title}</h1><p>{topic.preview?"Story-specific preview analysis · live comments not collected yet":topic.subtitle}</p><div className="topic-meta">{topic.demo?<span className="preview-badge">Pitch demo analysis</span>:topic.preview?<span className="preview-badge">Preview analysis</span>:<span className="live-tag"><Radio size={12}/> Live analysis</span>}<b>{topic.totalConversations.toLocaleString()}</b> {metricLabel} <i/> Updated {topic.updated}</div></div></div><div className="topic-actions"><button onClick={()=>navigator.clipboard?.writeText(location.href)}><Share2 size={16}/> Share</button><button onClick={download}><ArrowDownToLine size={16}/> Download report</button></div></header>
    <div className="topic-grid top-grid">
      <section className="panel sentiment-panel" data-slot="sentiment-analysis" data-endpoint="GET /api/topics/{slug}/sentiment"><h2>{topic.preview||signalOnly?"Headline-tone preview":"Overall public sentiment"} <Info size={13}/></h2><SentimentDonut values={topic.sentiment}/>{!signalOnly&&topic.totalConversations>0&&<div className="sentiment-shift"><TrendingUp size={16}/><span><b>{topic.sentimentChange}% more opposing</b> conversation<br/>in the selected comparison window</span></div>}</section>
      <section className="panel insight-panel" data-slot="intelligence-brief" data-endpoint="GET /api/topics/{slug}/brief"><h2>AI Insight <Info size={13}/></h2><DataSlot name="ai-insight" endpoint="GET /api/topics/{slug}/brief" hasData={Boolean(topic.insight)}><blockquote>{topic.insight}</blockquote></DataSlot><Link href="/methodology">How this was calculated <ChevronRight size={13}/></Link></section>
      <section className="panel audience-panel" data-slot="audience-intelligence" data-endpoint="GET /api/topics/{slug}/audience"><h2>Understand the conversation <Info size={13}/></h2><DataSlot name="audience-cards" endpoint="GET /api/topics/{slug}/audience" hasData={audience.some(item=>Boolean(item.value))}><div className="audience-grid">{audience.map((item,index)=>{const Icon=audienceIcons[index];return <article key={item.title}><Icon size={21}/><div><strong>{item.title}</strong><small>{item.label}</small><b>{item.value}</b>{item.meta&&<em>{item.meta}</em>}</div></article>})}</div></DataSlot></section>
    </div>
    <section className="panel drivers" data-slot="conversation-drivers" data-endpoint="GET /api/topics/{slug}/drivers"><h2>What’s driving the conversation? <Info size={13}/></h2><DataSlot name="driver-cards" endpoint="GET /api/topics/{slug}/drivers" hasData={topic.drivers.length>0}><div className="drivers-grid">{topic.drivers.map((driver,index)=>{const Icon=driverIcons[index%driverIcons.length];return <article key={driver.title}><i><Icon size={21}/></i><div><strong>{driver.title}</strong><p>{driver.description}</p><span className={driver.status.toLowerCase().replace(" ","-")}>{driver.status}</span></div></article>})}</div></DataSlot></section>
    <section className="panel voices" data-slot="public-voices" data-endpoint="GET /api/topics/{slug}/voices">
      <div className="panel-header-row">
        <h2>Voices from the public <Info size={13}/></h2>
        <span className="live-pill-mini"><Radio size={10} className="live-pulse"/> Live Community Discourse</span>
      </div>
      <DataSlot name="voice-cards" endpoint="GET /api/topics/{slug}/voices" hasData={voices.length>0} emptyTitle="Public discourse initializing" emptyMessage="Verified community statements are being indexed.">
        <div className="voices-grid">
          {voices.map((voice, idx) => (
            <article key={`${voice.label}-${idx}`}>
              <q>{voice.quote}</q>
              <div className="voice-footer">
                <span className={voice.tone}>{voice.label}</span>
              </div>
            </article>
          ))}
        </div>
      </DataSlot>
      <small>Representative, anonymized statements from the current analysis dataset.</small>

      <div className="voice-contribute-box">
        <div className="voice-contribute-header">
          <MessageCircle size={15}/>
          <div>
            <strong>Add your voice to this public analysis</strong>
            <p>Contribute a real public perspective or ground observation on this topic. It is classified live via the MuRIL sentiment engine and indexed into this story’s intelligence.</p>
          </div>
        </div>
        <form onSubmit={handleVoiceSubmit} className="voice-form">
          <input
            type="text"
            placeholder="Share your opinion or ground observation on this topic..."
            value={userComment}
            onChange={e => setUserComment(e.target.value)}
            disabled={submitting}
            required
          />
          <select value={userRole} onChange={e => setUserRole(e.target.value)} disabled={submitting}>
            <option value="Community Voice">Community Voice</option>
            <option value="Student Aspirant">Student Aspirant</option>
            <option value="Local Citizen">Local Citizen</option>
            <option value="Civic Observer">Civic Observer</option>
          </select>
          <button type="submit" disabled={submitting || !userComment.trim()}>
            {submitting ? "Analyzing..." : "Post Voice"}
          </button>
        </form>
        {feedback && <div className="voice-toast">{feedback}</div>}
      </div>
    </section>
    <section className="panel confidence" data-slot="data-confidence" data-endpoint="GET /api/topics/{slug}/confidence"><h2>Data confidence <Info size={13}/></h2><DataSlot name="confidence-metrics" endpoint="GET /api/topics/{slug}/confidence" hasData={topic.confidence.sources.length>0}><div className="confidence-grid"><article><Database/><span>Sources analysed<b>{topic.confidence.sources.join(", ")}</b></span></article><article><UsersRound/><span>{signalOnly?"Total public signals":"Total conversations"}<b>{topic.totalConversations.toLocaleString()}</b></span></article><article><Clock3/><span>Last updated<b>{topic.updated}</b></span></article><article><ShieldCheck/><span>AI confidence<b className="green">{topic.confidence.level}</b></span></article></div><p className="confidence-summary">{topic.confidence.qualified.toLocaleString()} qualified signals · {topic.confidence.lowSignal.toLocaleString()} low-signal items excluded or down-weighted</p></DataSlot></section>
    <section className="panel trend-panel" data-slot="temporal-intelligence" data-endpoint="GET /api/topics/{slug}/trends"><div className="panel-heading"><div><h2>{topic.preview?"Illustrative signal trajectory":"Conversation volume over time"}</h2><p>{topic.preview?"Relative story-context preview · not measured conversation volume":"Qualified public conversation · dynamic analysis window"}</p></div><span className="rising"><TrendingUp size={14}/> {topic.preview?"Preview":"Dynamic status"}</span></div><TrendChart data={topic.trends}/></section>
    <AIAnalyst topicSlug={topic.slug}/><NetworkPanel network={topic.network}/>
    <footer className="topic-footer"><strong>{topic.demo?"Pitch demonstration dataset":topic.preview?"Story-context preview":"API-backed intelligence"}</strong><span>{topic.demo?"Complete deterministic sample analytics for presentation rehearsal. Values and representative voices are synthetic and clearly separated from live evidence.":topic.preview?"Preview values are generated independently from this story’s title and category. They are low-confidence and will be replaced—not combined—with collected comment analysis.":signalOnly?"Public-signal counts are matched Wikipedia pageviews, not unique people or social comments. Headline tone is shown separately.":"Every analytics module reflects comments attached to this topic only."}</span><Link href="/methodology">View methodology & data ethics</Link></footer>
  </main></div>
}
