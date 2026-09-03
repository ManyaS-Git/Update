from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class RiskEvent:
    risk_id: str
    topic_slug: str
    title: str
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float  # 0 to 100
    reason: str
    evidence: list[str]
    affected_platforms: list[str]
    trend_direction: str  # accelerating, escalating, steady, declining
    recommended_attention: str

class RiskMonitorService:
    """
    AI Risk Monitor Engine.
    Continuously evaluates multi-vector threat indicators:
    sentiment shifts, narrative velocity, coordination risk, and cross-platform spillover.
    """

    def evaluate_risk(
        self,
        topic_slug: str,
        topic_title: str,
        negative_sentiment_pct: float,
        sentiment_shift_6h: float,
        momentum_score: float,
        coordination_risk: float,
        platforms: list[str] | None = None,
        volume: int = 0,
    ) -> RiskEvent:
        platforms = platforms or ["web"]
        evidence: list[str] = []
        score = 0.0

        # 1. Negative Sentiment Vector
        if negative_sentiment_pct >= 60.0:
            score += 35.0
            evidence.append(f"Dominant opposing public reaction ({negative_sentiment_pct}% negative)")
        elif negative_sentiment_pct >= 40.0:
            score += 20.0
            evidence.append(f"Elevated negative reaction ({negative_sentiment_pct}% negative)")

        # 2. Sudden Sentiment Acceleration Shift
        if sentiment_shift_6h >= 15.0:
            score += 25.0
            evidence.append(f"Rapid negative sentiment surge (+{sentiment_shift_6h}% in last 6h)")
        elif sentiment_shift_6h >= 8.0:
            score += 15.0
            evidence.append(f"Upward trending negative sentiment (+{sentiment_shift_6h}% in last 6h)")

        # 3. Narrative Momentum & Velocity Vector
        if momentum_score >= 75.0:
            score += 25.0
            evidence.append(f"High narrative momentum score: {momentum_score}/100")
        elif momentum_score >= 50.0:
            score += 15.0
            evidence.append(f"Substantial momentum: {momentum_score}/100")

        # 4. Coordinated Amplification Vector
        if coordination_risk >= 65.0:
            score += 25.0
            evidence.append(f"Severe coordinated amplification detected (risk {coordination_risk}/100)")
        elif coordination_risk >= 40.0:
            score += 15.0
            evidence.append(f"Elevated repetitive burst activity (risk {coordination_risk}/100)")

        # 5. Cross-Platform Spillover Vector
        if len(platforms) >= 3:
            score += 10.0
            evidence.append(f"Active cross-platform diffusion across {len(platforms)} networks ({', '.join(platforms)})")

        final_score = round(min(100.0, max(5.0, score)), 1)

        # Classification
        if final_score >= 80.0:
            level = "CRITICAL"
            reason = "High-velocity negative narrative with severe multi-platform propagation and potential coordination."
            trend = "escalating"
            attention = "Immediate escalation & close response monitoring required"
        elif final_score >= 55.0:
            level = "HIGH"
            reason = "Accelerating public controversy with notable negative sentiment shift."
            trend = "accelerating"
            attention = "Proactive communications monitoring recommended"
        elif final_score >= 35.0:
            level = "MEDIUM"
            reason = "Moderate civic debate with emerging critical feedback signals."
            trend = "steady"
            attention = "Standard intelligence tracking"
        else:
            level = "LOW"
            reason = "Contained discourse with balanced sentiment and normal organic velocity."
            trend = "steady"
            attention = "Informational monitoring only"

        if not evidence:
            evidence.append("Balanced conversational metrics; no acute risk thresholds triggered.")

        return RiskEvent(
            risk_id=f"risk_{topic_slug}",
            topic_slug=topic_slug,
            title=f"Discourse Assessment for {topic_title}",
            level=level,
            risk_score=final_score,
            reason=reason,
            evidence=evidence,
            affected_platforms=platforms,
            trend_direction=trend,
            recommended_attention=attention,
        )

_risk_instance = RiskMonitorService()

def get_risk_monitor() -> RiskMonitorService:
    return _risk_instance
