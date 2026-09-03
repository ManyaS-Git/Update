"use client";
import {Database,Eye,FileText,HelpCircle,Lock,type LucideIcon,Plus,ScrollText,ShieldCheck,UserCheck} from "lucide-react";
import {useState} from "react";
import {Sidebar} from "./Sidebar";
import {Topbar} from "./Topbar";

type Tab="privacy"|"terms"|"faq";
const tabs:{id:Tab;label:string;icon:LucideIcon}[]=[{id:"privacy",label:"Data Privacy",icon:ShieldCheck},{id:"terms",label:"Terms & Conditions",icon:ScrollText},{id:"faq",label:"FAQ",icon:HelpCircle}];

const privacyBlocks=[
  {icon:Database,title:"What we collect",body:"UPDATES analyzes publicly available social posts, comments and news signals. We process only public content and derived, aggregated indicators — never private messages, contacts or content behind a login.",list:["Public posts, comments and reactions from connected sources","Aggregated sentiment, topic and volume metrics","Inferred, non-identifying audience patterns (approximate region, likely age band, interest clusters)"]},
  {icon:Eye,title:"How we use it",body:"Data is used strictly to surface emerging trends and demographic patterns in the aggregate. Individual authors are not profiled, scored or targeted.",list:["Trend detection and conversation analysis","Anonymized, representative sampling of public voices","Confidence scoring so low-signal data is down-weighted"]},
  {icon:UserCheck,title:"Your rights & anonymization",body:"All demographic insights are probabilistic and shown at group level only. Quotes are anonymized and never fabricated. We do not sell personal data, and you can request removal of any content that identifies you.",list:["Right to access the categories of data we process","Right to request deletion of identifying content","Right to opt out of any future personalized features"]},
  {icon:Lock,title:"How we protect it",body:"Access to raw collected data is restricted and encrypted in transit. Retention is limited to what is needed for active trend windows, after which raw items are purged and only aggregates remain."},
];

const termsBlocks=[
  {title:"1. Acceptable use",body:"UPDATES provides social intelligence and analytics for research, editorial and situational-awareness purposes. You agree not to use the platform to harass, surveil or target individuals, or to make automated decisions about people based on inferred attributes."},
  {title:"2. Nature of the insights",body:"All sentiment, demographic and trend outputs are AI-generated estimates with confidence labels. They are indicative, not definitive, and should not be treated as verified fact about any individual or protected group."},
  {title:"3. Data sources",body:"Signals originate from public sources and third-party providers. Availability, accuracy and completeness of those sources are outside our control, and coverage may change without notice."},
  {title:"4. No fabricated content",body:"Representative quotes shown in the product are drawn from real, anonymized public content. The platform does not invent statements and attribute them to people."},
  {title:"5. Limitation of liability",body:"UPDATES is provided \"as is\". To the maximum extent permitted by law, we are not liable for decisions made solely on the basis of platform outputs."},
  {title:"6. Changes to these terms",body:"We may update these terms as the platform evolves. Material changes will be reflected here with a revised date, and continued use constitutes acceptance."},
];

const faqs=[
  {q:"Where does the data come from?",a:"From publicly available posts, comments and news across the sources connected in your workspace. Nothing behind a login or private setting is collected."},
  {q:"How are age, location and interests determined?",a:"They are inferred at the aggregate level using language, public profile signals and behavioral patterns. Every demographic figure carries a confidence label, and low-confidence signals are down-weighted."},
  {q:"Are the public quotes real?",a:"Yes. Quotes are pulled from real, topic-matched public content and anonymized before display. Preview panels intentionally stay empty rather than showing fabricated quotes."},
  {q:"Can an individual be identified or tracked?",a:"No. The platform is built for group-level analysis. It does not profile, score or track individual people, and demographic outputs are never tied to a named person."},
  {q:"How current is the analysis?",a:"Live topics refresh as new signals arrive. Each panel shows its last-updated time so you always know how fresh the underlying data is."},
  {q:"What does the confidence label mean?",a:"It reflects how much qualified data supports a given insight. Higher confidence means more corroborating signals; lower confidence means the result should be read with caution."},
  {q:"How do I remove content that identifies me?",a:"Use the request channel in Data Privacy. We will locate and purge identifying items and confirm once removed."},
];

function FaqRow({q,a}:{q:string;a:string}){
  const [open,setOpen]=useState(false);
  return <div className={open?"faq-item open":"faq-item"}><button onClick={()=>setOpen(v=>!v)} aria-expanded={open}>{q}<Plus size={17}/></button>{open&&<div className="faq-answer">{a}</div>}</div>;
}

export function HelpPage(){
  const [tab,setTab]=useState<Tab>("privacy");
  return <div className="app-shell"><Sidebar active="Help & Guide"/><main className="main"><Topbar/>
    <header className="utility-header"><HelpCircle/><div><span>HELP &amp; GUIDE</span><h1>Help &amp; Guide</h1><p>Understand how your data is handled, the terms of using UPDATES, and answers to common questions.</p></div></header>
    <nav className="help-tabs" aria-label="Help sections">{tabs.map(({id,label,icon:Icon})=><button key={id} className={tab===id?"active":""} onClick={()=>setTab(id)} aria-pressed={tab===id}><Icon size={15}/>{label}</button>)}</nav>

    {tab==="privacy"&&<section className="help-panel"><h2>Data Privacy</h2><p>We are a social media analytics platform built around one principle: analyze public conversations in the aggregate, never surveil individuals. Here is exactly what that means for your data.</p>{privacyBlocks.map(({icon:Icon,title,body,list})=><article className="help-block" key={title}><h3><Icon size={18}/>{title}</h3><p>{body}</p>{list&&<ul>{list.map(item=><li key={item}>{item}</li>)}</ul>}</article>)}<p className="help-updated">Privacy summary last reviewed: September 2026. This is a plain-language overview, not a substitute for the full legal policy.</p></section>}

    {tab==="terms"&&<section className="help-panel"><h2>Terms &amp; Conditions</h2><p>By using UPDATES you agree to the following terms. They exist to keep the platform ethical, accurate and safe for the public whose conversations we analyze.</p>{termsBlocks.map(({title,body})=><article className="help-block" key={title}><h3><FileText size={18}/>{title}</h3><p>{body}</p></article>)}<p className="help-updated">Terms last updated: September 2026.</p></section>}

    {tab==="faq"&&<section className="help-panel"><h2>Frequently Asked Questions</h2><p>Quick answers to the questions we hear most about data, methodology and privacy.</p>{faqs.map(item=><FaqRow key={item.q} q={item.q} a={item.a}/>)}</section>}
  </main></div>;
}
