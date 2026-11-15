from src.graphs.graph import Graph
from src.graphs.algorithms import useDijkstra

graph = Graph()

graph = Graph()
graph.add_edge("A", "B", 4)
graph.add_edge("A", "C", 10)
graph.add_edge("B", "C", 3)
graph.add_edge("B", "D", 12)
graph.add_edge("C", "D", 2)

print(useDijkstra(graph, "A", "A"))