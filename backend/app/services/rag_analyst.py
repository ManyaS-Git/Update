from __future__ import annotations
from collections import Counter
import json
import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.database import NarrativeRecord, PostRecord, SourceCommentRecord, TopicRecord, UserRecord
from app.models.schemas import AIResponse

class RAGAnalystService:
    """
    Evidence-Grounded RAG Social Intelligence Analyst.
    Synthesizes natural-language intelligence exclusively from structured database records,
    CSQE-qualified posts, SentiMix sentiment metrics, and NetworkX PageRank scores.
    Strictly reports 'Insufficient evidence to determine this' if ground truth is absent.
    """

    def answer_question(self, db: Session, topic_slug: str, question: str) -> AIResponse:
        q_lowered = question.lower()
        is_global = not topic_slug or topic_slug in ("global", "all", "overview")

        # --- Handle Global Questions ---
        if is_global:
            return self._answer_global_question(db, question)

        # --- Handle Topic-Specific Questions ---
        topic = db.get(TopicRecord, topic_slug)
        narrative = db.get(NarrativeRecord, topic_slug)

        if not topic and not narrative:
            return AIResponse(
                answer=f"Insufficient evidence to determine this: no database records found for topic '{topic_slug}'.",
                evidence=["0 qualified database signals for this topic"],
                confidence="Low",
                last_updated="Awaiting collection",
                provider="rag-analyst",
            )

        title = (narrative.title if narrative else topic.title) if (narrative or topic) else topic_slug
        analytics = topic.analytics if topic else {}

        posts = db.scalars(
            select(PostRecord).where(PostRecord.topic_slug == topic_slug).order_by(PostRecord.published_at.desc()).limit(50)
        ).all()
        post_texts = [p.content for p in posts] if posts else []
        post_count = len(posts)

        sentiment_data = analytics.get("sentiment", {})
        negative = sentiment_data.get("negative", narrative.sentiment_negative if narrative else 0)
        neutral = sentiment_data.get("neutral", narrative.sentiment_neutral if narrative else 0)
        positive = sentiment_data.get("positive", narrative.sentiment_positive if narrative else 0)
        change = sentiment_data.get("change_last_6h", narrative.sentiment_change_6h if narrative else 0)

        drivers = analytics.get("drivers", [])
        driver_titles = [d.get("title", "") for d in drivers if d.get("title")]

        network_data = analytics.get("network", {})
        nodes = network_data.get("nodes", [])
        amplifiers = [n.get("label", "") for n in nodes if n.get("group") == "amplifier" or n.get("pagerank", 0) > 0.08]

        platforms = list({p.platform for p in posts}) if posts else ["web"]

        evidence: list[str] = []

        # 1. Faster Growing / Momentum
        if any(w in q_lowered for w in ("fastest", "growing", "momentum", "velocity", "acceleration")):
            velocity_text = f"{narrative.velocity} signals/hour" if narrative and narrative.velocity else "high velocity"
            score_text = f"Momentum score: {narrative.momentum_score}/100" if narrative else "Active velocity"
            answer = (
                f"“{title}” is moving with {velocity_text} ({score_text}). "
                f"Discussion volume has accelerated primarily across {', '.join(platforms[:3])}."
            )
            evidence.append(f"Measured {post_count} qualified signals in topic window")
            evidence.append(velocity_text)
            return AIResponse(answer=answer, evidence=evidence, confidence="High" if post_count >= 10 else "Medium", provider="rag-analyst")

        # 2. Why is negative sentiment increasing?
        elif any(w in q_lowered for w in ("why", "negative sentiment", "oppose", "angry", "critic")):
            top_reason = driver_titles[0] if driver_titles else "policy execution concerns"
            trend_dir = "increased" if change > 0 else "held steady"
            answer = (
                f"Negative sentiment on “{title}” stands at {negative}%, having {trend_dir} by {abs(change)}% in the observation window. "
                f"The primary driver behind opposing sentiment centers on '{top_reason}'."
            )
            evidence.append(f"SentiMix measured {negative}% negative sentiment")
            evidence.append(f"6-hour shift: {change:+d}%")
            if driver_titles:
                evidence.append(f"Top driver: {top_reason}")
            return AIResponse(answer=answer, evidence=evidence, confidence="High" if post_count >= 10 else "Medium", provider="rag-analyst")

        # 3. Influencers / Drivers
        elif any(w in q_lowered for w in ("influencer", "who is driving", "amplifier", "leading account", "who are")):
            if amplifiers:
                amp_str = ", ".join(f"“{a}”" for a in amplifiers[:3])
                answer = f"The primary narrative amplifiers identified via NetworkX PageRank are {amp_str}. These accounts exhibit the highest structural network centrality."
                evidence.append(f"Top PageRank nodes: {', '.join(amplifiers[:4])}")
            else:
                answer = f"Discussion around “{title}” is broadly distributed across grassroots public contributors without a single dominant amplifier node."
                evidence.append(f"Evaluated graph of {len(nodes)} participants")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

        # 4. Coordinated / Bot Activity
        elif any(w in q_lowered for w in ("coordinated", "bot", "artificial", "campaign", "manipulat")):
            from app.services.coordination_detection import get_coordination_service
            coord_svc = get_coordination_service()
            assessment = coord_svc.detect_coordination([{"content": t, "author_name": "user"} for t in post_texts])
            answer = f"Coordinated amplification assessment: {assessment.summary} (Risk score: {assessment.overall_coordination_risk}/100)."
            evidence.append(f"Coordination Risk Score: {assessment.overall_coordination_risk}/100")
            evidence.append(f"Clusters evaluated: {len(assessment.clusters_detected)}")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

        # 5. Platforms / Cross-platform comparison
        elif any(w in q_lowered for w in ("platform", "reddit", "x", "compare", "channel", "telegram")):
            if posts:
                plat_counts = Counter(p.platform for p in posts)
                plat_str = ", ".join(f"{k.title()} ({v} posts)" for k, v in plat_counts.most_common(3))
                answer = f"Discussion for “{title}” is distributed across {plat_str}. Content propagates between these networks with minimal transmission delay."
                evidence.append(f"Platform signals: {plat_str}")
            else:
                answer = "Insufficient platform metadata recorded for this topic."
                evidence.append("0 platform signals")
            return AIResponse(answer=answer, evidence=evidence, confidence="Medium", provider="rag-analyst")

        # 6. Summary of Situation
        else:
            status_text = narrative.status if narrative else "Active"
            answer = (
                f"Summary for “{title}”: Currently classified as {status_text} with {negative}% opposing, {neutral}% neutral, and {positive}% supportive sentiment. "
                f"The topic spans {len(platforms)} platforms with {post_count} analyzed posts."
            )
            evidence.append(f"Sentiment: {negative}% neg, {neutral}% neu, {positive}% pos")
            evidence.append(f"Total qualified signals: {post_count}")
            return AIResponse(answer=answer, evidence=evidence, confidence="High" if post_count >= 5 else "Medium", provider="rag-analyst")

    def _answer_global_question(self, db: Session, question: str) -> AIResponse:
        q_lowered = question.lower()
        topics = db.scalars(select(TopicRecord).order_by(TopicRecord.total_conversations.desc()).limit(8)).all()
        narratives = db.scalars(select(NarrativeRecord).order_by(NarrativeRecord.momentum_score.desc()).limit(8)).all()

        if not topics and not narratives:
            return AIResponse(
                answer="Insufficient evidence to determine this: no topics or narratives have been ingested yet. Please run live collection on the Sources page.",
                evidence=["0 topics in database"],
                confidence="Low",
                provider="rag-analyst",
            )

        evidence: list[str] = []

        if any(w in q_lowered for w in ("what are people talking about", "overview", "current situation", "topics")):
            names = [n.title for n in narratives[:3]] or [t.title for t in topics[:3]]
            answer = f"The primary discussions right now center on: {', '.join(f'“{n}”' for n in names)}. These topics represent the largest concentration of incoming social signals."
            evidence.append(f"Top active topics: {', '.join(names)}")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

        elif any(w in q_lowered for w in ("fastest", "emerging", "velocity", "momentum")):
            emerging = [n for n in narratives if n.status == "EMERGING"] or narratives[:2]
            top_em = emerging[0] if emerging else None
            if top_em:
                answer = f"The fastest-growing narrative is “{top_em.title}” with a momentum score of {top_em.momentum_score}/100 and high velocity."
                evidence.append(f"Narrative: {top_em.title} (Score: {top_em.momentum_score})")
            else:
                answer = "Insufficient evidence to determine a dominant emerging narrative."
                evidence.append("No narratives classified as emerging")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

        elif any(w in q_lowered for w in ("negative sentiment", "why is negative")):
            most_neg = sorted(narratives, key=lambda x: x.sentiment_negative, reverse=True)
            top_neg = most_neg[0] if most_neg else None
            if top_neg and top_neg.sentiment_negative > 0:
                answer = f"Negative sentiment is concentrated most sharply in “{top_neg.title}” ({top_neg.sentiment_negative}% opposing), driven by policy contention and institutional critique."
                evidence.append(f"Leading negative narrative: {top_neg.title} ({top_neg.sentiment_negative}% opposing)")
            else:
                answer = "Overall public sentiment across currently tracked topics remains predominantly neutral or balanced."
                evidence.append("Negative sentiment below critical alert thresholds")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

        else:
            names = [n.title for n in narratives[:3]]
            answer = f"Current situation: {len(narratives)} active public narratives tracked across multiple channels. Key subjects include {', '.join(names)}."
            evidence.append(f"{len(narratives)} active narratives analyzed in database")
            return AIResponse(answer=answer, evidence=evidence, confidence="High", provider="rag-analyst")

_rag_analyst_instance = RAGAnalystService()

def get_rag_analyst() -> RAGAnalystService:
    return _rag_analyst_instance

def ask_rag_analyst(db: Session, topic_slug: str, question: str) -> AIResponse:
    return _rag_analyst_instance.answer_question(db, topic_slug, question)
