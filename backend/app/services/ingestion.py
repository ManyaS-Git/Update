from __future__ import annotations
from collections import Counter
from datetime import datetime,timedelta,timezone
import hashlib,hmac,json,secrets
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.collectors.adapters import CollectorError,get_collector
from app.models.database import CommentAnalysisRecord,IngestionJobRecord,SourceCommentRecord,TopicRecord
from app.models.schemas import CommentInput,IngestionRequest
from app.services.intelligence import CommentIntelligenceService
from app.core.config import get_settings

_EPHEMERAL_PRIVACY_SECRET=secrets.token_bytes(32)

def _hash_author(value:str|None)->str|None:
    if not value:return None
    configured=get_settings().privacy_hash_secret;secret=configured.encode() if configured else _EPHEMERAL_PRIVACY_SECRET
    return hmac.new(secret,value.encode(),hashlib.sha256).hexdigest()

def _store(db:Session,topic_slug:str,platform:str,raw:dict,service:CommentIntelligenceService)->bool:
    collector=get_collector(platform);item=collector.normalize(raw,topic_slug)
    if not item.text:return False
    existing=db.scalar(select(SourceCommentRecord).where(SourceCommentRecord.platform==platform,SourceCommentRecord.external_id==item.external_id))
    if existing:return False
    record=SourceCommentRecord(topic_slug=topic_slug,platform=platform,external_id=item.external_id,parent_external_id=item.parent_id,author_hash=_hash_author(item.author_id),text=item.text,published_at=item.timestamp,engagement_json=json.dumps(item.engagement),public_signals_json=json.dumps(item.public_profile_signals),raw_metadata_json=json.dumps(item.raw_metadata));db.add(record);db.flush()
    result=service.analyse(CommentInput(text=item.text,context=topic_slug,platform=platform,engagement=item.engagement,public_signals=item.public_profile_signals))
    db.add(CommentAnalysisRecord(comment_id=record.id,sentiment=result.sentiment,sentiment_score=result.sentiment_score,stance=result.stance,emotion=result.emotion,safety=result.safety,language=result.language,interests_json=json.dumps(result.interests),geography=result.geography,age_bracket=result.age_bracket,inference_json=json.dumps({"confidence":result.confidence,"evidence":result.evidence,"signal_quality":result.signal_quality,"signal_classification":result.signal_classification,"safety_model":result.safety_model_name}),influence_score=result.influence_score,model_name=result.model_name));return True

def _percent(count:int,total:int)->int:
    return round(100*count/total) if total else 0

def _distribution(counts:Counter,total:int,keys:list[str]|None=None)->dict[str,int]:
    names=keys or [name for name,_ in counts.most_common()]
    values={name:_percent(counts[name],total) for name in names}
    if values:
        leader=max(names,key=lambda name:counts[name]);values[leader]+=100-sum(values.values())
    return values

def _utc(value:datetime)->datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

def _human_platform(name:str)->str:
    return {"x":"X (Twitter)","youtube":"YouTube","reddit":"Reddit","facebook":"Facebook","instagram":"Instagram"}.get(name,name.title())

def _confidence_label(score:float,coverage:float=1)->str:
    if coverage<=0:return "Unavailable"
    combined=score*min(1,coverage)
    return "High" if combined>=.7 else "Medium" if combined>=.4 else "Low"

def _driver_description(name:str,count:int,total:int)->str:
    return f"Appears in {count} of {total} analysed conversations and is a leading discussion theme."

def _representative_voices(rows:list[tuple[SourceCommentRecord,CommentAnalysisRecord]])->list[dict]:
    labels={"supportive":"Supporting voice","opposing":"Concerned voice","questioning":"Neutral / questioning voice","neutral":"Neutral voice"}
    result=[]
    for stance in ("supportive","opposing","questioning","neutral"):
        candidates=[(comment,analysis) for comment,analysis in rows if analysis.stance==stance]
        if not candidates:continue
        comment,_=max(candidates,key=lambda pair:(pair[1].influence_score,pair[0].published_at))
        quote=" ".join(comment.text.split())[:280]
        result.append({"quote":quote,"label":labels[stance],"stance":stance,"source":_human_platform(comment.platform)})
        if len(result)==3:break
    used={item["quote"] for item in result}
    for comment,analysis in sorted(rows,key=lambda pair:pair[1].influence_score,reverse=True):
        quote=" ".join(comment.text.split())[:280]
        if quote in used:continue
        result.append({"quote":quote,"label":labels.get(analysis.stance,"Representative voice"),"stance":analysis.stance,"source":_human_platform(comment.platform)});used.add(quote)
        if len(result)==3:break
    return result

def _conversation_network(rows:list[tuple[SourceCommentRecord,CommentAnalysisRecord]])->dict:
    node_counts=Counter();edge_counts=Counter()
    for _,analysis in rows:
        labels=sorted(set(json.loads(analysis.interests_json or "[]")))
        node_counts.update(labels)
        for index,source in enumerate(labels):
            for target in labels[index+1:]:edge_counts[(source,target)]+=1
    nodes=[{"id":name.lower().replace(" ","-"),"label":name,"centrality":round(count/max(1,len(rows)),3)} for name,count in node_counts.most_common(8)]
    if not nodes:
        platforms=Counter(_human_platform(comment.platform) for comment,_ in rows)
        nodes=[{"id":f"source-{index}","label":name,"centrality":round(count/max(1,len(rows)),3)} for index,(name,count) in enumerate(platforms.most_common(8))]
    ids={node["label"]:node["id"] for node in nodes}
    edges=[{"source":ids[source],"target":ids[target],"weight":count} for (source,target),count in edge_counts.most_common(12) if source in ids and target in ids]
    return {"nodes":nodes,"edges":edges}

def refresh_topic_analytics(db:Session,topic_slug:str)->None:
    topic=db.get(TopicRecord,topic_slug)
    if not topic:return
    rows=db.execute(select(SourceCommentRecord,CommentAnalysisRecord).join(CommentAnalysisRecord,CommentAnalysisRecord.comment_id==SourceCommentRecord.id).where(SourceCommentRecord.topic_slug==topic_slug)).all()
    if not rows:return
    analytics=topic.analytics;sentiments=Counter(a.sentiment for _,a in rows);languages=Counter(a.language for _,a in rows);geographies=Counter(a.geography for _,a in rows if a.geography);ages=Counter(a.age_bracket for _,a in rows if a.age_bracket);platforms=Counter(c.platform for c,_ in rows);interests=Counter(interest for _,a in rows for interest in json.loads(a.interests_json or "[]"));inferences=[json.loads(a.inference_json or "{}") for _,a in rows]
    total=len(rows);now=datetime.now(timezone.utc);recent=[a for c,a in rows if _utc(c.published_at)>=now-timedelta(hours=6)];previous=[a for c,a in rows if now-timedelta(hours=12)<=_utc(c.published_at)<now-timedelta(hours=6)];recent_negative=_percent(sum(a.sentiment=="negative" for a in recent),len(recent));previous_negative=_percent(sum(a.sentiment=="negative" for a in previous),len(previous));change=recent_negative-previous_negative if previous else 0
    sentiment_distribution=_distribution(sentiments,total,["negative","neutral","positive"]);analytics["sentiment"]={**sentiment_distribution,"change_last_6h":change,"qualified_conversations":total}
    confidence_values=lambda key:[float(item.get("confidence",{}).get(key,0)) for item in inferences];average=lambda values:sum(values)/len(values) if values else 0;geo_coverage=sum(geographies.values())/total;age_coverage=sum(ages.values())/total;language_score=average(confidence_values("language"));interest_score=average(confidence_values("interests"))
    audience=analytics.setdefault("audience",{});audience["language"]={"distribution":_distribution(languages,total),"confidence":_confidence_label(language_score),"provenance":"Multilingual classifier applied to collected comments"};audience["geography"]={"value":geographies.most_common(1)[0][0] if geographies else "Not available from public source metadata","confidence":_confidence_label(average(confidence_values("geography")),geo_coverage),"coverage":_percent(sum(geographies.values()),total),"provenance":"Explicit public profile or record metadata only"};audience["age_bracket"]={"value":ages.most_common(1)[0][0] if ages else "Not available from public source metadata","confidence":_confidence_label(average(confidence_values("age")),age_coverage),"coverage":_percent(sum(ages.values()),total),"provenance":"Explicit broad age metadata only; never inferred from writing"};audience["interest_groups"]=[name for name,_ in interests.most_common(3)] or ["No recurring interest theme detected"];audience["key_topics"]=[name for name,_ in interests.most_common(5)] or ["No recurring topic detected"];audience["leading_platform"]=f"{_human_platform(platforms.most_common(1)[0][0])} · {_percent(platforms.most_common(1)[0][1],total)}% of collected data";audience["confidence"]={"interests":_confidence_label(interest_score),"topics":_confidence_label(interest_score),"platform":"High"};audience["provenance"]={"interests":"Aggregate theme classifier across collected comments","topics":"Recurring classified themes across collected comments","platform":"Observed collector record counts"}
    bucket_rows:dict[str,list[CommentAnalysisRecord]]={}
    for comment,analysis in rows:bucket_rows.setdefault(_utc(comment.published_at).strftime("%Y-%m-%d %H:00"),[]).append(analysis)
    analytics["trends"]=[{"time":label,"volume":len(values),"negative":_percent(sum(item.sentiment=="negative" for item in values),len(values))} for label,values in sorted(bucket_rows.items())]
    top_interests=interests.most_common(4)
    if not top_interests:
        stances=Counter(a.stance for _,a in rows);top_interests=[(f"{name.title()} viewpoints",count) for name,count in stances.most_common(4)]
    analytics["drivers"]=[{"title":name,"description":_driver_description(name,count,total),"status":"TOP_CONCERN" if index==0 else "RISING" if index<3 else "STABLE"} for index,(name,count) in enumerate(top_interests)]
    analytics["voices"]=_representative_voices(rows);analytics["network"]=_conversation_network(rows)
    signal_classes=Counter(item.get("signal_classification","UNKNOWN") for item in inferences);low_signal=signal_classes["NOISE"]+signal_classes["LOW_SIGNAL"];qualified=max(0,total-low_signal);coverage=(sum(geographies.values())+sum(ages.values()))/(2*total);confidence_level="High" if total>=100 and qualified/total>=.8 else "Medium" if total>=25 and qualified/total>=.6 else "Low"
    source_names=[_human_platform(name) for name in sorted(platforms)];analytics["confidence"]={"level":confidence_level,"sources":source_names,"qualified_conversations":qualified,"low_signal_excluded_or_downweighted":low_signal,"metadata_coverage":round(coverage,3),"model":"Multilingual sentiment, stance and safety classifiers","analysis_scope":"public_conversation","refreshed_at":datetime.now(timezone.utc).isoformat()}
    dominant=max(sentiments,key=sentiments.get);themes=[name for name,_ in interests.most_common(3)];theme_text=", ".join(themes) if themes else "the selected story";analytics["brief"]={"insight":f"The conversation is predominantly {dominant} ({_percent(sentiments[dominant],total)}%). The strongest recurring themes are {theme_text}. Analysis covers {total:,} collected public comments across {', '.join(source_names)}.","what_changed":f"Opposing sentiment changed by {change:+d} percentage points in the latest six-hour comparison window.","what_is_rising":themes[0] if themes else "No recurring theme detected","what_to_watch":themes[1] if len(themes)>1 else themes[0] if themes else "Collect more comments"}
    topic.total_conversations=total;topic.updated="just now";topic.is_demo=False;topic.analytics_json=json.dumps(analytics)

async def run_ingestion(db:Session,payload:IngestionRequest)->dict:
    if not db.get(TopicRecord,payload.topic_slug):raise CollectorError("Topic not found")
    job=IngestionJobRecord(id=str(uuid4()),topic_slug=payload.topic_slug,platforms_json=json.dumps(payload.platforms),query=payload.query,status="running");db.add(job);db.commit();service=CommentIntelligenceService();results={};errors={}
    for platform in payload.platforms:
        collector=get_collector(platform);added=0
        try:
            targets=payload.targets.get(platform,[])
            if targets:
                raw=[]
                for target in targets:
                    raw.extend(await collector.fetch_comments(target,max(1,payload.max_items-len(raw))))
                    if len(raw)>=payload.max_items:break
            elif platform=="x":raw=await collector.fetch_posts(payload.query,payload.max_items)
            elif platform in {"youtube","reddit"}:
                posts=await collector.fetch_posts(payload.query,min(10,payload.max_items));raw=[]
                for post in posts:
                    raw.extend(await collector.fetch_comments(post["id"],max(1,payload.max_items-len(raw))))
                    if len(raw)>=payload.max_items:break
            else:raw=await collector.fetch_posts(payload.query,payload.max_items)
            for item in raw[:payload.max_items]:added+=int(_store(db,payload.topic_slug,platform,item,service))
            db.commit();results[platform]={"fetched":len(raw[:payload.max_items]),"stored":added}
        except Exception as exc:
            db.rollback();errors[platform]=str(exc)
    refresh_topic_analytics(db,payload.topic_slug);job=db.get(IngestionJobRecord,job.id);job.results_json=json.dumps(results);job.error_json=json.dumps(errors);job.status="completed" if results else "failed";job.completed_at=datetime.now(timezone.utc);db.commit()
    return {"job_id":job.id,"status":job.status,"results":results,"errors":errors}
