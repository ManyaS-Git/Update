from datetime import datetime, timezone
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.database import AnalysisRunRecord, StoryRecord, TopicRecord, get_db
from app.models.schemas import AIQuestion, AIResponse, AnalysisRequest, AnalysisRunResponse, ChatQuestion, ChatResponse
from app.core.security import require_admin
router=APIRouter(prefix="/api",tags=["analysis"])

@router.post("/chat",response_model=ChatResponse)
def chat(payload:ChatQuestion,db:Session=Depends(get_db)):
    text=payload.message.strip().lower();topic=db.get(TopicRecord,payload.topic_slug) if payload.topic_slug else None;story=None
    if payload.page_path and payload.page_path.startswith("/story/"):
        try: story=db.get(StoryRecord,int(payload.page_path.split("/story/",1)[1].split("/",1)[0]))
        except (TypeError,ValueError): story=None
    if story and not topic: topic=db.get(TopicRecord,story.topic_slug)
    latest=db.scalars(select(StoryRecord).order_by(StoryRecord.published_at.desc()).limit(3)).all()
    if text in {"hi","hello","hey","hey there","namaste","hii","hello there"}:
        context=f" You’re viewing “{story.title}”." if story else (f" You’re viewing “{topic.title}”." if topic else "")
        return ChatResponse(answer=f"Hi! I’m your UPDATES news assistant.{context} Ask me to explain this story, its sentiment or confidence, find coverage on a subject, or show the latest headlines.",actions=[{"label":"Latest news","href":"/live"},{"label":"How analysis works","href":"/methodology"}])
    if any(word in text for word in ("latest","news","trending","today")):
        titles="\n".join(f"{index}. {item.title}" for index,item in enumerate(latest,1))
        return ChatResponse(answer=f"These are the three newest indexed stories:\n{titles}",actions=[{"label":"Open live feed","href":"/live"},{"label":"View top stories","href":"/#stories"}],evidence=[f"{len(latest)} newest records ordered by publication time"])
    if any(word in text for word in ("this story","this article","explain","summary","summarise","summarize","what is this")) and (story or topic):
        analytics=topic.analytics if topic else {};confidence=analytics.get("confidence",{});sentiment=analytics.get("sentiment",{});drivers=analytics.get("drivers") or [];subject=story.title if story else topic.title;summary=story.summary if story else topic.subtitle
        measured=topic.total_conversations if topic else 0;scope=confidence.get("analysis_scope","story context")
        detail=f" Current signals are {sentiment.get('negative',0)}% opposing, {sentiment.get('neutral',0)}% neutral and {sentiment.get('positive',0)}% supportive." if sentiment else ""
        caveat=f" This is based on {measured:,} {confidence.get('metric_label','signals')} with {confidence.get('level','unavailable')} confidence." if measured else " No qualified public comments have been collected yet, so audience sentiment should not be treated as measured opinion."
        driver=f" The leading theme is {drivers[0].get('title')}." if drivers else ""
        return ChatResponse(answer=f"{subject}: {summary}{detail}{driver}{caveat}",actions=[{"label":"Open full analysis","href":f"/topic/{topic.slug}"},{"label":"Methodology","href":"/methodology"}],evidence=[scope,*confidence.get("sources",[])])
    if topic and any(word in text for word in ("sentiment","positive","negative","support","oppose","reaction","feel")):
        analytics=topic.analytics;sentiment=analytics.get("sentiment",{});confidence=analytics.get("confidence",{});count=topic.total_conversations
        if not count:return ChatResponse(answer=f"I can’t claim measured public sentiment for {topic.title} yet because there are no qualified comments attached to this topic. The page may show headline-context analysis, which is different from audience opinion.",actions=[{"label":"Check sources","href":"/sources"},{"label":"Read methodology","href":"/methodology"}],evidence=["0 qualified topic comments"])
        return ChatResponse(answer=f"For {topic.title}, the current topic-scoped result is {sentiment.get('negative',0)}% opposing, {sentiment.get('neutral',0)}% neutral and {sentiment.get('positive',0)}% supportive across {count:,} {confidence.get('metric_label','signals')}. Confidence is {confidence.get('level','unavailable')}.",actions=[{"label":"View analysis","href":f"/topic/{topic.slug}"}],evidence=confidence.get("sources",[]))
    if topic and any(word in text for word in ("confidence","accurate","accuracy","geography","location","age","language","interest","demographic")):
        audience=topic.analytics.get("audience",{});confidence=topic.analytics.get("confidence",{});geo=audience.get("geography",{});age=audience.get("age_bracket",{});language=audience.get("language",{});distribution=language.get("distribution",{});dominant=max(distribution,key=distribution.get) if distribution else "Unavailable"
        return ChatResponse(answer=f"For this topic: geography is {geo.get('value','Unavailable')} ({geo.get('confidence','Unavailable')} confidence); likely age is {age.get('value','Unavailable')} ({age.get('confidence','Unavailable')} confidence); dominant language is {dominant} ({language.get('confidence','Unavailable')} confidence). These fields remain unavailable when source metadata does not support them—UPDATES does not invent demographics.",actions=[{"label":"Open analysis","href":f"/topic/{topic.slug}"},{"label":"Methodology","href":"/methodology"}],evidence=confidence.get("sources",[]))
    if any(word in text for word in ("source","api","data from","connector")):
        return ChatResponse(answer="You can inspect every news, social and model connector on the Sources page. It shows which APIs are configured, recent ingestion jobs and evidence limitations.",actions=[{"label":"Open sources","href":"/sources"}],evidence=["Connector status endpoint"])
    if any(word in text for word in ("privacy","collect","personal data","safe")):
        return ChatResponse(answer="UPDATES analyzes permitted public information in aggregate. Author identifiers are hashed, private messages are excluded, and age or geography remain unavailable unless supported by explicit public metadata.",actions=[{"label":"Read privacy guide","href":"/help#privacy"}],evidence=["UPDATES privacy and methodology policy"])
    if any(word in text for word in ("help","how","what can you")):
        return ChatResponse(answer="I can find the latest stories, explain a story’s sentiment and confidence, show connected sources, open saved items, and explain how UPDATES protects privacy.",actions=[{"label":"Help & Guide","href":"/help"},{"label":"Search news","href":"/search"}])
    stop={"find","show","search","tell","give","about","for","me","the","a","an","please","coverage","story","stories","article","articles","on","of","is","are","what","who","why","how"};terms=[word.strip(".,?!:;()[]\"'") for word in text.split()];terms=[word for word in terms if len(word)>2 and word not in stop][:5]
    if terms:
        filters=[]
        for term in terms: filters.extend((StoryRecord.title.ilike(f"%{term}%"),StoryRecord.summary.ilike(f"%{term}%"),StoryRecord.category.ilike(f"%{term}%")))
        matches=db.scalars(select(StoryRecord).where(or_(*filters)).order_by(StoryRecord.published_at.desc()).limit(3)).all()
        if matches:
            titles="\n".join(f"{index}. {item.title}" for index,item in enumerate(matches,1));query=" ".join(terms)
            return ChatResponse(answer=f"I found these relevant stories for “{query}”:\n{titles}",actions=[{"label":"Open search results","href":f"/search?q={query.replace(' ','%20')}"},{"label":"Latest feed","href":"/live"}],evidence=[f"{len(matches)} matching indexed stories"])
    return ChatResponse(answer="I couldn’t match that question to verified project data. Try naming a person, place or topic, or open a story and ask ‘Explain this story’, ‘What is the sentiment?’, or ‘How confident is the age and geography data?’",actions=[{"label":"Browse latest","href":"/live"},{"label":"Help & Guide","href":"/help"}],evidence=["No matching indexed evidence"])

@router.post("/ai/ask",response_model=AIResponse)
def ask(payload: AIQuestion,db:Session=Depends(get_db)):
    topic=db.get(TopicRecord,payload.topic_slug)
    if not topic: raise HTTPException(404,"Topic not found")
    if topic.total_conversations<=0:
        return AIResponse(answer=f"No qualified comments have been collected for {topic.title} yet. Run collection for this story before asking for sentiment, audience or trend conclusions.",evidence=["0 qualified comments for this topic","No cross-topic fallback was used"],confidence="Low",last_updated=topic.updated,provider="topic-scoped")
    analytics=topic.analytics;confidence=analytics.get("confidence",{});scope=confidence.get("analysis_scope");sentiment=analytics.get("sentiment",{});audience=analytics.get("audience",{});drivers=analytics.get("drivers",[]);negative=sentiment.get("negative",0);neutral=sentiment.get("neutral",0);positive=sentiment.get("positive",0);top_driver=drivers[0].get("title") if drivers else "No dominant narrative established";platform=audience.get("leading_platform") or "multiple collected sources"
    if scope=="public_attention_signals":
        return AIResponse(answer=f"For {topic.title}, {topic.total_conversations:,} public-attention signals are currently available from {platform}. Sentiment percentages are headline-tone context—not measured audience opinion. The leading story theme is {top_driver}.",evidence=[confidence.get("disclaimer","Public signals are not social comments"),f"Topic analytics updated {topic.updated}"],confidence="Medium" if confidence.get("level")=="Medium" else "Low",last_updated=topic.updated,provider="topic-scoped-public-signals")
    answer=f"For {topic.title}, {topic.total_conversations:,} qualified comments currently measure {negative}% opposing, {neutral}% neutral and {positive}% supportive. The leading observed source is {platform}; the strongest available narrative is {top_driver}."
    return AIResponse(answer=answer,evidence=[f"{topic.total_conversations:,} comments attached only to {topic.slug}",f"Topic analytics updated {topic.updated}"],confidence=analytics.get("confidence",{}).get("level","Medium") if analytics.get("confidence",{}).get("level") in {"Low","Medium","High"} else "Medium",last_updated=topic.updated,provider="topic-scoped")

@router.post("/analysis/run",response_model=AnalysisRunResponse)
def run(payload: AnalysisRequest,db:Session=Depends(get_db),_:None=Depends(require_admin)):
    if not db.get(TopicRecord,payload.topic_slug): raise HTTPException(404,"Topic not found")
    settings=get_settings()
    result=AnalysisRunRecord(id=str(uuid4()),topic_slug=payload.topic_slug,status="completed" if settings.demo_mode else "queued",mode="demo" if settings.demo_mode else "configured_collectors",metrics_json=json.dumps({"records_processed":52480 if settings.demo_mode else 0}),completed_at=datetime.now(timezone.utc) if settings.demo_mode else None)
    db.add(result);db.commit()
    return AnalysisRunResponse(run_id=result.id,topic_slug=result.topic_slug,status=result.status,mode=result.mode)

@router.get("/analysis/runs")
def runs(db:Session=Depends(get_db)):
    rows=db.scalars(select(AnalysisRunRecord).order_by(AnalysisRunRecord.started_at.desc()).limit(50)).all()
    return [{"run_id":r.id,"topic_slug":r.topic_slug,"status":r.status,"mode":r.mode,"started_at":r.started_at,"completed_at":r.completed_at,"metrics":json.loads(r.metrics_json)} for r in rows]

@router.get("/analysis/runs/{run_id}")
def run_status(run_id:str,db:Session=Depends(get_db)):
    r=db.get(AnalysisRunRecord,run_id)
    if not r: raise HTTPException(404,"Analysis run not found")
    return {"run_id":r.id,"topic_slug":r.topic_slug,"status":r.status,"mode":r.mode,"started_at":r.started_at,"completed_at":r.completed_at,"metrics":json.loads(r.metrics_json)}
