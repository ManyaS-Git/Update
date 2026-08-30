from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import asyncio,httpx
from app.collectors.base import BaseCollector
from app.core.config import Settings, get_settings
from app.models.schemas import NormalizedContent

class CollectorError(RuntimeError): pass

def _time(value: str | int | float | None) -> datetime:
    if isinstance(value,(int,float)): return datetime.fromtimestamp(value,tz=timezone.utc)
    if not value: return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z","+00:00"))

class OfficialCollector(BaseCollector):
    required_environment: tuple[str,...]=()
    def __init__(self,settings:Settings|None=None): self.settings=settings or get_settings()
    @property
    def configured(self)->bool: return all(bool(getattr(self.settings,name)) for name in self.required_environment)
    def require(self)->None:
        if not self.configured: raise CollectorError(f"{self.platform} credentials are not configured")
    def normalize(self,raw:dict,topic_id:str)->NormalizedContent:
        return NormalizedContent(platform=self.platform,external_id=str(raw["id"]),topic_id=topic_id,author_id=raw.get("author_id"),text=raw.get("text","").strip(),timestamp=_time(raw.get("created_at")),parent_id=raw.get("parent_id"),engagement=raw.get("engagement",{}),public_profile_signals=raw.get("public_signals",{}),raw_metadata=raw.get("metadata",{}))
    async def request(self,method:str,url:str,**kwargs)->dict:
        async with httpx.AsyncClient(timeout=30,follow_redirects=True) as client:
            for attempt in range(self.settings.collector_max_retries):
                response=await client.request(method,url,**kwargs)
                if response.status_code<400:return response.json()
                if response.status_code not in {429,500,502,503,504} or attempt+1>=self.settings.collector_max_retries:break
                retry_after=response.headers.get("retry-after")
                await asyncio.sleep(min(30,float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt))
        raise CollectorError(f"{self.platform} API returned {response.status_code}: {response.text[:300]}")

class XCollector(OfficialCollector):
    platform="x";required_environment=("x_bearer_token",)
    async def _search(self,query:str,limit:int)->list[dict]:
        self.require();rows=[];pagination_token=None
        while len(rows)<limit:
            params={"query":query,"max_results":min(100,max(10,limit-len(rows))),"tweet.fields":"author_id,conversation_id,created_at,lang,public_metrics,geo,referenced_tweets","expansions":"author_id,geo.place_id","user.fields":"location,verified","place.fields":"country,country_code,full_name,geo"}
            if pagination_token:params["pagination_token"]=pagination_token
            payload=await self.request("GET","https://api.x.com/2/tweets/search/recent",params=params,headers={"Authorization":f"Bearer {self.settings.x_bearer_token}"});users={x["id"]:x for x in payload.get("includes",{}).get("users",[])};places={x["id"]:x for x in payload.get("includes",{}).get("places",[])}
            for item in payload.get("data",[]):
                user=users.get(item.get("author_id"),{});metrics=item.get("public_metrics",{});place=places.get((item.get("geo")or{}).get("place_id"),{})
                location=place.get("full_name") or user.get("location","")
                rows.append({"id":item["id"],"text":item.get("text",""),"created_at":item.get("created_at"),"author_id":item.get("author_id"),"parent_id":item.get("conversation_id") if item.get("conversation_id")!=item.get("id") else None,"engagement":{"likes":metrics.get("like_count",0),"replies":metrics.get("reply_count",0),"shares":metrics.get("retweet_count",0)+metrics.get("quote_count",0)},"public_signals":{"location":location},"metadata":{"language_api":item.get("lang"),"verified":user.get("verified",False),"conversation_id":item.get("conversation_id"),"geo_source":"place" if place else "profile" if location else None}})
                if len(rows)>=limit:break
            pagination_token=payload.get("meta",{}).get("next_token")
            if not pagination_token:break
        return rows
    async def fetch_posts(self,topic:str,limit:int=100)->list[dict]: return await self._search(f"({topic}) -is:retweet",limit)
    async def fetch_comments(self,external_id:str,limit:int=100)->list[dict]: return await self._search(f"conversation_id:{external_id} -is:retweet",limit)

class YouTubeCollector(OfficialCollector):
    platform="youtube";required_environment=("youtube_api_key",)
    async def fetch_posts(self,topic:str,limit:int=25)->list[dict]:
        self.require();p=await self.request("GET","https://www.googleapis.com/youtube/v3/search",params={"part":"snippet","q":topic,"type":"video","maxResults":min(50,limit),"key":self.settings.youtube_api_key})
        return [{"id":x["id"]["videoId"],"text":x["snippet"].get("title","")+" "+x["snippet"].get("description",""),"created_at":x["snippet"].get("publishedAt"),"author_id":x["snippet"].get("channelId"),"engagement":{},"metadata":{"title":x["snippet"].get("title"),"channel_title":x["snippet"].get("channelTitle")}} for x in p.get("items",[])]
    async def fetch_comments(self,external_id:str,limit:int=100)->list[dict]:
        self.require();rows=[];page_token=None
        while len(rows)<limit:
            params:dict[str,Any]={"part":"snippet,replies","videoId":external_id,"textFormat":"plainText","maxResults":min(100,limit-len(rows)),"order":"time","key":self.settings.youtube_api_key}
            if page_token: params["pageToken"]=page_token
            p=await self.request("GET","https://www.googleapis.com/youtube/v3/commentThreads",params=params)
            for thread in p.get("items",[]):
                top=thread["snippet"]["topLevelComment"];s=top["snippet"]
                rows.append({"id":top["id"],"text":s.get("textDisplay",""),"created_at":s.get("publishedAt"),"author_id":(s.get("authorChannelId")or{}).get("value"),"engagement":{"likes":s.get("likeCount",0),"replies":thread["snippet"].get("totalReplyCount",0)},"metadata":{"video_id":external_id}})
                included_replies=thread.get("replies",{}).get("comments",[])
                for reply in included_replies:
                    rs=reply["snippet"];rows.append({"id":reply["id"],"text":rs.get("textDisplay",""),"created_at":rs.get("publishedAt"),"author_id":(rs.get("authorChannelId")or{}).get("value"),"parent_id":rs.get("parentId"),"engagement":{"likes":rs.get("likeCount",0)},"metadata":{"video_id":external_id}})
                total_replies=thread["snippet"].get("totalReplyCount",0)
                if total_replies>len(included_replies) and len(rows)<limit:
                    reply_page=None
                    while len(rows)<limit:
                        reply_params={"part":"snippet","parentId":top["id"],"textFormat":"plainText","maxResults":min(100,limit-len(rows)),"key":self.settings.youtube_api_key}
                        if reply_page:reply_params["pageToken"]=reply_page
                        reply_payload=await self.request("GET","https://www.googleapis.com/youtube/v3/comments",params=reply_params)
                        for reply in reply_payload.get("items",[]):
                            rs=reply["snippet"];rows.append({"id":reply["id"],"text":rs.get("textDisplay",rs.get("textOriginal","")),"created_at":rs.get("publishedAt"),"author_id":(rs.get("authorChannelId")or{}).get("value"),"parent_id":rs.get("parentId"),"engagement":{"likes":rs.get("likeCount",0)},"metadata":{"video_id":external_id}})
                        reply_page=reply_payload.get("nextPageToken")
                        if not reply_page:break
            page_token=p.get("nextPageToken")
            if not page_token: break
        return rows[:limit]

class RedditCollector(OfficialCollector):
    platform="reddit";required_environment=("reddit_client_id","reddit_client_secret")
    async def _token(self)->str:
        self.require();p=await self.request("POST","https://www.reddit.com/api/v1/access_token",data={"grant_type":"client_credentials"},auth=(self.settings.reddit_client_id,self.settings.reddit_client_secret),headers={"User-Agent":self.settings.reddit_user_agent});return p["access_token"]
    async def _get(self,path:str,params:dict)->Any:
        token=await self._token();return await self.request("GET",f"https://oauth.reddit.com{path}",params=params,headers={"Authorization":f"Bearer {token}","User-Agent":self.settings.reddit_user_agent})
    async def fetch_posts(self,topic:str,limit:int=25)->list[dict]:
        p=await self._get("/search",{"q":topic,"sort":"new","limit":min(100,limit),"type":"link","raw_json":1});rows=[]
        for child in p.get("data",{}).get("children",[]):
            x=child["data"];rows.append({"id":x["id"],"text":f"{x.get('title','')} {x.get('selftext','')}","created_at":x.get("created_utc"),"author_id":x.get("author_fullname")or x.get("author"),"engagement":{"likes":max(x.get("score",0),0),"replies":x.get("num_comments",0)},"public_signals":{"community":x.get("subreddit","")},"metadata":{"subreddit":x.get("subreddit"),"permalink":x.get("permalink")}})
        return rows
    async def fetch_comments(self,external_id:str,limit:int=100)->list[dict]:
        p=await self._get(f"/comments/{external_id}",{"limit":min(500,limit),"depth":10,"raw_json":1});rows=[]
        def walk(children:list[dict]):
            for child in children:
                if child.get("kind")!="t1": continue
                x=child["data"];replies=x.get("replies");reply_children=(replies or {}).get("data",{}).get("children",[]) if isinstance(replies,dict) else []
                rows.append({"id":x["id"],"text":x.get("body",""),"created_at":x.get("created_utc"),"author_id":x.get("author_fullname")or x.get("author"),"parent_id":x.get("parent_id"),"engagement":{"likes":max(x.get("score",0),0),"replies":len(reply_children)},"public_signals":{"community":x.get("subreddit","")},"metadata":{"subreddit":x.get("subreddit"),"permalink":x.get("permalink")}});walk(reply_children)
        if len(p)>1: walk(p[1].get("data",{}).get("children",[]))
        return rows[:limit]

class FacebookCollector(OfficialCollector):
    platform="facebook";required_environment=("facebook_page_access_token",)
    async def fetch_posts(self,topic:str,limit:int=25)->list[dict]: raise CollectorError("Facebook discovery is not unrestricted; provide authorised Page post IDs in targets.facebook")
    async def fetch_comments(self,external_id:str,limit:int=100)->list[dict]:
        self.require();url=f"https://graph.facebook.com/{self.settings.meta_graph_version}/{external_id}/comments";params={"fields":"id,message,created_time,from,like_count,comment_count,parent","limit":min(100,limit),"access_token":self.settings.facebook_page_access_token};rows=[]
        while url and len(rows)<limit:
            p=await self.request("GET",url,params=params);params={};rows.extend([{"id":x["id"],"text":x.get("message",""),"created_at":x.get("created_time"),"author_id":(x.get("from")or{}).get("id"),"parent_id":(x.get("parent")or{}).get("id"),"engagement":{"likes":x.get("like_count",0),"replies":x.get("comment_count",0)},"metadata":{"managed_page_content":True}} for x in p.get("data",[])]);url=p.get("paging",{}).get("next")
        return rows[:limit]

class InstagramCollector(OfficialCollector):
    platform="instagram";required_environment=("instagram_access_token",)
    async def fetch_posts(self,topic:str,limit:int=25)->list[dict]: raise CollectorError("Instagram discovery is limited to authorised professional accounts; provide media IDs in targets.instagram")
    async def fetch_comments(self,external_id:str,limit:int=100)->list[dict]:
        self.require();url=f"https://graph.instagram.com/{self.settings.meta_graph_version}/{external_id}/comments";params={"fields":"id,text,timestamp,from,like_count,parent_id","limit":min(100,limit),"access_token":self.settings.instagram_access_token};rows=[]
        while url and len(rows)<limit:
            p=await self.request("GET",url,params=params);params={};rows.extend([{"id":x["id"],"text":x.get("text",""),"created_at":x.get("timestamp"),"author_id":(x.get("from")or{}).get("id"),"parent_id":x.get("parent_id"),"engagement":{"likes":x.get("like_count",0)},"metadata":{"professional_account_content":True}} for x in p.get("data",[])]);url=p.get("paging",{}).get("next")
        return rows[:limit]

COLLECTORS={"x":XCollector,"youtube":YouTubeCollector,"reddit":RedditCollector,"facebook":FacebookCollector,"instagram":InstagramCollector}
def get_collector(name:str,settings:Settings|None=None)->OfficialCollector:
    if name not in COLLECTORS: raise CollectorError(f"Unsupported platform: {name}")
    return COLLECTORS[name](settings)
