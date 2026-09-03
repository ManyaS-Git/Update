from __future__ import annotations
import importlib.util
import os
import threading
from typing import Sequence
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from app.core.config import get_settings

class EmbeddingService:
    """
    Multilingual Document Embedding Service.
    Produces dense sentence vectors for semantic clustering in BERTopic.
    Uses sentence-transformers when available, or a calibrated TF-IDF + SVD projection fallback.
    """
    _model = None
    _lock = threading.Lock()
    _active_status = "uninitialized"

    def __init__(self, model_name: str | None = None, dimension: int = 32):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.embedding_model_name
        self.dimension = dimension

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        clean_texts = [t.strip() for t in texts if t.strip()]
        if not clean_texts:
            return np.zeros((0, self.dimension))

        # 1. Try SentenceTransformers if installed
        if importlib.util.find_spec("sentence_transformers"):
            try:
                with self._lock:
                    if self._model is None:
                        from sentence_transformers import SentenceTransformer
                        self._model = SentenceTransformer(
                            self.model_name,
                            cache_folder=self.settings.hf_model_cache
                        )
                        EmbeddingService._active_status = "executed_local_weights"

                if self._model:
                    embeddings = self._model.encode(clean_texts, show_progress_bar=False)
                    return np.asarray(embeddings, dtype=np.float32)
            except Exception:
                EmbeddingService._active_status = "active_fallback"

        # 2. Resilient Vector Projection Fallback (TF-IDF + TruncatedSVD)
        if len(clean_texts) == 1:
            vec = TfidfVectorizer(max_features=self.dimension)
            matrix = vec.fit_transform([clean_texts[0], "baseline multilingual reference anchor"]).toarray()
            out = np.zeros((1, self.dimension), dtype=np.float32)
            out[0, :matrix.shape[1]] = matrix[0]
            return out

        target_dim = min(self.dimension, len(clean_texts) - 1, 64)
        if target_dim < 2:
            target_dim = 2

        vec = TfidfVectorizer(ngram_range=(1, 2), max_features=128)
        tfidf_mat = vec.fit_transform(clean_texts)
        actual_features = tfidf_mat.shape[1]

        if actual_features <= target_dim:
            dense = tfidf_mat.toarray()
            padded = np.zeros((len(clean_texts), self.dimension), dtype=np.float32)
            padded[:, :actual_features] = dense
            return padded

        svd = TruncatedSVD(n_components=target_dim, random_state=42)
        reduced = svd.fit_transform(tfidf_mat)
        padded = np.zeros((len(clean_texts), self.dimension), dtype=np.float32)
        padded[:, :reduced.shape[1]] = reduced
        return padded

_embedding_instance = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    return _embedding_instance
