"use client";
import {Bell,ChevronRight,Cookie,Database,Download,Eye,Fingerprint,Globe2,KeyRound,type LucideIcon,MapPin,Megaphone,Monitor,ShieldCheck,Sparkles,Trash2,UserRound} from "lucide-react";
import {useEffect,useState} from "react";
import {getPreferences,setNotifications} from "@/lib/api";
import {Sidebar} from "./Sidebar";
import {Topbar} from "./Topbar";

type Category="profile"|"security"|"privacy"|"ads";
const categories:{id:Category;label:string;hint:string;icon:LucideIcon}[]=[
  {id:"profile",label:"Profile",hint:"Name, workspace, notifications",icon:UserRound},
  {id:"security",label:"Password & Security",hint:"Login, 2FA, sessions",icon:KeyRound},
  {id:"privacy",label:"Data & Privacy",hint:"Collection, sharing, deletion",icon:ShieldCheck},
  {id:"ads",label:"Ad Preferences",hint:"Personalization & activity",icon:Megaphone},
];

type ToggleRow={kind:"toggle";id:string;icon:LucideIcon;title:string;desc:string;default:boolean};
type ValueRow={kind:"value";icon:LucideIcon;title:string;desc:string;value:string};
type Row=ToggleRow|ValueRow;
type Group={heading:string;rows:Row[]};

const content:Record<Category,{title:string;intro:string;groups:Group[]}>={
  profile:{title:"Profile",intro:"How your account appears and how UPDATES keeps you informed. These details are visible only inside your workspace.",groups:[
    {heading:"Account",rows:[
      {kind:"value",icon:UserRound,title:"Display name",desc:"Shown on shared reports and comments.",value:"Analyst"},
      {kind:"value",icon:Globe2,title:"Workspace",desc:"The organization this account belongs to.",value:"UPDATES Intelligence"},
      {kind:"value",icon:MapPin,title:"Default region",desc:"Used to prioritize regional signals.",value:"Global"},
    ]},
    {heading:"Notifications",rows:[
      {kind:"toggle",id:"notify",icon:Bell,title:"Live update notifications",desc:"Interface alerts when followed topics change significantly.",default:false},
      {kind:"toggle",id:"digest",icon:Sparkles,title:"Weekly trend digest",desc:"A summary of emerging narratives across your topics.",default:true},
    ]},
  ]},
  security:{title:"Password & Security",intro:"Keep your account secure. Manage how you sign in and review where your account is active.",groups:[
    {heading:"Login",rows:[
      {kind:"value",icon:KeyRound,title:"Password",desc:"Last changed 3 months ago.",value:"Change"},
      {kind:"toggle",id:"twofa",icon:Fingerprint,title:"Two-factor authentication",desc:"Require a second step when signing in from a new device.",default:true},
      {kind:"toggle",id:"alerts",icon:ShieldCheck,title:"Unrecognized login alerts",desc:"Get notified about logins from new devices or locations.",default:true},
    ]},
    {heading:"Sessions",rows:[
      {kind:"value",icon:Monitor,title:"Where you're logged in",desc:"Review and sign out active devices.",value:"2 active"},
      {kind:"toggle",id:"autologout",icon:KeyRound,title:"Auto sign-out when idle",desc:"End the session after a long period of inactivity.",default:false},
    ]},
  ]},
  privacy:{title:"Data & Privacy",intro:"Control what UPDATES collects for you and how insights are shared. The platform only ever analyzes public content in the aggregate.",groups:[
    {heading:"Collection",rows:[
      {kind:"toggle",id:"aggregate",icon:Database,title:"Aggregate analytics only",desc:"Restrict processing to group-level, non-identifying signals.",default:true},
      {kind:"toggle",id:"sensitive",icon:ShieldCheck,title:"Exclude sensitive categories",desc:"Down-weight signals inferring health, religion or political identity.",default:true},
    ]},
    {heading:"Sharing",rows:[
      {kind:"toggle",id:"share",icon:Eye,title:"Share anonymized insights",desc:"Allow aggregated trends to improve shared benchmarks.",default:false},
      {kind:"value",icon:Download,title:"Download your data",desc:"Export the preferences and settings tied to this account.",value:"Export"},
      {kind:"value",icon:Trash2,title:"Delete account data",desc:"Permanently remove this account's stored preferences.",value:"Delete"},
    ]},
  ]},
  ads:{title:"Ad Preferences",intro:"Manage personalization. UPDATES does not sell your data — these controls govern only in-product recommendations.",groups:[
    {heading:"Personalization",rows:[
      {kind:"toggle",id:"personalized",icon:Megaphone,title:"Personalized recommendations",desc:"Tailor suggested topics to your recent activity.",default:true},
      {kind:"toggle",id:"activity",icon:Eye,title:"Use activity for suggestions",desc:"Let your reading history influence what surfaces first.",default:false},
      {kind:"toggle",id:"cookies",icon:Cookie,title:"Non-essential cookies",desc:"Allow analytics cookies that help improve the interface.",default:false},
    ]},
  ]},
};

export function SettingsPage(){
  const [category,setCategory]=useState<Category>("profile");
  const [toggles,setToggles]=useState<Record<string,boolean>>(()=>{const seed:Record<string,boolean>={};Object.values(content).forEach(section=>section.groups.forEach(group=>group.rows.forEach(row=>{if(row.kind==="toggle")seed[row.id]=row.default})));return seed});
  const [saved,setSaved]=useState("");
  useEffect(()=>{getPreferences().then(x=>setToggles(prev=>({...prev,notify:x.notifications_enabled}))).catch(()=>setToggles(prev=>({...prev,notify:localStorage.getItem("updates-notifications")==="true"})))},[]);
  async function flip(id:string){const next=!toggles[id];setToggles(prev=>({...prev,[id]:next}));if(id==="notify"){localStorage.setItem("updates-notifications",String(next));try{await setNotifications(next);flash("Saved to backend")}catch{flash("Saved on this device")}}else flash("Preference updated")}
  function flash(message:string){setSaved(message);setTimeout(()=>setSaved(""),1600)}
  const active=content[category];
  return <div className="app-shell"><Sidebar active="Settings"/><main className="main"><Topbar/>
    <header className="utility-header"><ShieldCheck/><div><span>ACCOUNTS CENTER</span><h1>Settings</h1><p>Manage your profile, security, data privacy and ad preferences in one place.</p></div></header>
    <div className="accounts-center">
      <aside className="ac-rail" aria-label="Settings categories"><div className="ac-rail-title">SETTINGS</div>{categories.map(({id,label,hint,icon:Icon})=><button key={id} className={category===id?"active":""} onClick={()=>setCategory(id)} aria-pressed={category===id}><Icon/><span><b>{label}</b><small>{hint}</small></span></button>)}</aside>
      <section className="ac-content"><header><h2>{active.title}</h2><p>{active.intro}</p></header>
        {active.groups.map(group=><div className="ac-group" key={group.heading}><h3>{group.heading}</h3>{group.rows.map(row=>{const Icon=row.icon;return <div className="ac-row" key={row.title}><Icon size={19}/><div className="ac-row-main"><strong>{row.title}</strong><small>{row.desc}</small></div>{row.kind==="toggle"?<button className={toggles[row.id]?"ac-toggle on":"ac-toggle"} onClick={()=>flip(row.id)} aria-pressed={toggles[row.id]} aria-label={row.title}><i/></button>:<><span className="ac-value">{row.value}</span><button className="ac-chevron" aria-label={row.title}><ChevronRight size={17}/></button></>}</div>})}</div>)}
        <div className="ac-note"><ShieldCheck size={16}/><span>These controls are a hardcoded demonstration of the privacy and security surface. Toggle states are stored locally; connect the backend to persist them per account. Live update notifications are already wired to the preferences API.</span></div>
      </section>
    </div>
    {saved&&<div className="toast">{saved}</div>}
  </main></div>;
}
