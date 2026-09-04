import {TopicPage} from "@/components/TopicPage";
import {getTopic} from "@/lib/api";

export async function generateMetadata({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params;
  const topic=await getTopic(slug);
  return {title:`${topic.title} · Public Conversation Analysis`,description:topic.insight||topic.subtitle};
}

export default async function Page({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params;
  const topic=await getTopic(slug);
  return <TopicPage topic={topic}/>;
}
