from __future__ import annotations
from typing import Any
import networkx as nx
import numpy as np

class GraphSAGEService:
    """
    GraphSAGE (Graph Sample and Aggregate) Inductive Neighborhood Layer.
    Computes k-hop neighborhood aggregation:
        h_v^{(k)} = sigma( W_k * [ h_v^{(k-1)} || AGG_{u in N(v)} h_u^{(k-1)} ] )
    Provides learned graph structural representations from local neighborhoods.
    Distinguishes structural architectural inference from pretrained model weights.
    """

    def __init__(self, hidden_dim: int = 16, num_layers: int = 2):
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        # Deterministic weight initialization for architectural feature mapping
        rng = np.random.RandomState(42)
        # Weights for layer 1 and layer 2: maps [feature_dim * 2] -> [hidden_dim]
        self.W1 = rng.normal(0, 0.1, (hidden_dim * 2, hidden_dim))
        self.W2 = rng.normal(0, 0.1, (hidden_dim * 2, hidden_dim))

    def _initial_features(self, G: nx.Graph) -> tuple[dict[str, int], np.ndarray]:
        nodes = list(G.nodes)
        node_indices = {n: i for i, n in enumerate(nodes)}
        n_nodes = len(nodes)
        feat_dim = self.hidden_dim
        features = np.zeros((n_nodes, feat_dim), dtype=np.float32)

        for n, idx in node_indices.items():
            in_d = G.in_degree(n) if hasattr(G, "in_degree") else G.degree(n)
            out_d = G.out_degree(n) if hasattr(G, "out_degree") else G.degree(n)
            deg = in_d + out_d
            features[idx, 0] = float(in_d)
            features[idx, 1] = float(out_d)
            features[idx, 2] = float(deg) / max(1.0, float(n_nodes))
            # Trigonometric positional encoding based on node index
            for d in range(3, feat_dim):
                features[idx, d] = np.sin((idx + 1) * (d + 1) * 0.5)

        return node_indices, features

    def aggregate(self, G: nx.Graph) -> dict[str, list[float]]:
        if not G or len(G.nodes) == 0:
            return {}

        node_indices, h0 = self._initial_features(G)
        n_nodes = len(G.nodes)
        undirected = G.to_undirected()

        # --- Layer 1 Aggregation (1-Hop Neighborhood) ---
        h1 = np.zeros((n_nodes, self.hidden_dim), dtype=np.float32)
        for n, idx in node_indices.items():
            neighbors = list(undirected.neighbors(n))
            if neighbors:
                neigh_idx = [node_indices[nbr] for nbr in neighbors if nbr in node_indices]
                # Mean aggregation: AGG(N(v))
                neigh_mean = np.mean(h0[neigh_idx], axis=0)
            else:
                neigh_mean = h0[idx]

            # Concatenation [h_v || h_N(v)]
            concat = np.concatenate([h0[idx], neigh_mean])
            # Projection and non-linearity (ReLU)
            proj = np.dot(concat, self.W1)
            h1[idx] = np.maximum(0, proj)

        # Normalize layer 1
        norm1 = np.linalg.norm(h1, axis=1, keepdims=True)
        norm1[norm1 == 0] = 1.0
        h1 = h1 / norm1

        # --- Layer 2 Aggregation (2-Hop Neighborhood) ---
        h2 = np.zeros((n_nodes, self.hidden_dim), dtype=np.float32)
        for n, idx in node_indices.items():
            neighbors = list(undirected.neighbors(n))
            if neighbors:
                neigh_idx = [node_indices[nbr] for nbr in neighbors if nbr in node_indices]
                neigh_mean = np.mean(h1[neigh_idx], axis=0)
            else:
                neigh_mean = h1[idx]

            concat = np.concatenate([h1[idx], neigh_mean])
            proj = np.dot(concat, self.W2)
            h2[idx] = np.maximum(0, proj)

        # Normalize final layer
        norm2 = np.linalg.norm(h2, axis=1, keepdims=True)
        norm2[norm2 == 0] = 1.0
        h2 = h2 / norm2

        output = {}
        for n, idx in node_indices.items():
            output[n] = [round(float(val), 4) for val in h2[idx]]

        return output

_graphsage_instance = GraphSAGEService()

def get_graphsage_service() -> GraphSAGEService:
    return _graphsage_instance
