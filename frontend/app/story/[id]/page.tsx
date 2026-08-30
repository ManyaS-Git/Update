import {StoryDetail} from "@/components/StoryDetail";
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <StoryDetail id={id}/>}
