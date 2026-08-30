import {notFound} from "next/navigation";import {TopicPage} from "@/components/TopicPage";import {reservationTopic} from "@/lib/demo-data";import {getTopic} from "@/lib/api";
export async function generateMetadata({params}:{params:Promise<{slug:string}>}){const {slug}=await params;if(slug!==reservationTopic.slug)return {};return {title:reservationTopic.title,description:reservationTopic.insight}}
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const topic=await getTopic(slug);if(!topic)notFound();return <TopicPage topic={topic}/>}
