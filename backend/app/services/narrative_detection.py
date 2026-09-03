from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import math
from typing import Any
from app.models.schemas import EmergingNarrative
from app.services.topic_modeling import DynamicTopic

class NarrativeDetector:
    """
    Distinguishes Emerging Narratives from Already Popular Trends by analyzing:
    - Growth Rate (dV / V_prev)
    - Mention Velocity (posts/hr acceleration)
    - Cross-Platform Activity (Shannon Entropy across platforms)
    - Topic Momentum (acceleration over time windows)
    - Novelty Score (recent appearance)
    - Network Propagation & Amplification ratio (replies & shares vs likes)
    """

    def analyze_narratives(
        self,
        topics: list[DynamicTopic],
        posts_by_topic: dict[str, list[dict]],
    ) -> list[EmergingNarrative]:
        narratives: list[EmergingNarrative] = []
        now = datetime.now(timezone.utc)

        for topic in topics:
            topic_posts = posts_by_topic.get(topic.topic_id, [])
            if not topic_posts:
                continue

            total_volume = len(topic_posts)

            # 1. Temporal breakdown: last 6h vs 6-18h ago
            six_hours_ago = now.timestamp() - 6 * 3600
            eighteen_hours_ago = now.timestamp() - 18 * 3600

            v_recent = sum(1 for p in topic_posts if p.get("timestamp", now).timestamp() >= six_hours_ago)
            v_older = sum(1 for p in topic_posts if eighteen_hours_ago <= p.get("timestamp", now).timestamp() < six_hours_ago)

            growth_rate = (v_recent - v_older) / max(1.0, float(v_older))
            velocity = v_recent / 6.0  # posts per hour in recent window

            # 2. Topic Momentum (acceleration)
            momentum = max(-1.0, min(2.0, (v_recent - v_older) / max(1.0, total_volume / 2.0)))

            # 3. Cross-Platform Activity Score (Normalized Shannon Entropy)
            platforms = [p.get("platform", "web") for p in topic_posts]
            platform_counts = Counter(platforms)
            num_platforms = len(platform_counts)

            if num_platforms > 1:
                entropy = -sum((c / total_volume) * math.log(c / total_volume) for c in platform_counts.values())
                max_entropy = math.log(max(2, num_platforms))
                cross_platform_score = round(min(1.0, entropy / max_entropy), 3)
            else:
                cross_platform_score = 0.15

            # 4. Novelty Score (proportion of posts in the recent 12 hours)
            twelve_hours_ago = now.timestamp() - 12 * 3600
            recent_count = sum(1 for p in topic_posts if p.get("timestamp", now).timestamp() >= twelve_hours_ago)
            novelty = round(recent_count / max(1.0, total_volume), 3)

            # 5. Network Amplification Ratio (shares & replies vs likes)
            total_likes = sum(p.get("likes", 0) for p in topic_posts)
            total_amplification = sum(p.get("shares", 0) + p.get("comments", 0) for p in topic_posts)
            amplification_ratio = min(1.0, total_amplification / max(1.0, total_likes))

            # 6. Combined Emerging Metric
            # Distinguishes genuine emerging breakout from established popular trends
            emerging_metric = (
                0.35 * max(0.0, momentum) +
                0.25 * cross_platform_score +
                0.25 * novelty +
                0.15 * amplification_ratio
            )

            # Classification:
            # - POPULAR_TREND: high volume, low momentum/growth (already saturated)
            # - EMERGING: high momentum, high cross-platform spread, high novelty
            # - DECLINING: negative growth
            # - STABLE: moderate steady volume
            if total_volume >= 200 and emerging_metric < 0.40 and growth_rate <= 0.10:
                status = "POPULAR_TREND"
                is_emerging = False
            elif emerging_metric >= 0.45 or (growth_rate > 0.30 and novelty > 0.60):
                status = "EMERGING"
                is_emerging = True
            elif growth_rate < -0.15:
                status = "DECLINING"
                is_emerging = False
            else:
                status = "STABLE"
                is_emerging = False

            # Calculate sentiment distribution for this topic
            sentiments = [p.get("sentiment", "neutral") for p in topic_posts]
            sent_counts = Counter(sentiments)
            total_sent = max(1, len(sentiments))
            sent_dist = {
                "negative": round(100 * sent_counts.get("negative", 0) / total_sent),
                "neutral": round(100 * sent_counts.get("neutral", 0) / total_sent),
                "positive": round(100 * sent_counts.get("positive", 0) / total_sent),
            }
            # Adjust rounding to 100
            diff = 100 - sum(sent_dist.values())
            sent_dist["neutral"] += diff

            narratives.append(
                EmergingNarrative(
                    slug=topic.name.lower().replace(" ", "-")[:80],
                    title=topic.name,
                    category="India" if any(k in topic.name.lower() for k in ("delhi", "protest", "court", "policy", "india")) else "Analysis",
                    status=status,
                    is_emerging=is_emerging,
                    momentum_score=round(emerging_metric, 3),
                    velocity=round(velocity, 2),
                    growth_rate=round(growth_rate, 3),
                    cross_platform_score=cross_platform_score,
                    total_conversations=total_volume,
                    sentiment=sent_dist,
                    topics=topic.keywords,
                    updated="Just now",
                )
            )

        # Sort so that emerging narratives and high momentum rank first
        narratives.sort(key=lambda n: (n.is_emerging, n.momentum_score, n.total_conversations), reverse=True)
        return narratives

_detector = NarrativeDetector()

def detect_narratives(topics: list[DynamicTopic], posts_by_topic: dict[str, list[dict]]) -> list[EmergingNarrative]:
    return _detector.analyze_narratives(topics, posts_by_topic)
