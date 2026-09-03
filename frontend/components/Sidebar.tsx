"use client";
import Link from "next/link";
import {Bookmark, DatabaseZap, Grid2X2, HelpCircle, House, Radio, Settings, Star, UserRound} from "lucide-react";
import {Logo} from "./Logo";
import {Chatbot} from "./Chatbot";
const items=[{label:"Home",icon:House,href:"/"},{label:"Live",icon:Radio,href:"/live"},{label:"Top Stories",icon:Star,href:"/#stories"},{label:"Saved",icon:Bookmark,href:"/saved"},{label:"Categories",icon:Grid2X2,href:"/#categories"},{label:"My Feed",icon:UserRound,href:"/feed"},{label:"Sources",icon:DatabaseZap,href:"/sources"},{label:"Help & Guide",icon:HelpCircle,href:"/help"},{label:"Settings",icon:Settings,href:"/settings"}];
export function Sidebar({active="Home"}:{active?:string}){return <aside className="sidebar"><Link href="/" aria-label="UPDATES home"><Logo/></Link><nav>{items.map(({label,icon:Icon,href})=><Link className={active===label?"active":""} href={href} key={label}><Icon size={19}/><span>{label}</span></Link>)}</nav><Chatbot/></aside>}
