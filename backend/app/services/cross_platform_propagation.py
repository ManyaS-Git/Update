from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class PlatformStep:
    platform: str
    first_seen: str
    delay_minutes: int
    volume: int
    engagement: int

@dataclass
class PropagationTimeline:
    origin_platform: str | None
    origin_timestamp: str | None
    path_summary: str
    platforms_involved: list[str]
    steps: list[PlatformStep]
    has_sufficient_timeline_evidence: bool

class CrossPlatformPropagationService:
    """
    Cross-Platform Narrative Propagation Engine.
    Traces the chronological diffusion of public narratives across X, Reddit, Telegram,
    YouTube, Facebook, and Instagram, calculating inter-platform propagation delays.
    """

    def analyze_propagation(self, posts: list[dict]) -> PropagationTimeline:
        if not posts:
            return PropagationTimeline(
                origin_platform=None,
                origin_timestamp=None,
                path_summary="Insufficient multi-platform timeline data to establish propagation sequence.",
                platforms_involved=[],
                steps=[],
                has_sufficient_timeline_evidence=False,
            )

        platform_records = defaultdict(list)
        for p in posts:
            plat = p.get("platform", "web").lower()
            ts = p.get("published_at")
            eng = (p.get("likes", 0) or 0) + (p.get("shares", 0) or 0) + (p.get("comments", 0) or 0)
            platform_records[plat].append({
                "timestamp": ts,
                "engagement": eng,
            })

        # Calculate earliest timestamp per platform
        platform_summary = []
        for plat, recs in platform_records.items():
            valid_ts = [r["timestamp"] for r in recs if isinstance(r["timestamp"], datetime)]
            earliest = min(valid_ts) if valid_ts else None
            total_eng = sum(r["engagement"] for r in recs)
            platform_summary.append({
                "platform": plat,
                "earliest": earliest,
                "volume": len(recs),
                "engagement": total_eng,
            })

        # Filter platforms with valid timestamp evidence
        with_ts = [p for p in platform_summary if p["earliest"] is not None]
        with_ts.sort(key=lambda x: x["earliest"])

        if len(with_ts) < 2:
            single_plat = with_ts[0]["platform"] if with_ts else (posts[0].get("platform") or "web")
            return PropagationTimeline(
                origin_platform=single_plat,
                origin_timestamp=with_ts[0]["earliest"].isoformat() if with_ts else None,
                path_summary=f"Activity currently concentrated on {single_plat.title()}; broader cross-platform diffusion not yet recorded.",
                platforms_involved=list(platform_records.keys()),
                steps=[
                    PlatformStep(
                        platform=p["platform"],
                        first_seen=p["earliest"].isoformat() if p["earliest"] else "Awaiting timestamp",
                        delay_minutes=0,
                        volume=p["volume"],
                        engagement=p["engagement"],
                    )
                    for p in platform_summary
                ],
                has_sufficient_timeline_evidence=False,
            )

        origin = with_ts[0]
        origin_time: datetime = origin["earliest"]

        steps = []
        path_tokens = []

        for p in with_ts:
            delay = max(0, int((p["earliest"] - origin_time).total_seconds() / 60))
            steps.append(
                PlatformStep(
                    platform=p["platform"],
                    first_seen=p["earliest"].strftime("%H:%M UTC"),
                    delay_minutes=delay,
                    volume=p["volume"],
                    engagement=p["engagement"],
                )
            )
            if delay == 0:
                path_tokens.append(f"{p['platform'].title()} ({p['earliest'].strftime('%H:%M')})")
            else:
                path_tokens.append(f"{p['platform'].title()} (+{delay}m)")

        path_summary = f"Narrative first emerged on {origin['platform'].title()}, subsequently diffusing to: {' → '.join(path_tokens[1:])}."

        return PropagationTimeline(
            origin_platform=origin["platform"],
            origin_timestamp=origin["earliest"].isoformat(),
            path_summary=path_summary,
            platforms_involved=[p["platform"] for p in with_ts],
            steps=steps,
            has_sufficient_timeline_evidence=True,
        )

_propagation_instance = CrossPlatformPropagationService()

def get_propagation_service() -> CrossPlatformPropagationService:
    return _propagation_instance
