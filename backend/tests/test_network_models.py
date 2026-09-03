import pytest
import networkx as nx
from app.services.networkx_service import get_networkx_service
from app.services.pagerank_service import get_pagerank_service
from app.services.node2vec_service import get_node2vec_service
from app.services.graphsage_service import get_graphsage_service

def test_network_models_suite():
    posts = [
        {"author_name": "lead_analyst", "content": "Critical update regarding the policy @reporter_one @civic_voice", "platform": "x"},
        {"author_name": "reporter_one", "content": "Breaking announcement covered by @lead_analyst", "platform": "x"},
        {"author_name": "civic_voice", "content": "Community forum discussion on reforms", "platform": "reddit"},
        {"author_name": "citizen_two", "content": "Agree with @lead_analyst on this point", "platform": "telegram"},
    ]

    # 1. NetworkX Graph Construction
    nx_svc = get_networkx_service()
    G = nx_svc.build_interaction_graph(posts)
    assert len(G.nodes) >= 4
    assert len(G.edges) >= 3

    # 2. PageRank Influence Ranking
    pr_svc = get_pagerank_service()
    influencers = pr_svc.rank_influencers(G, limit=5)
    assert len(influencers) > 0
    assert influencers[0].pagerank_score > 0.0
    assert "@lead_analyst" in [inf.label for inf in influencers]

    # 3. Node2Vec Biased Random Walks & Node Vectors
    node2vec = get_node2vec_service()
    embeddings = node2vec.fit_transform(G)
    assert len(embeddings) == len(G.nodes)
    for node, vec in embeddings.items():
        assert len(vec) == 16

    # 4. GraphSAGE Inductive Neighborhood Aggregation
    graphsage = get_graphsage_service()
    sage_embeddings = graphsage.aggregate(G)
    assert len(sage_embeddings) == len(G.nodes)
    for node, vec in sage_embeddings.items():
        assert len(vec) == 16
