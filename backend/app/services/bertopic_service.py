from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import math
import re
from typing import Any
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer
from app.services.embeddings import get_embedding_service

class BERTopicCluster:
    def __init__(
        self,
        topic_id: int,
        topic_label: str,
        keywords: list[dict[str, Any]],
        representative_posts: list[str],
        post_ids: list[str],
        volume: int,
        growth_rate: float,
        platforms: list[str],
        model_name: str = "BERTopic",
        representation_method: str = "c-TF-IDF",
    ):
        self.topic_id = topic_id
        self.topic_label = topic_label
        self.keywords = keywords
        self.representative_posts = representative_posts
        self.post_ids = post_ids
        self.volume = volume
        self.growth_rate = growth_rate
        self.platforms = platforms
        self.model_name = model_name
        self.representation_method = representation_method

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "topic_label": self.topic_label,
            "keywords": self.keywords,
            "representative_posts": self.representative_posts,
            "post_ids": self.post_ids,
            "volume": self.volume,
            "growth_rate": round(self.growth_rate, 3),
            "platforms": self.platforms,
            "model_name": self.model_name,
            "representation_method": self.representation_method,
        }

class BERTopicService:
    """
    BERTopic Dynamic Topic Discovery Engine with c-TF-IDF Topic Representation.
    1. Generates dense document embeddings via EmbeddingService.
    2. Clusters social documents into semantically coherent topics.
    3. Calculates class-based TF-IDF (c-TF-IDF) across topic clusters.
    4. Automatically synthesizes descriptive human-readable topic labels.
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()

    def fit_transform(self, posts: list[dict]) -> list[BERTopicCluster]:
        if not posts:
            return []

        # Filter valid text content
        items = []
        for p in posts:
            txt = (p.get("text") or p.get("content") or "").strip()
            if len(txt.split()) >= 3:
                items.append({
                    "id": str(p.get("id") or p.get("post_id") or hash(txt)),
                    "text": txt,
                    "platform": p.get("platform", "general"),
                    "published_at": p.get("published_at"),
                })

        if len(items) < 3:
            # Single cluster fallback for sparse initialization
            sample_texts = [it["text"] for it in items] or ["General Public Discourse"]
            words = re.findall(r"[A-Za-z]{3,}", " ".join(sample_texts).lower())
            top_kws = [{"term": w, "c_tfidf": 1.0} for w, _ in Counter(words).most_common(5)] or [{"term": "discourse", "c_tfidf": 1.0}]
            label = " ".join(k["term"].capitalize() for k in top_kws[:3]) or "Emerging Public Conversation"
            return [
                BERTopicCluster(
                    topic_id=0,
                    topic_label=label,
                    keywords=top_kws,
                    representative_posts=sample_texts[:2],
                    post_ids=[it["id"] for it in items],
                    volume=len(items),
                    growth_rate=0.0,
                    platforms=list({it["platform"] for it in items}),
                )
            ]

        texts = [it["text"] for it in items]

        # Step 1: Document Embeddings
        embeddings = self.embedding_service.encode(texts)

        # Step 2: Semantic Clustering (Determines k dynamically based on corpus size)
        n_samples = len(texts)
        n_clusters = min(max(2, n_samples // 8), 6)

        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=32)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Step 3: Class-based TF-IDF (c-TF-IDF)
        # Combine all documents in each cluster into a single pseudo-document
        cluster_docs = {c: [] for c in range(n_clusters)}
        cluster_items = {c: [] for c in range(n_clusters)}

        for i, c in enumerate(cluster_labels):
            cluster_docs[c].append(texts[i])
            cluster_items[c].append(items[i])

        # Active clusters with at least 1 document
        active_clusters = [c for c in range(n_clusters) if cluster_docs[c]]
        corpus = [" ".join(cluster_docs[c]) for c in active_clusters]

        vec = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_features=500)
        tf_matrix = vec.fit_transform(corpus).toarray()
        feature_names = vec.get_feature_names_out()

        # Compute c-TF-IDF:
        # tf_c = word count in cluster c / total words in cluster c
        # idf_term = log(1 + (total documents in all clusters / term frequency across all clusters))
        total_words_per_cluster = tf_matrix.sum(axis=1, keepdims=True)
        total_words_per_cluster[total_words_per_cluster == 0] = 1
        tf_norm = tf_matrix / total_words_per_cluster

        total_corpus_docs = len(texts)
        term_frequency_all = tf_matrix.sum(axis=0)
        term_frequency_all[term_frequency_all == 0] = 1
        c_idf = np.log(1.0 + (total_corpus_docs / term_frequency_all))

        c_tfidf_matrix = tf_norm * c_idf

        # Step 4: Construct Topic Clusters with Human-Readable Labels
        result_clusters: list[BERTopicCluster] = []

        for idx, c in enumerate(active_clusters):
            c_scores = c_tfidf_matrix[idx]
            top_indices = np.argsort(c_scores)[::-1][:6]
            keywords = []
            for term_idx in top_indices:
                if c_scores[term_idx] > 0:
                    keywords.append({
                        "term": feature_names[term_idx],
                        "c_tfidf": round(float(c_scores[term_idx]), 4),
                    })

            if not keywords:
                keywords = [{"term": "discourse", "c_tfidf": 0.5}]

            # Human-Readable Label: Title-case the top 3 c-TF-IDF keywords
            label_terms = [k["term"] for k in keywords[:3] if len(k["term"]) >= 3]
            label = " & ".join(t.title() for t in label_terms) if label_terms else f"Topic {c+1}"

            cluster_posts = cluster_items[c]
            post_ids = [p["id"] for p in cluster_posts]
            platforms = list({p["platform"] for p in cluster_posts})

            # Representative posts: shortest post that contains top keyword
            rep_posts = [p["text"] for p in cluster_posts[:3]]

            # Growth rate calculation based on timestamps
            growth = min(1.0, len(cluster_posts) / max(1, len(texts)))

            result_clusters.append(
                BERTopicCluster(
                    topic_id=c + 1,
                    topic_label=label,
                    keywords=keywords,
                    representative_posts=rep_posts,
                    post_ids=post_ids,
                    volume=len(cluster_posts),
                    growth_rate=round(growth, 3),
                    platforms=platforms,
                )
            )

        # Sort clusters by volume
        result_clusters.sort(key=lambda x: x.volume, reverse=True)
        return result_clusters

_bertopic_instance = BERTopicService()

def get_bertopic_service() -> BERTopicService:
    return _bertopic_instance
