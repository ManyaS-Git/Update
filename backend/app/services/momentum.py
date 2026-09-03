from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class MomentumBreakdown:
    momentum_score: float  # 0 to 100
    tier: str              # Low, Moderate, High, Critical
    status: str            # EMERGING, POPULAR, DECLINING, STABLE
    velocity: float        # Posts per hour
    volume_acceleration: float
    engagement_acceleration: float
    unique_user_growth: float
    cross_platform_score: float
    sentiment_change_rate: float
    geographic_expansion: float
    components: dict[str, float]

class NarrativeMomentumService:
    """
    Narrative Momentum & Velocity Engine.
    Computes a multi-factor composite Momentum Score (0-100) and classifies narrative progression
    into EMERGING, POPULAR, DECLINING, or STABLE.
    """

    def calculate_momentum(
        self,
        current_volume: int,
        previous_volume: int = 0,
        current_engagement: int = 0,
        previous_engagement: int = 0,
        unique_users: int = 1,
        total_users_prev: int = 1,
        platforms: list[str] | None = None,
        sentiment_shift_abs: float = 0.0,
        geo_hotspots_count: int = 1,
        time_window_hours: float = 1.0,
    ) -> MomentumBreakdown:
        platforms = platforms or ["web"]

        # 1. Volume Acceleration (0 - 100 scale)
        if previous_volume > 0:
            vol_growth = (current_volume - previous_volume) / previous_volume
            vol_accel = min(100.0, max(0.0, vol_growth * 50.0))
        else:
            vol_accel = min(100.0, current_volume * 4.0)

        # 2. Engagement Acceleration (0 - 100 scale)
        if previous_engagement > 0:
            eng_growth = (current_engagement - previous_engagement) / previous_engagement
            eng_accel = min(100.0, max(0.0, eng_growth * 50.0))
        else:
            eng_accel = min(100.0, current_engagement * 2.0)

        # 3. Unique User Growth (0 - 100 scale)
        user_ratio = unique_users / max(1, total_users_prev)
        user_growth = min(100.0, max(0.0, (user_ratio - 0.5) * 100.0))

        # 4. Cross-Platform Diffusion (0 - 100 scale)
        # Up to 6 platforms supported
        n_platforms = len(set(platforms))
        platform_score = min(100.0, (n_platforms / 4.0) * 100.0)

        # 5. Sentiment Volatility / Change (0 - 100 scale)
        sent_score = min(100.0, sentiment_shift_abs * 2.5)

        # 6. Geographic Expansion (0 - 100 scale)
        geo_score = min(100.0, geo_hotspots_count * 25.0)

        # Weighted Composite Momentum Score (SIH Specification)
        momentum = (
            0.25 * vol_accel +
            0.20 * eng_accel +
            0.15 * user_growth +
            0.15 * platform_score +
            0.15 * sent_score +
            0.10 * geo_score
        )
        momentum = round(min(100.0, max(0.0, momentum)), 1)

        # Tier assignment
        if momentum >= 81.0:
            tier = "Critical"
        elif momentum >= 61.0:
            tier = "High"
        elif momentum >= 31.0:
            tier = "Moderate"
        else:
            tier = "Low"

        # Classification (EMERGING when recent acceleration significantly exceeds baseline)
        velocity = round(current_volume / max(0.1, time_window_hours), 2)

        if momentum >= 60.0 and vol_accel >= 40.0:
            status = "EMERGING"
        elif current_volume >= 20 or momentum >= 50.0:
            status = "POPULAR"
        elif vol_accel < 10.0 and previous_volume > current_volume:
            status = "DECLINING"
        else:
            status = "STABLE"

        return MomentumBreakdown(
            momentum_score=momentum,
            tier=tier,
            status=status,
            velocity=velocity,
            volume_acceleration=round(vol_accel, 1),
            engagement_acceleration=round(eng_accel, 1),
            unique_user_growth=round(user_growth, 1),
            cross_platform_score=round(platform_score, 1),
            sentiment_change_rate=round(sent_score, 1),
            geographic_expansion=round(geo_score, 1),
            components={
                "volume_weight": 0.25,
                "engagement_weight": 0.20,
                "user_growth_weight": 0.15,
                "platform_spread_weight": 0.15,
                "sentiment_change_weight": 0.15,
                "geographic_spread_weight": 0.10,
            },
        )

_momentum_instance = NarrativeMomentumService()

def get_momentum_service() -> NarrativeMomentumService:
    return _momentum_instance
