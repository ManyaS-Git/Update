import {reservationTopic} from "./demo-data";
import type {Driver,EmergingSnapshot,PublicVoice,Story,Topic,TrendPoint} from "@/types";

const API_URL=process.env.NEXT_PUBLIC_API_URL;
export const CLIENT_API_URL=process.env.NEXT_PUBLIC_API_URL??"http://127.0.0.1:8001";
const titleCase=(value:string)=>value.toLowerCase().replace(/(^|_)(\w)/g,(_,space,letter)=>`${space?" ":""}${letter.toUpperCase()}`);

async function getJson<T>(path:string):Promise<T>{
  if(!API_URL)throw new Error("API URL is not configured");
  const response=await fetch(`${API_URL}${path}`,{cache:"no-store"});
  if(!response.ok)throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

type Meta={slug:string;title:string;subtitle:string;image?:string;category?:string;demo?:boolean;total_conversations:number;updated:string};
type Sentiment={negative:number;neutral:number;positive:number;change_last_6h:number};
type Audience={geography:{value:string;confidence?:string};language:{distribution:Record<string,number>;confidence?:string};age_bracket:{value:string;confidence:string};interest_groups:string[];key_topics?:string[];leading_platform?:string;confidence?:{interests?:string;topics?:string;platform?:string}};
type TrendApi={time:string;volume:number;negative:number}[];
type DriverApi={title:string;description:string;status:string}[];
type VoiceApi={quote:string;label:string;stance?:string;source?:string}[];
type Confidence={level:string;sources:string[];qualified_conversations:number;qualified_public_signals?:number;low_signal_excluded_or_downweighted:number;analysis_scope?:string;metric_label?:string};
type Brief={insight:string};
type Network={nodes:{id:string;label:string;centrality:number}[];edges:{source:string;target:string;weight:number}[]};

/** Aggregates the independent FastAPI endpoints into the dashboard model. */
export async function getTopic(slug:string):Promise<Topic|null>{
  if(slug!==reservationTopic.slug&&!API_URL)return null;
  if(!API_URL)return reservationTopic;
  try{
    const [meta,sentiment,audience,trends,drivers,voices,network,confidence,brief]=await Promise.all([
      getJson<Meta>(`/api/topics/${slug}`),getJson<Sentiment>(`/api/topics/${slug}/sentiment`),
      getJson<Audience>(`/api/topics/${slug}/audience`),getJson<TrendApi>(`/api/topics/${slug}/trends`),
      getJson<DriverApi>(`/api/topics/${slug}/drivers`),getJson<VoiceApi>(`/api/topics/${slug}/voices`),
      getJson<Network>(`/api/topics/${slug}/network`),getJson<Confidence>(`/api/topics/${slug}/confidence`),
      getJson<Brief>(`/api/topics/${slug}/brief`),
    ]);
    const language=Object.entries(audience.language.distribution).sort((a,b)=>b[1]-a[1])[0]?.[0]??"Unavailable";
    const mappedTrends:TrendPoint[]=trends.map(point=>({time:point.time,volume:point.volume,sentiment:point.negative}));
    const mappedDrivers:Driver[]=drivers.map(driver=>({title:driver.title,description:driver.description,status:titleCase(driver.status) as Driver["status"]}));
    const mappedVoices:PublicVoice[]=voices.map(voice=>({quote:voice.quote,label:voice.source?`${voice.label} · ${voice.source}`:voice.label,tone:voice.stance==="supportive"?"supporting":voice.stance==="opposing"?"concerned":"neutral"}));
    const rawAge=audience.age_bracket.value??"";const age=rawAge&&/^\d/.test(rawAge)?`${rawAge} years`:rawAge;
    return {slug:meta.slug,title:meta.title,subtitle:meta.subtitle,image:meta.image,category:meta.category,demo:Boolean(meta.demo),preview:Boolean(meta.demo&&meta.total_conversations===0),analysisScope:confidence.analysis_scope,metricLabel:confidence.metric_label??"public conversations analysed",totalConversations:meta.total_conversations,updated:meta.updated,sentiment:{negative:sentiment.negative,neutral:sentiment.neutral,positive:sentiment.positive},sentimentChange:sentiment.change_last_6h,insight:brief.insight,audience:{geography:audience.geography.value,geographyConfidence:audience.geography.confidence??"Unavailable",language,languageConfidence:audience.language.confidence??"Unavailable",age,ageConfidence:audience.age_bracket.confidence,interests:audience.interest_groups.join(" & "),interestsConfidence:audience.confidence?.interests??"Unavailable",topics:audience.key_topics??[],topicsConfidence:audience.confidence?.topics??"Unavailable",platform:audience.leading_platform??"",platformConfidence:audience.confidence?.platform??"Unavailable"},drivers:mappedDrivers,voices:mappedVoices,trends:mappedTrends,confidence:{sources:confidence.sources,qualified:confidence.qualified_public_signals??confidence.qualified_conversations,lowSignal:confidence.low_signal_excluded_or_downweighted,level:confidence.level},network:{nodes:network.nodes.map(node=>({id:node.id,label:node.label,group:"dynamic",size:Math.max(20,Math.round(node.centrality*50))})),edges:network.edges}};
  }catch{return slug===reservationTopic.slug?reservationTopic:null}
}

export async function askAnalyst(topicSlug:string,question:string){
  const response=await fetch(`${CLIENT_API_URL}/api/ai/ask`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic_slug:topicSlug,question})});
  if(!response.ok)throw new Error("The analyst is temporarily unavailable");
  return response.json() as Promise<{answer:string;evidence:string[];confidence:string;last_updated:string}>;
}

async function clientJson<T>(path:string,init?:RequestInit):Promise<T>{
  const response=await fetch(`${CLIENT_API_URL}${path}`,init);
  if(!response.ok)throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}
export const getStories=(path="/api/stories")=>clientJson<Story[]>(path);
export const getEmergingTopics=()=>clientJson<EmergingSnapshot>("/api/emerging?limit=6");
export const refreshLatestNews=()=>clientJson<{provider:string;received:number;added:number;stories:Story[]}>("/api/news/refresh",{method:"POST"});
export const getStory=(id:string)=>clientJson<Story>(`/api/stories/${id}`);
export const getBookmarks=()=>clientJson<Story[]>("/api/bookmarks");
export const getFeed=()=>clientJson<Story[]>("/api/feed");
export const searchContent=(query:string)=>clientJson<{query:string;stories:Story[];topics:{slug:string;title:string;subtitle:string;updated:string}[]}>(`/api/search?q=${encodeURIComponent(query)}`);
export const setBookmark=(id:string,enabled:boolean)=>clientJson<{story_id:string;bookmarked:boolean}>(`/api/bookmarks/${id}`,{method:enabled?"POST":"DELETE"});
export const getPreferences=()=>clientJson<{notifications_enabled:boolean}>("/api/preferences");
export const setNotifications=(enabled:boolean)=>clientJson<{notifications_enabled:boolean}>("/api/preferences/notifications",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({enabled})});
export const chatWithAssistant=(message:string,topicSlug?:string,pagePath?:string)=>clientJson<{answer:string;actions:{label:string;href:string}[];evidence:string[]}>("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message,topic_slug:topicSlug,page_path:pagePath})});
export interface ConnectorStatus{platform:string;configured:boolean;description:string;credential_fields:string[];discovery_supported:boolean;requires_targets:boolean}
export interface IngestionJob{job_id:string;topic_slug:string;platforms:string[];query:string;status:string;results:Record<string,{fetched:number;stored:number}>;errors:Record<string,string>;started_at:string;completed_at:string|null}
export interface TopicSummary{slug:string;title:string;subtitle:string;total_conversations:number;updated:string;demo:boolean}
export interface AutomationStatus{status:string;enabled:boolean;interval_minutes:number;configured_platforms:string[];requested_platforms:string[];credential_setup_required:boolean;last_started:string|null;last_completed:string|null;topics_processed:number;comments_stored:number;errors:Record<string,unknown>}
export const getConnectors=()=>clientJson<ConnectorStatus[]>("/api/connectors");
export const getTopics=()=>clientJson<TopicSummary[]>("/api/topics");
export const getModelStatus=()=>clientJson<{sentiment:{requested_provider:string;active_provider:string;model:string;local_runtime_installed:boolean;endpoint_configured:boolean;last_error:string|null;model_card_note:string};safety:{active_provider:string;model:string;note:string}}>("/api/models/status");
export const getIngestionJobs=()=>clientJson<IngestionJob[]>("/api/ingestion/jobs");
export const getAutomationStatus=()=>clientJson<AutomationStatus>("/api/ingestion/automation/status");
export const runAutomationNow=()=>clientJson<AutomationStatus>("/api/ingestion/automation/run-now",{method:"POST"});
export const runIngestion=(payload:{topic_slug:string;query:string;platforms:string[];targets:Record<string,string[]>;max_items:number})=>clientJson<{job_id:string;status:string;results:Record<string,{fetched:number;stored:number}>;errors:Record<string,string>}>("/api/ingestion/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
export const getCommentSummary=()=>clientJson<Record<string,unknown>>("/api/comments/summary");
export const classifyComment=(text:string)=>clientJson<Record<string,unknown>>("/api/classify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text,context:"reservation policy",platform:"manual"})});
