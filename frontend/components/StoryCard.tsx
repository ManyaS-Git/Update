/* eslint-disable @next/next/no-img-element */
"use client";
import Image from "next/image";
import Link from "next/link";
import {Bookmark,Radio} from "lucide-react";
import {useState} from "react";
import type {Story} from "@/types";
import {setBookmark} from "@/lib/api";

export function StoryCard({story,onBookmark}:{story:Story;onBookmark?:(enabled:boolean)=>void}){
  const [saved,setSaved]=useState(Boolean(story.bookmarked));
  async function toggle(){const next=!saved;setSaved(next);onBookmark?.(next);const values=JSON.parse(localStorage.getItem("updates-bookmarks")??"[]") as string[];localStorage.setItem("updates-bookmarks",JSON.stringify(next?[...new Set([...values,story.id])]:values.filter(id=>id!==story.id)));try{await setBookmark(story.id,next)}catch{}}
  const href=story.topic_slug?`/topic/${story.topic_slug}`:`/story/${story.id}`;const remote=/^https?:\/\//.test(story.image);
  return <article className="story-card"><Link className="story-link" href={href}><div className="story-image">{remote?<img src={story.image} alt={story.title} style={{objectPosition:story.imagePosition??"center",width:"100%",height:"100%"}}/>:<Image src={story.image} alt={story.title} fill sizes="(max-width:700px) 80vw, 16vw" style={{objectPosition:story.imagePosition??"center"}}/>}{story.live&&<span><Radio size={12}/> LIVE</span>}</div><div className="story-copy"><h3>{story.title}</h3><div><small>{story.time} &nbsp;•&nbsp; {story.category}</small></div></div></Link><button className={saved?"bookmark-button saved":"bookmark-button"} onClick={toggle} aria-label={saved?"Remove bookmark":"Save story"}><Bookmark size={16} fill={saved?"currentColor":"none"}/></button></article>
}
