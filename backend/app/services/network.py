import networkx as nx

class NetworkIntelligenceService:
    def analyse(self, edges: list[dict]) -> dict:
        graph=nx.DiGraph()
        for edge in edges: graph.add_edge(edge["source"],edge["target"],weight=edge.get("weight",1))
        centrality=nx.degree_centrality(graph) if graph else {}
        return {"nodes":[{"id":node,"degree_centrality":round(value,3)} for node,value in centrality.items()],"edges":edges,"causation_claimed":False}
