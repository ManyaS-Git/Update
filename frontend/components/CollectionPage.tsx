"use client";
import {useEffect,useState} from "react";
import {Bookmark,LoaderCircle,Rss} from "lucide-react";
import type {Story} from "@/types";
import {getBookmarks,getFeed} from "@/lib/api";
import {stories as fallback} from "@/lib/demo-data";
import {Sidebar} from "./Sidebar";import {Topbar} from "./Topbar";import {StoryCard} from "./StoryCard";

export function CollectionPage({mode}:{mode:"saved"|"feed"}){const [items,setItems]=useState<Story[]|null>(null);useEffect(()=>{const request=mode==="saved"?getBookmarks():getFeed();request.then(setItems).catch(()=>{if(mode==="saved"){const ids=JSON.parse(localStorage.getItem("updates-bookmarks")??"[]") as string[];setItems(fallback.filter(item=>ids.includes(item.id)).map(item=>({...item,bookmarked:true})))}else setItems(fallback)})},[mode]);const title=mode==="saved"?"Saved stories":"My feed";const Icon=mode==="saved"?Bookmark:Rss;return <div className="app-shell"><Sidebar active={mode==="saved"?"Saved":"My Feed"}/><main className="main"><Topbar/><header className="utility-header"><Icon/><div><span>YOUR UPDATES</span><h1>{title}</h1><p>{mode==="saved"?"Stories you bookmarked appear here across sessions.":"A dynamic feed prepared from live, recent and relevant stories."}</p></div></header>{items===null?<div className="page-state"><LoaderCircle className="spin"/> Loading…</div>:items.length?<div className="story-grid utility-grid">{items.map(item=><StoryCard key={item.id} story={item} onBookmark={enabled=>{if(!enabled&&mode==="saved")setItems(current=>current?.filter(x=>x.id!==item.id)??[])}}/>)}</div>:<div className="data-empty large-empty"><Bookmark/><strong>No saved stories yet</strong><p>Use the bookmark button on any story and it will appear here.</p></div>}</main></div>}
