from .graph import Graph

def useDijkstra(graph: Graph, source: str , destination: str) -> float:
    
    if source not in graph.adjacency:
        raise ValueError("Start vertex does not exist")
    
    if destination not in graph.adjacency:
        raise ValueError("Destination vertex does not exist")
    
    for vertex in graph.adjacency:
        for _, weight in graph.get_neighbors(vertex).items():
            if weight < 0:
                raise ValueError("Negative weights is invalid")
            
    distances = {
        vertex: float("inf")
        for vertex in graph.adjacency
    }
    
    distances[source] = 0
    unvisited = set(graph.adjacency)
    
    while unvisited:
        current = min(unvisited, key=distances.get)
        
        for neighbor, weight in graph.get_neighbors(current).items():
            newDistance = distances[current] + weight
            
            if newDistance < distances[neighbor]:
                distances[neighbor] = newDistance
                
        unvisited.remove(current)
        
    return distances[destination]