from __future__ import annotations
from collections import Counter
import re
from typing import Any

class AudienceIntelligenceService:
    """
    Produces audience intelligence strictly respecting data ethics:
    - Never fabricates demographics.
    - Explicitly distinguishes Observed data from Model-based inferences.
    - Reports confidence levels or declares unavailable when signals are absent.
    """
    INDIAN_CITIES = {
        "delhi": "Delhi NCR, India", "new delhi": "Delhi NCR, India", "noida": "Delhi NCR, India",
        "mumbai": "Mumbai, Maharashtra", "pune": "Pune, Maharashtra", "nagpur": "Maharashtra, India",
        "bengaluru": "Bengaluru, Karnataka", "bangalore": "Bengaluru, Karnataka",
        "hyderabad": "Hyderabad, Telangana", "chennai": "Chennai, Tamil Nadu",
        "kolkata": "Kolkata, West Bengal", "ahmedabad": "Ahmedabad, Gujarat",
        "jaipur": "Jaipur, Rajasthan", "lucknow": "Lucknow, Uttar Pradesh",
        "patna": "Patna, Bihar", "chandigarh": "Chandigarh, Punjab/Haryana",
        "bhopal": "Bhopal, Madhya Pradesh", "indore": "Indore, Madhya Pradesh",
        "kochi": "Kochi, Kerala", "guwahati": "Guwahati, Assam"
    }

    COMMUNITY_AGE_MAP = {
        "student": ("18–24 years", "Medium"),
        "college": ("18–24 years", "Medium"),
        "university": ("18–24 years", "Medium"),
        "campus": ("18–24 years", "Medium"),
        "aspirant": ("18–24 years", "Medium"),
        "exam": ("18–24 years", "Medium"),
        "job": ("22–30 years", "Low"),
        "career": ("22–30 years", "Low"),
        "parent": ("35–50 years", "Low"),
        "tax": ("28–45 years", "Low"),
        "pension": ("50+ years", "Low"),
    }

    def analyze_audience(self, posts: list[dict]) -> dict[str, Any]:
        if not posts:
            return {
                "geography": {"value": "Not available from public metadata", "confidence": "Unavailable", "is_observed": False},
                "language": {"distribution": {}},
                "age_bracket": {"value": "Not available from public source metadata", "confidence": "Unavailable", "is_observed": False},
                "interest_groups": [],
                "key_topics": [],
                "leading_platform": "Awaiting source collection",
            }

        total = len(posts)

        # 1. Geography (Observed from author locations, geotags, text mentions)
        observed_locations = Counter()
        for p in posts:
            loc = (p.get("public_signals") or {}).get("location") or (p.get("metadata") or {}).get("location") or ""
            if loc:
                observed_locations[loc.title()] += 1
            else:
                # Scan text for explicit city mentions
                lowered = p.get("text", "").lower()
                for city_term, norm_loc in self.INDIAN_CITIES.items():
                    if re.search(rf"\b{city_term}\b", lowered):
                        observed_locations[norm_loc] += 1
                        break

        if observed_locations:
            top_loc, loc_count = observed_locations.most_common(1)[0]
            confidence = "High" if loc_count >= 5 else "Medium"
            geography_data = {
                "value": top_loc,
                "confidence": confidence,
                "is_observed": True,
                "coverage_pct": round(100 * sum(observed_locations.values()) / total),
            }
        else:
            geography_data = {
                "value": "Not available from public metadata",
                "confidence": "Unavailable",
                "is_observed": False,
            }

        # 2. Language distribution (Observed from script analysis)
        lang_counts = Counter()
        for p in posts:
            text = p.get("text", "")
            if any("\u0900" <= c <= "\u097f" for c in text):
                lang_counts["Hindi"] += 1
            elif any(w in text.lower().split() for w in ("hai", "nahi", "kya", "sahi", "yaar")):
                lang_counts["Hinglish"] += 1
            elif any(c.isascii() for c in text):
                lang_counts["English"] += 1
            else:
                lang_counts["Other"] += 1

        lang_dist = {k: round(100 * v / total) for k, v in lang_counts.most_common()}
        if lang_dist:
            diff = 100 - sum(lang_dist.values())
            leader = max(lang_dist, key=lang_dist.get)
            lang_dist[leader] += diff

        # 3. Age Bracket (Model-based inference from community markers, NEVER fabricated)
        age_evidence = Counter()
        for p in posts:
            lowered = p.get("text", "").lower()
            for cue, (bracket, conf) in self.COMMUNITY_AGE_MAP.items():
                if cue in lowered:
                    age_evidence[bracket] += 1
                    break

        if age_evidence:
            top_age, count = age_evidence.most_common(1)[0]
            age_data = {
                "value": top_age,
                "confidence": "Medium" if count >= 4 else "Low",
                "is_observed": False,
                "method": "Inferred from community discussion themes",
            }
        else:
            age_data = {
                "value": "Not available from public source metadata",
                "confidence": "Unavailable",
                "is_observed": False,
                "method": "No reliable age indicators in public text",
            }

        # 4. Interest groups and Key topics
        words = []
        for p in posts:
            words.extend(re.findall(r"[A-Za-z]{4,}", p.get("text", "").lower()))
        common_words = [w for w, _ in Counter(words).most_common(20)]
        stop_words = {"this", "that", "with", "from", "they", "have", "been", "were", "what", "more", "will", "about"}
        filtered_interests = [w.title() for w in common_words if w not in stop_words][:5]

        # 5. Leading platform
        platform_counts = Counter(p.get("platform", "unknown") for p in posts)
        top_platform = platform_counts.most_common(1)[0][0].title() if platform_counts else "Multiple sources"

        return {
            "geography": geography_data,
            "language": {"distribution": lang_dist},
            "age_bracket": age_data,
            "interest_groups": filtered_interests[:3] or ["General Public Discussion"],
            "key_topics": filtered_interests or ["Public Interest"],
            "leading_platform": f"{top_platform} leads discussion",
        }
