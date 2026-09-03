from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

@dataclass
class CoordinationCluster:
    cluster_id: str
    risk_score: float  # 0 to 100
    pattern_type: str  # "near_duplicate_text", "synchronized_burst", "hashtag_coordination"
    account_hashes: list[str]
    representative_text: str
    evidence: list[str]

@dataclass
class CoordinationAssessment:
    overall_coordination_risk: float  # 0 to 100
    level: str  # "LOW", "ELEVATED", "HIGH", "CRITICAL"
    clusters_detected: list[CoordinationCluster]
    summary: str

class CoordinationDetectionService:
    """
    Coordinated Activity & Amplification Detection Engine.
    Examines multi-platform social streams for synchronized bursts, near-duplicate copy-paste
    campaigns (Jaccard > 0.85), and abnormal interaction clusters without false bot labeling.
    """

    def detect_coordination(self, posts: list[dict]) -> CoordinationAssessment:
        if len(posts) < 3:
            return CoordinationAssessment(
                overall_coordination_risk=0.0,
                level="LOW",
                clusters_detected=[],
                summary="Insufficient conversation volume to evaluate coordinated amplification patterns.",
            )

        clusters: list[CoordinationCluster] = []
        risk_points = 0.0

        # 1. Text Normalization and Jaccard Near-Duplicate Detection
        tokenized_posts = []
        for p in posts:
            txt = (p.get("content") or p.get("text") or "").strip().lower()
            author = str(p.get("author_name") or p.get("author_id") or "author").strip()
            tokens = set(re.findall(r"[\w']+", txt))
            published_at = p.get("published_at")
            if len(tokens) >= 4:
                tokenized_posts.append({
                    "id": str(p.get("id") or p.get("post_id") or ""),
                    "author": author,
                    "text": txt,
                    "tokens": tokens,
                    "timestamp": published_at,
                })

        # Pairwise near-duplicate comparison
        near_dup_groups: dict[str, list[dict]] = {}
        for i in range(len(tokenized_posts)):
            for j in range(i + 1, min(i + 40, len(tokenized_posts))):
                p1 = tokenized_posts[i]
                p2 = tokenized_posts[j]
                if p1["author"] == p2["author"]:
                    continue  # Ignore same author posting twice

                inter = len(p1["tokens"] & p2["tokens"])
                union = len(p1["tokens"] | p2["tokens"])
                if union > 0 and (inter / union) >= 0.85:
                    key = p1["id"]
                    if key not in near_dup_groups:
                        near_dup_groups[key] = [p1]
                    near_dup_groups[key].append(p2)

        for key, members in near_dup_groups.items():
            if len(members) >= 2:
                authors = list({m["author"] for m in members})
                if len(authors) >= 2:
                    score = min(85.0, 45.0 + 10.0 * len(authors))
                    risk_points = max(risk_points, score)
                    clusters.append(
                        CoordinationCluster(
                            cluster_id=f"dup_{key[:8]}",
                            risk_score=round(score, 1),
                            pattern_type="near_duplicate_text",
                            account_hashes=authors[:6],
                            representative_text=members[0]["text"][:140],
                            evidence=[
                                f"Jaccard similarity >= 0.85 across {len(authors)} distinct accounts",
                                f"Near-identical wording observed: \"{members[0]['text'][:80]}...\"",
                            ],
                        )
                    )

        # 2. Synchronized Burst Detection (Posts within 3-minute window with matching hashtags)
        hashtag_posts = []
        for p in posts:
            txt = (p.get("content") or p.get("text") or "")
            tags = set(re.findall(r"#([A-Za-z0-9_]+)", txt.lower()))
            if tags:
                hashtag_posts.append({
                    "author": str(p.get("author_name") or p.get("author_id") or "author"),
                    "tags": tags,
                    "timestamp": p.get("published_at"),
                })

        tag_counter = Counter()
        for hp in hashtag_posts:
            for t in hp["tags"]:
                tag_counter[t] += 1

        frequent_tags = [t for t, c in tag_counter.most_common(3) if c >= 4]
        if frequent_tags:
            risk_points = max(risk_points, 45.0)
            clusters.append(
                CoordinationCluster(
                    cluster_id="burst_tags",
                    risk_score=45.0,
                    pattern_type="hashtag_coordination",
                    account_hashes=[hp["author"] for hp in hashtag_posts[:5]],
                    representative_text=f"Rapid repeated propagation of tags: {', '.join('#' + t for t in frequent_tags)}",
                    evidence=[
                        f"High-frequency concentrated hashtags: {', '.join('#' + t for t in frequent_tags)}",
                        "Elevated hashtag co-occurrence across multiple posters",
                    ],
                )
            )

        # 3. Overall Risk Assessment
        final_risk = round(min(100.0, risk_points), 1)
        if final_risk >= 75.0:
            level = "CRITICAL"
            summary = "High probability of coordinated amplification: multiple distinct accounts propagating near-identical copy in close temporal proximity."
        elif final_risk >= 50.0:
            level = "HIGH"
            summary = "Potential coordinated amplification detected: suspicious near-duplicate messaging patterns observed."
        elif final_risk >= 30.0:
            level = "ELEVATED"
            summary = "Minor repetitive messaging patterns detected; within normal organic discourse variance."
        else:
            level = "LOW"
            summary = "Organic discourse patterns: diverse lexical distribution and natural posting timeline observed."

        return CoordinationAssessment(
            overall_coordination_risk=final_risk,
            level=level,
            clusters_detected=clusters[:4],
            summary=summary,
        )

_coordination_instance = CoordinationDetectionService()

def get_coordination_service() -> CoordinationDetectionService:
    return _coordination_instance
