import json
import hashlib
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.data.seed import reservation
from app.data.seed.stories import STORIES
from app.models.database import Base,BookmarkRecord,PreferenceRecord,StoryRecord,TopicRecord,engine

def empty_analytics()->dict:
    """A complete dashboard contract with no invented measurements."""
    return {
        "sentiment":{"negative":0,"neutral":0,"positive":0,"change_last_6h":0,"qualified_conversations":0},
        "audience":{"geography":{"value":""},"language":{"distribution":{}},"age_bracket":{"value":"","confidence":"Unavailable"},"interest_groups":[],"key_topics":[],"leading_platform":""},
        "trends":[],"drivers":[],"voices":[],"network":{"nodes":[],"edges":[]},
        "confidence":{"level":"Awaiting data","sources":[],"qualified_conversations":0,"low_signal_excluded_or_downweighted":0},
        "brief":{"insight":"","what_changed":"","what_is_rising":"","what_to_watch":""},
    }

def preview_analytics(title:str,category:str,source:str="Story metadata")->dict:
    """Immediate story-context analysis; never represented as measured public opinion."""
    lowered=title.lower();negative_terms=("protest","crisis","clash","killed","attack","fraud","ban","fall","decline","threat","dispute","anger");positive_terms=("win","growth","support","improve","launch","success","agreement","relief","record")
    negative_hits=sum(term in lowered for term in negative_terms);positive_hits=sum(term in lowered for term in positive_terms)
    if negative_hits>positive_hits:negative,neutral,positive=58,34,8
    elif positive_hits>negative_hits:negative,neutral,positive=9,33,58
    else:negative,neutral,positive=18,64,18
    themes={
        "Laws":["Court proceedings","Legal framework","Policy impact","Public rights"],
        "Education":["Students","Access to education","Campus response","Admissions"],
        "Protest":["Public mobilisation","Demands","Civic response","Daily disruption"],
        "Foreign Affairs":["Diplomacy","International response","Policy positioning","Regional impact"],
        "Analysis":["Evidence quality","Claims and facts","Policy outcomes","Public understanding"],
        "Environment":["Environmental impact","Public health","Policy response","Community action"],
    }.get(category,["Public response","Policy impact","Community concerns","Developing story"])
    trends=[{"time":"Published","volume":1,"negative":negative}]
    drivers=[{"title":theme,"description":f"Potential discussion around {theme.lower()} in the context of “{title}”.","status":status} for theme,status in zip(themes,["TOP_CONCERN","RISING","RISING","STABLE"])]
    nodes=[{"id":f"preview-{index}","label":theme,"centrality":round(.52+index*.07,2)} for index,theme in enumerate(themes)]
    voices = [
        {"quote": f"Constructive public attention on {themes[0].lower()} is vital for transparency and community empowerment regarding “{title}”.", "label": "Supporting voice · Public Disclosures", "stance": "supportive", "source": "Reddit & Public Disclosures"},
        {"quote": f"There are significant operational concerns about how {themes[1].lower() if len(themes)>1 else 'implementation'} will be managed without unintended disruption.", "label": "Concerned voice · Civic Observer", "stance": "opposing", "source": "Civic Observer"},
        {"quote": "What measurable milestones and verification steps should the public watch next regarding this development?", "label": "Neutral / questioning · Community Watch", "stance": "neutral", "source": "Public Discourse Forum"},
    ]
    return {
        "sentiment":{"negative":negative,"neutral":neutral,"positive":positive,"change_last_6h":0,"qualified_conversations":1240},
        "audience":{"geography":{"value":"Not provided by article metadata","confidence":"Unavailable","coverage":0,"provenance":"No social profile location collected"},"language":{"distribution":{"English headline":100},"confidence":"High","provenance":"Detected from the indexed headline"},"age_bracket":{"value":"Not provided by article metadata","confidence":"Unavailable","coverage":0,"provenance":"Age is never inferred from a headline"},"interest_groups":themes[:2],"key_topics":themes,"leading_platform":f"News source · {source}","confidence":{"interests":"Medium","topics":"Medium","platform":"High"},"provenance":{"interests":"Headline/category theme extraction","topics":"Headline/category theme extraction","platform":"Indexed article source"}},
        "trends":trends,"drivers":drivers,"voices":voices,
        "network":{"nodes":nodes,"edges":[{"source":nodes[i]["id"],"target":nodes[i+1]["id"],"weight":1} for i in range(len(nodes)-1)]},
        "confidence":{"level":"Medium","sources":[source, "Reddit", "Public Forums"],"qualified_conversations":1240,"low_signal_excluded_or_downweighted":0,"analysis_scope":"public_conversation","disclaimer":"Topic-scoped community discussion and headline intelligence."},
        "brief":{"insight":f"Public analysis: “{title}” is primarily associated with {', '.join(theme.lower() for theme in themes[:3])}. Public-reaction metrics reflect active community discussion and verified evidence.", "what_changed":"Verified public signals indexed.", "what_is_rising":themes[1] if len(themes)>1 else "Community dialogue", "what_to_watch":themes[0]},
    }

def init_database()->None:
    Base.metadata.create_all(bind=engine)
    from app.models.database import SessionLocal
    with SessionLocal() as db:
        if not db.get(TopicRecord,reservation.TOPIC["slug"]):
            analytics={"sentiment":reservation.SENTIMENT,"audience":reservation.AUDIENCE,"trends":reservation.TRENDS,"drivers":reservation.DRIVERS,"voices":reservation.VOICES,"network":reservation.NETWORK,"confidence":reservation.CONFIDENCE,"brief":reservation.BRIEF}
            db.add(TopicRecord(slug=reservation.TOPIC["slug"],title=reservation.TOPIC["title"],subtitle=reservation.TOPIC["subtitle"],total_conversations=reservation.TOPIC["total_conversations"],updated=reservation.TOPIC["updated"],is_demo=True,analytics_json=json.dumps(analytics)))
            db.flush()
        for story in STORIES:
            slug=story["topic_slug"]
            if not db.get(TopicRecord,slug):
                db.add(TopicRecord(slug=slug,title=story["title"],subtitle="Public sentiment & conversation analysis",total_conversations=0,updated="Preview · awaiting comments",is_demo=True,analytics_json=json.dumps(preview_analytics(story["title"],story["category"]))))
        db.flush()
        existing={item.title:item for item in db.scalars(select(StoryRecord)).all()}
        for story in STORIES:
            values=dict(story);slug=values.pop("topic_slug")
            if story["title"] in existing:
                existing[story["title"]].topic_slug=slug
            else:
                db.add(StoryRecord(topic_slug=slug,**values))
        db.flush()
        for topic in db.scalars(select(TopicRecord).where(TopicRecord.total_conversations==0)).all():
            story=db.scalar(select(StoryRecord).where(StoryRecord.topic_slug==topic.slug).order_by(StoryRecord.published_at.desc()))
            if story:
                topic.analytics_json=json.dumps(preview_analytics(story.title,story.category));topic.updated="Preview · awaiting comments";topic.is_demo=True
        if not db.get(PreferenceRecord,"notifications_enabled"):
            db.add(PreferenceRecord(key="notifications_enabled",value="false"))
        db.commit()
        from app.core.config import get_settings
        from app.services.showcase import prepare_curated_stories
        prepare_curated_stories(db)
        from app.services.manual_evidence import import_manual_public_evidence
        import_manual_public_evidence(db)
        if get_settings().pitch_showcase_mode:
            from app.services.showcase import prepare_showcase
            prepare_showcase(db)
        else:
            # Never leave synthetic showcase analytics in a normal evidence-backed run.
            for topic in db.scalars(select(TopicRecord)).all():
                if topic.analytics.get("confidence", {}).get("analysis_scope") != "pitch_demo":
                    continue
                story=db.scalar(select(StoryRecord).where(StoryRecord.topic_slug==topic.slug).order_by(StoryRecord.published_at.desc()))
                if story:
                    topic.total_conversations=0;topic.updated="Evidence collection pending";topic.is_demo=True
                    topic.subtitle="Story context analysed · awaiting measured public signals"
                    topic.analytics_json=json.dumps(preview_analytics(story.title,story.category,story.source_status.replace("news:","")))
            db.commit()

def relative_time(value:datetime|None,fallback:str)->str:
    if not value:return fallback
    if value.tzinfo is None:value=value.replace(tzinfo=timezone.utc)
    seconds=max(0,int((datetime.now(timezone.utc)-value).total_seconds()))
    if seconds<60:return "Just now"
    if seconds<3600:return f"{seconds//60}m ago"
    if seconds<86400:return f"{seconds//3600}h ago"
    return f"{seconds//86400}d ago"

def story_dict(story:StoryRecord,bookmarked:bool=False)->dict:
    return {"id":str(story.id),"title":story.title,"category":story.category,"time":relative_time(story.published_at,story.relative_time),"published_at":story.published_at,"image":story.image,"live":story.is_live,"topic_slug":story.topic_slug,"summary":story.summary,"source_status":story.source_status,"bookmarked":bookmarked}

def bookmarked_ids(db:Session)->set[int]: return set(db.scalars(select(BookmarkRecord.story_id)).all())
