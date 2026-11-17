from .graph import Graph

def UseBellmanFord(graph: Graph, source: str, destination: str) -> float:
    
    if source not in graph.adjacency:
        raise ValueError("Start vertex does not exist")
    
    if destination not in graph.adjacency:
        raise ValueError("Destination vertex does not exist")
    
    distances = {
        vertex: float("inf")
        for vertex in graph.adjacency
    }
    
    distances[source] = 0
    
    for _ in range(len(graph.adjacency) - 1):
        for vertex in graph.adjacency:
            for neighbor, weight in graph.get_neighbors(vertex).items():
                newDistance = distances[vertex] + weight
                
                if newDistance < distances[neighbor]:
                    distances[neighbor] = newDistance
                    
    return distances[destination]