from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import networkx as nx

@dataclass
class InfluencerNode:
    node_id: str
    label: str
    pagerank_score: float
    rank: int
    group: str  # amplifier, origin, audience
    degree: int
    platform: str

class PageRankService:
    """
    PageRank Influence Ranking Engine.
    Uses NetworkX PageRank (alpha=0.85, max_iter=100) to evaluate structural importance
    and influence of participants in the discourse graph.
    """

    def calculate_pagerank(self, G: nx.DiGraph, alpha: float = 0.85) -> dict[str, float]:
        if not G or len(G.nodes) == 0:
            return {}
        try:
            return nx.pagerank(G, alpha=alpha, max_iter=100, weight="weight")
        except Exception:
            n = len(G.nodes)
            return {node: round(1.0 / n, 4) for node in G.nodes}

    def rank_influencers(self, G: nx.DiGraph, limit: int = 15) -> list[InfluencerNode]:
        if not G or len(G.nodes) == 0:
            return []

        pr_scores = self.calculate_pagerank(G)
        sorted_nodes = sorted(G.nodes, key=lambda n: pr_scores.get(n, 0.0), reverse=True)[:limit]

        results = []
        for rank, n in enumerate(sorted_nodes, start=1):
            score = pr_scores.get(n, 0.0)
            data = G.nodes[n]
            node_type = data.get("node_type", "user")

            if node_type == "topic":
                group = "origin"
            elif score > 0.08:
                group = "amplifier"
            else:
                group = "audience"

            results.append(
                InfluencerNode(
                    node_id=n,
                    label=data.get("label", n),
                    pagerank_score=round(score, 4),
                    rank=rank,
                    group=group,
                    degree=G.degree(n),
                    platform=data.get("platform", "web"),
                )
            )

        return results

_pagerank_instance = PageRankService()

def get_pagerank_service() -> PageRankService:
    return _pagerank_instance
