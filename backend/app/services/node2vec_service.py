from __future__ import annotations
import random
from typing import Any
import networkx as nx
import numpy as np

class Node2VecService:
    """
    Node2Vec Graph Representation Learning Engine.
    Generates node vector embeddings via second-order biased random walks (p, q).
    Enables structural similarity identification and community clustering.
    """

    def __init__(
        self,
        dimensions: int = 16,
        walk_length: int = 10,
        num_walks: int = 8,
        p: float = 1.0,  # Return parameter
        q: float = 1.0,  # In-out parameter
    ):
        self.dimensions = dimensions
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.p = p
        self.q = q

    def _get_transition_prob(self, G: nx.Graph, t: Any, v: Any) -> list[float]:
        neighbors = list(G.neighbors(v))
        probs = []
        for x in neighbors:
            weight = G[v][x].get("weight", 1.0)
            if x == t:
                prob = weight / self.p
            elif G.has_edge(t, x):
                prob = weight
            else:
                prob = weight / self.q
            probs.append(prob)

        total = sum(probs)
        if total > 0:
            return [p_val / total for p_val in probs]
        return [1.0 / len(neighbors)] * len(neighbors) if neighbors else []

    def _biased_random_walk(self, G: nx.Graph, start_node: Any) -> list[str]:
        walk = [start_node]
        while len(walk) < self.walk_length:
            curr = walk[-1]
            neighbors = list(G.neighbors(curr))
            if not neighbors:
                break
            if len(walk) == 1:
                walk.append(random.choice(neighbors))
            else:
                prev = walk[-2]
                probs = self._get_transition_prob(G, prev, curr)
                if probs and len(probs) == len(neighbors):
                    next_node = random.choices(neighbors, weights=probs, k=1)[0]
                else:
                    next_node = random.choice(neighbors)
                walk.append(next_node)
        return [str(n) for n in walk]

    def fit_transform(self, G: nx.Graph) -> dict[str, list[float]]:
        if not G or len(G.nodes) == 0:
            return {}

        nodes = list(G.nodes)
        undirected = G.to_undirected()

        # Step 1: Generate biased random walks
        walks = []
        for _ in range(self.num_walks):
            shuffled = list(nodes)
            random.shuffle(shuffled)
            for node in shuffled:
                walks.append(self._biased_random_walk(undirected, node))

        # Step 2: Skip-Gram / Co-occurrence Vectorization
        node_indices = {n: i for i, n in enumerate(nodes)}
        n_nodes = len(nodes)
        cooc = np.zeros((n_nodes, n_nodes), dtype=np.float32)

        window_size = 3
        for w in walks:
            for i, target in enumerate(w):
                if target not in node_indices:
                    continue
                t_idx = node_indices[target]
                start = max(0, i - window_size)
                end = min(len(w), i + window_size + 1)
                for j in range(start, end):
                    if i != j and w[j] in node_indices:
                        cooc[t_idx, node_indices[w[j]]] += 1.0

        # Step 3: Low-rank SVD projection to target embedding dimensions
        dim = min(self.dimensions, max(2, n_nodes - 1))
        # Add slight regularizer to avoid zero vectors
        cooc += np.eye(n_nodes) * 0.1

        try:
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=dim, random_state=42)
            dense_vectors = svd.fit_transform(cooc)
        except Exception:
            # Deterministic projection fallback
            dense_vectors = np.random.RandomState(42).randn(n_nodes, self.dimensions) * 0.1

        # Normalize L2
        norm = np.linalg.norm(dense_vectors, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        normalized = dense_vectors / norm

        embeddings = {}
        for node, idx in node_indices.items():
            vec = normalized[idx]
            if len(vec) < self.dimensions:
                padded = np.zeros(self.dimensions)
                padded[:len(vec)] = vec
                embeddings[node] = [round(float(x), 4) for x in padded]
            else:
                embeddings[node] = [round(float(x), 4) for x in vec[:self.dimensions]]

        return embeddings

    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        a = np.array(v1)
        b = np.array(v2)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

_node2vec_instance = Node2VecService()

def get_node2vec_service() -> Node2VecService:
    return _node2vec_instance
