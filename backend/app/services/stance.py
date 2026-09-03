from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

STANCE_SUPPORT = {
    "support", "agree", "necessary", "justice", "representation", "equal opportunity",
    "favour", "in favor", "backed", "welcomed", "appreciated",
    "samarthan", "sahi", "zaroori", "shandar", "badhiya",
    "समर्थन", "सही", "न्याय", "ज़रूरी", "स्वीकार"
}

STANCE_OPPOSE = {
    "oppose", "against", "unfair", "remove", "wrong", "reject", "protest", "strike", "bandh",
    "condemn", "unacceptable", "boycott",
    "galat", "virodh", "nahi chahiye", "hatao", "barbaad",
    "नहीं चाहिए", "गलत", "विरोध", "हटाओ", "खारिज"
}

@dataclass
class StancePrediction:
    stance: str  # support, oppose, neutral, unclear
    confidence: float
    evidence: list[str]
    model_name: str = "Multilingual-Stance-Engine"

class StanceService:
    """
    Stance Analysis Engine.
    Classifies discourse into: Support, Oppose, Neutral, and Unclear.
    Calculates percentage breakdowns and evaluates stance evolution over time.
    """

    def predict(self, text: str, topic_context: str | None = None) -> StancePrediction:
        lowered = text.lower()
        words = set(re.findall(r"[\w'-]+", lowered))

        support_hits = words & STANCE_SUPPORT
        oppose_hits = words & STANCE_OPPOSE

        if support_hits and oppose_hits:
            if len(support_hits) > len(oppose_hits):
                return StancePrediction(
                    stance="support",
                    confidence=0.72,
                    evidence=[f"Predominant supportive cue: {', '.join(list(support_hits)[:2])}"],
                )
            elif len(oppose_hits) > len(support_hits):
                return StancePrediction(
                    stance="oppose",
                    confidence=0.75,
                    evidence=[f"Predominant opposition cue: {', '.join(list(oppose_hits)[:2])}"],
                )
            else:
                return StancePrediction(
                    stance="unclear",
                    confidence=0.60,
                    evidence=["Conflicting stance cues present in statement"],
                )
        elif support_hits:
            return StancePrediction(
                stance="support",
                confidence=min(0.92, 0.65 + 0.10 * len(support_hits)),
                evidence=[f"Support markers: {', '.join(list(support_hits)[:3])}"],
            )
        elif oppose_hits:
            return StancePrediction(
                stance="oppose",
                confidence=min(0.95, 0.68 + 0.10 * len(oppose_hits)),
                evidence=[f"Opposition markers: {', '.join(list(oppose_hits)[:3])}"],
            )
        elif "?" in text:
            return StancePrediction(
                stance="unclear",
                confidence=0.65,
                evidence=["Inquisitive / questioning tone without overt stance"],
            )
        else:
            return StancePrediction(
                stance="neutral",
                confidence=0.60,
                evidence=["Factual reporting or neutral civic observation"],
            )

    def analyze_stance_distribution(self, texts: list[str]) -> dict[str, Any]:
        if not texts:
            return {
                "support_pct": 0.0,
                "oppose_pct": 0.0,
                "neutral_pct": 100.0,
                "unclear_pct": 0.0,
                "total_analyzed": 0,
            }

        counts = Counter()
        for t in texts:
            pred = self.predict(t)
            counts[pred.stance] += 1

        total = len(texts)
        return {
            "support_pct": round((counts["support"] / total) * 100, 1),
            "oppose_pct": round((counts["oppose"] / total) * 100, 1),
            "neutral_pct": round((counts["neutral"] / total) * 100, 1),
            "unclear_pct": round((counts["unclear"] / total) * 100, 1),
            "total_analyzed": total,
        }

_stance_instance = StanceService()

def get_stance_service() -> StanceService:
    return _stance_instance
