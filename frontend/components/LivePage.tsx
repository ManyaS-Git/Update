/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {BarChart3,Bookmark,Heart,LoaderCircle,MessageCircle,Radio,Repeat2} from "lucide-react";
import {useEffect,useMemo,useState} from "react";
import type {Story} from "@/types";
import {getStories,setBookmark} from "@/lib/api";
import {stories as fallback} from "@/lib/demo-data";
import {Sidebar} from "./Sidebar";
import {Topbar} from "./Topbar";

/** Converts relative labels like "2h ago" / "15m ago" into minutes for sorting. */
function toMinutes(time?:string):number{
  if(!time)return Number.MAX_SAFE_INTEGER;
  const match=time.match(/(\d+)\s*([mhd])/i);
  if(!match)return Number.MAX_SAFE_INTEGER;
  const value=Number(match[1]);const unit=match[2].toLowerCase();
  return unit==="m"?value:unit==="h"?value*60:value*1440;
}

function dedupe(list:Story[]):Story[]{const seen=new Set<string>();return list.filter(item=>{const key=(item.title??"").toLowerCase().trim();const id=String(item.id);if(seen.has(id)||seen.has(key))return false;seen.add(id);seen.add(key);return true})}

function PostCard({story}:{story:Story}){
  const [liked,setLiked]=useState(false);
  const [saved,setSaved]=useState(Boolean(story.bookmarked));
  const href=story.topic_slug?`/topic/${story.topic_slug}`:`/story/${story.id}`;
  const remote=/^https?:\/\//.test(story.image);
  const source=story.category||"Signal";
  async function save(){const next=!saved;setSaved(next);try{await setBookmark(story.id,next)}catch{}}
  return <article className="post-card">
    <div className="post-avatar" aria-hidden>{source.charAt(0).toUpperCase()}</div>
    <div className="post-body">
      <div className="post-head"><strong>{source}</strong><span>@updates_signals</span><i/><time>{story.time}</time>{story.live&&<span className="post-live"><Radio size={11}/> LIVE</span>}</div>
      <Link className="post-text" href={href}>{story.title}</Link>
      {story.summary&&<p className="post-summary">{story.summary}</p>}
      <Link className="post-media" href={href} aria-label={`Open analysis for ${story.title}`}>
        {remote?<img src={story.image} alt={story.title} style={{objectPosition:story.imagePosition??"center"}}/>:<Image src={story.image} alt={story.title} fill sizes="(max-width:700px) 92vw, 560px" style={{objectPosition:story.imagePosition??"center"}}/>}
      </Link>
      <div className="post-actions">
        <Link href={href} className="post-action"><MessageCircle size={17}/><span>Discuss</span></Link>
        <button className="post-action" type="button"><Repeat2 size={17}/><span>Share signal</span></button>
        <button className={liked?"post-action liked":"post-action"} type="button" onClick={()=>setLiked(v=>!v)} aria-pressed={liked}><Heart size={17} fill={liked?"currentColor":"none"}/><span>{liked?"Liked":"Like"}</span></button>
        <Link href={href} className="post-action"><BarChart3 size={17}/><span>Analysis</span></Link>
        <button className={saved?"post-action saved":"post-action"} type="button" onClick={save} aria-pressed={saved}><Bookmark size={17} fill={saved?"currentColor":"none"}/></button>
      </div>
    </div>
  </article>;
}

export function LivePage(){
  const [items,setItems]=useState<Story[]|null>(null);
  const [sort,setSort]=useState<"top"|"latest">("top");
  useEffect(()=>{getStories().then(list=>setItems(dedupe(list))).catch(()=>setItems(dedupe(fallback)))},[]);
  const feed=useMemo(()=>{
    if(!items)return [];
    const list=[...items];
    if(sort==="latest")return list.sort((a,b)=>toMinutes(a.time)-toMinutes(b.time));
    return list.sort((a,b)=>Number(Boolean(b.live))-Number(Boolean(a.live))||toMinutes(a.time)-toMinutes(b.time));
  },[items,sort]);
  return <div className="app-shell"><Sidebar active="Live"/><main className="main"><Topbar/>
    <header className="live-header"><div><span className="live-eyebrow"><span className="live-pulse"/> LIVE FEED</span><h1>Top posts right now</h1><p>The most active public posts across connected sources, refreshed as new signals arrive.</p></div>
      <div className="live-sort"><button className={sort==="top"?"active":""} onClick={()=>setSort("top")}>Top</button><button className={sort==="latest"?"active":""} onClick={()=>setSort("latest")}>Latest</button></div>
    </header>
    {items===null?<div className="page-state"><LoaderCircle className="spin"/> Loading live feed…</div>
    :feed.length?<div className="live-feed">{feed.map(story=><PostCard key={story.id} story={story}/>)}</div>
    :<div className="data-empty large-empty"><Radio/><strong>No live posts yet</strong><p>This feed is wired to the posts endpoint and will populate as sources are collected.</p><code>GET /api/stories</code></div>}
  </main></div>;
}
