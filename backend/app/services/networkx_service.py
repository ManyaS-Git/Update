from __future__ import annotations
import re
from collections import Counter
from typing import Any
import networkx as nx

class NetworkXService:
    """
    NetworkX Graph Analysis Engine.
    Constructs directed multi-relational graphs representing:
    Users, Posts, Topics, Mentions, Replies, and Reposts/Shares.
    """

    def build_interaction_graph(self, posts: list[dict]) -> nx.DiGraph:
        G = nx.DiGraph()
        if not posts:
            return G

        author_counts = Counter()

        for p in posts:
            author = str(p.get("author_name") or p.get("author_id") or "author").strip()
            if not author.startswith("@") and not author.startswith("u/"):
                author = f"@{author}"
            author_counts[author] += 1
            G.add_node(author, label=author, node_type="user", platform=p.get("platform", "web"))

            # 1. User Mentions (@user)
            mentions = re.findall(r"@([A-Za-z0-9_]+)", (p.get("content") or p.get("text") or ""))
            for m in mentions[:3]:
                target = f"@{m}"
                G.add_node(target, label=target, node_type="user", platform=p.get("platform", "web"))
                if G.has_edge(author, target):
                    G[author][target]["weight"] += 1.0
                else:
                    G.add_edge(author, target, weight=1.0, relation="mention")

            # 2. Parent / Reply Relationships
            parent = p.get("parent_author") or p.get("reply_to")
            if parent:
                parent_node = f"@{parent}" if not parent.startswith("@") else parent
                G.add_node(parent_node, label=parent_node, node_type="user", platform=p.get("platform", "web"))
                if G.has_edge(author, parent_node):
                    G[author][parent_node]["weight"] += 2.0
                else:
                    G.add_edge(author, parent_node, weight=2.0, relation="reply")

        # 3. Topic Anchor Nodes
        words = []
        for p in posts:
            txt = (p.get("content") or p.get("text") or "").lower()
            words.extend(re.findall(r"[a-z]{4,}", txt))
        top_terms = [w.title() for w, _ in Counter(words).most_common(4) if w not in ("this", "that", "with", "from", "have", "will", "what")]

        for term in top_terms[:3]:
            term_node = f"#{term}"
            G.add_node(term_node, label=term_node, node_type="topic", platform="multi")
            for author, _ in author_counts.most_common(3):
                G.add_edge(author, term_node, weight=1.5, relation="discusses")

        # Ensure minimal topology
        if len(G.nodes) == 1:
            lone_node = list(G.nodes)[0]
            G.add_node("#Discourse", label="#Discourse", node_type="topic", platform="multi")
            G.add_edge(lone_node, "#Discourse", weight=1.0, relation="participates")

        return G

_networkx_instance = NetworkXService()

def get_networkx_service() -> NetworkXService:
    return _networkx_instance
