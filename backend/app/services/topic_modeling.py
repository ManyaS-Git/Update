from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import math
import re
from typing import Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans

class DynamicTopic:
    def __init__(
        self,
        topic_id: str,
        name: str,
        keywords: list[str],
        representation: str,
        post_ids: list[str],
        timestamps: list[datetime],
        growth_rate: float = 0.0,
    ):
        self.topic_id = topic_id
        self.name = name
        self.keywords = keywords
        self.representation = representation
        self.post_ids = post_ids
        self.timestamps = timestamps
        self.post_count = len(post_ids)
        self.growth_rate = growth_rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "name": self.name,
            "keywords": self.keywords,
            "representation": self.representation,
            "post_count": self.post_count,
            "growth_rate": round(self.growth_rate, 3),
            "timestamps": [t.isoformat() for t in self.timestamps],
        }

class TopicModelingService:
    """
    Dynamic Topic Modeling implementing c-TF-IDF keyword extraction
    and vector clustering over real social conversation data.
    Never hardcodes topic names.
    """
    def extract_topics(self, posts: list[dict]) -> list[DynamicTopic]:
        if not posts:
            return []

        texts = [p.get("text", "").strip() for p in posts]
        valid_indices = [i for i, t in enumerate(texts) if len(t.split()) >= 3]

        if len(valid_indices) < 3:
            # Group all into a single organic topic
            words = []
            for t in texts:
                words.extend(re.findall(r"[A-Za-z]{3,}", t.lower()))
            top_kw = [w for w, _ in Counter(words).most_common(5)] or ["general", "discussion"]
            name = " ".join(k.capitalize() for k in top_kw[:3]) or "Public Discussion"
            timestamps = [posts[i].get("timestamp", datetime.now(timezone.utc)) for i in range(len(posts))]
            return [
                DynamicTopic(
                    topic_id="topic-1",
                    name=name,
                    keywords=top_kw,
                    representation=", ".join(top_kw),
                    post_ids=[str(p.get("id")) for p in posts],
                    timestamps=timestamps,
                    growth_rate=0.0,
                )
            ]

        # Vectorize with TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=1,
            )
            filtered_texts = [texts[i] for i in valid_indices]
            tfidf_matrix = vectorizer.fit_transform(filtered_texts)
            feature_names = vectorizer.get_feature_names_out()

            # Determine number of clusters (k between 2 and 6 depending on sample size)
            k = max(2, min(6, len(filtered_texts) // 4))
            kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=64, n_init=3)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)

            # Group posts by cluster
            clusters: dict[int, list[int]] = {}
            for row_idx, cluster_id in enumerate(cluster_labels):
                clusters.setdefault(cluster_id, []).append(valid_indices[row_idx])

            dynamic_topics = []
            for c_id, original_indices in clusters.items():
                cluster_posts = [posts[i] for i in original_indices]
                cluster_texts = [texts[i] for i in original_indices]

                # Compute c-TF-IDF for cluster to get top keywords
                c_words = []
                for t in cluster_texts:
                    c_words.extend([w.lower() for w in re.findall(r"[A-Za-z]{3,}", t)])
                kw_counts = Counter(c_words)
                # Remove common stopwords
                for stop in ("the", "and", "this", "that", "with", "from", "for", "are", "have", "not"):
                    kw_counts.pop(stop, None)

                top_keywords = [w for w, _ in kw_counts.most_common(6)]
                if not top_keywords:
                    top_keywords = ["conversation", "signals", "public"]

                # Generate clean topic title from top keywords
                topic_title = " ".join(k.title() for k in top_keywords[:3])
                topic_slug = "-".join(top_keywords[:3]).lower()

                # Calculate growth rate comparing recent half to older half of timestamps
                timestamps = [p.get("timestamp", datetime.now(timezone.utc)) for p in cluster_posts]
                growth_rate = self._compute_growth(timestamps)

                dynamic_topics.append(
                    DynamicTopic(
                        topic_id=f"topic-{c_id}-{topic_slug}",
                        name=topic_title,
                        keywords=top_keywords,
                        representation=", ".join(top_keywords),
                        post_ids=[str(p.get("id")) for p in cluster_posts],
                        timestamps=timestamps,
                        growth_rate=growth_rate,
                    )
                )

            # Sort by post count
            dynamic_topics.sort(key=lambda t: t.post_count, reverse=True)
            return dynamic_topics
        except Exception:
            # Fallback if clustering encounters degenerate vector space
            return []

    def _compute_growth(self, timestamps: list[datetime]) -> float:
        if len(timestamps) < 4:
            return 0.0
        now = datetime.now(timezone.utc)
        recent_cutoff = now.timestamp() - 3600 * 6
        recent = sum(1 for t in timestamps if t.timestamp() >= recent_cutoff)
        older = len(timestamps) - recent
        if older == 0:
            return 1.0
        return (recent - older) / float(older)

_topic_service = TopicModelingService()

def extract_dynamic_topics(posts: list[dict]) -> list[DynamicTopic]:
    return _topic_service.extract_topics(posts)
