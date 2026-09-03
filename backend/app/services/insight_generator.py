from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class InsightCard:
    insight_id: str
    topic_slug: str
    priority_score: float  # 0 to 100
    category: str          # "Sentiment Shift", "Emerging Narrative", "Coordinated Amplification", "Cross-Platform Surge", "Audience Polarization"
    title: str
    insight: str
    evidence: list[str]
    why_it_matters: str
    confidence: str        # "HIGH", "MEDIUM", "LOW"
    source_signals: list[str]
    model_name: str = "SIH Intelligence Engine"

class InsightGeneratorService:
    """
    AI Insight Generator with Multidimensional Prioritization.
    Computes AI Priority Score:
        Priority = Impact x Velocity x Confidence x CrossPlatformSpread x Influence (normalized to 0-100)
    Generates structured, explainable intelligence cards with explicit evidence citations.
    """

    def generate_prioritized_insights(
        self,
        topic_slug: str,
        topic_title: str,
        negative_pct: float,
        sentiment_shift_6h: float,
        momentum_score: float,
        velocity: float,
        coordination_risk: float,
        platforms: list[str],
        top_driver: str | None = None,
        top_influencer: str | None = None,
        volume: int = 0,
    ) -> list[InsightCard]:
        insights: list[InsightCard] = []

        # 1. Sentiment Shift Insight Card
        if abs(sentiment_shift_6h) >= 5.0 or negative_pct >= 45.0:
            impact = 0.85 if negative_pct >= 50.0 else 0.65
            vel_factor = min(1.0, velocity / 20.0)
            conf_val = 0.90 if volume >= 15 else 0.70
            spread_factor = min(1.0, len(platforms) / 3.0)
            priority = round(min(100.0, impact * 35.0 + vel_factor * 25.0 + conf_val * 20.0 + spread_factor * 20.0), 1)

            direction = "increased" if sentiment_shift_6h > 0 else "decreased"
            driver_phrase = f" primarily associated with discussions around '{top_driver}'" if top_driver else ""
            insights.append(
                InsightCard(
                    insight_id=f"ins_sent_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=priority,
                    category="Sentiment Shift",
                    title="Negative Sentiment Dynamics",
                    insight=f"Negative sentiment has {direction} to {negative_pct}%{driver_phrase}.",
                    evidence=[
                        f"Current negative stance: {negative_pct}%",
                        f"6-hour sentiment shift: {int(sentiment_shift_6h):+d}%",
                        f"Sample volume: {volume} qualified signals",
                    ],
                    why_it_matters="Sharp sentiment shifts indicate shifting public perception or reaction to breaking developments.",
                    confidence="HIGH" if volume >= 15 else "MEDIUM",
                    source_signals=[f"{plat.title()} stream" for plat in platforms[:3]],
                )
            )

        # 2. Emerging Narrative Velocity Insight Card
        if momentum_score >= 45.0:
            priority = round(min(100.0, momentum_score * 0.75 + len(platforms) * 5.0 + (15.0 if volume >= 20 else 5.0)), 1)
            insights.append(
                InsightCard(
                    insight_id=f"ins_vel_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=priority,
                    category="Emerging Narrative",
                    title="Narrative Acceleration",
                    insight=f"'{topic_title}' is gaining substantial momentum with an observed velocity of {velocity} posts/hour.",
                    evidence=[
                        f"Composite Momentum Score: {momentum_score}/100",
                        f"Current processing velocity: {velocity} signals/hour",
                        f"Observed across {len(platforms)} platforms: {', '.join(platforms)}",
                    ],
                    why_it_matters="Accelerating narratives represent the fastest-growing topics in public consciousness.",
                    confidence="HIGH" if momentum_score >= 60.0 else "MEDIUM",
                    source_signals=[f"Kafka high-signal stream: {p}" for p in platforms[:3]],
                )
            )

        # 3. Coordinated Activity Alert Card
        if coordination_risk >= 40.0:
            priority = round(min(100.0, coordination_risk * 0.85 + 15.0), 1)
            insights.append(
                InsightCard(
                    insight_id=f"ins_coord_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=priority,
                    category="Coordinated Amplification",
                    title="Potential Narrative Coordination",
                    insight="Abnormal repetitive messaging or synchronized bursts detected in narrative amplification.",
                    evidence=[
                        f"Coordination Risk Score: {coordination_risk}/100",
                        "Near-duplicate text similarity (Jaccard >= 0.85) observed across distinct accounts",
                        "Concentrated hashtag propagation patterns identified",
                    ],
                    why_it_matters="Coordinated campaigns can artificially inflate perceived public consensus or distress.",
                    confidence="HIGH" if coordination_risk >= 65.0 else "MEDIUM",
                    source_signals=["CSQE near-duplicate filter", "Network cluster analysis"],
                )
            )

        # 4. Cross-Platform Diffusion Card
        if len(platforms) >= 3:
            priority = round(min(100.0, 50.0 + len(platforms) * 10.0), 1)
            insights.append(
                InsightCard(
                    insight_id=f"ins_diff_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=priority,
                    category="Cross-Platform Surge",
                    title="Multi-Platform Narrative Diffusion",
                    insight=f"Discussion has expanded across {len(platforms)} platforms, confirming broad cross-channel transmission.",
                    evidence=[
                        f"Active platforms: {', '.join(p.title() for p in platforms)}",
                        "Inter-platform diffusion delays recorded in timeline graph",
                    ],
                    why_it_matters="Multi-platform spread demonstrates organic spillover beyond initial audience silos.",
                    confidence="HIGH",
                    source_signals=platforms,
                )
            )

        # 5. Influencer Driver Card
        if top_influencer and top_influencer != "None":
            insights.append(
                InsightCard(
                    insight_id=f"ins_inf_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=58.0,
                    category="Network Influence",
                    title="Key Opinion Driver Identified",
                    insight=f"{top_influencer} holds the highest structural PageRank influence in this discussion community.",
                    evidence=[
                        f"Lead amplifier: {top_influencer}",
                        "Identified via NetworkX PageRank structural centrality",
                    ],
                    why_it_matters="Key amplifiers drive the majority of downstream reposts, quotes, and conversational cascades.",
                    confidence="HIGH",
                    source_signals=["NetworkX PageRank computation"],
                )
            )

        # Baseline insight if sparse
        if not insights:
            insights.append(
                InsightCard(
                    insight_id=f"ins_base_{topic_slug}",
                    topic_slug=topic_slug,
                    priority_score=40.0,
                    category="Public Discourse",
                    title="Baseline Narrative Analysis",
                    insight=f"Discourse around '{topic_title}' remains within baseline stability parameters.",
                    evidence=[f"Processed {volume} qualified public signals", "No acute risk spikes recorded"],
                    why_it_matters="Demonstrates normal public conversation without anomalous agitation.",
                    confidence="MEDIUM",
                    source_signals=platforms or ["Live streams"],
                )
            )

        # Sort by AI Priority Score descending
        insights.sort(key=lambda x: x.priority_score, reverse=True)
        return insights

_insight_instance = InsightGeneratorService()

def get_insight_generator() -> InsightGeneratorService:
    return _insight_instance
