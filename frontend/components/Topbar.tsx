"use client";
import {Bell,Bookmark,Search} from "lucide-react";
import Link from "next/link";
import {useRouter} from "next/navigation";
import {FormEvent,useState} from "react";
export function Topbar({compact=false}:{compact?:boolean}){const [query,setQuery]=useState("");const router=useRouter();function submit(e:FormEvent){e.preventDefault();if(query.trim())router.push(`/search?q=${encodeURIComponent(query.trim())}`)}return <header className="topbar"><form onSubmit={submit}><button type="submit" className="search-submit" aria-label="Search"><Search size={19}/></button><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search any topic, protest, event or issue..." aria-label="Search topics"/></form><div className="top-actions"><Link className="live-pill" href="/live"><i/> Live Updates</Link>{compact&&<Link href="/saved" aria-label="Saved stories"><Bookmark size={20}/></Link>}<Link href="/settings" aria-label="Notification settings"><Bell size={20}/></Link></div></header>}
