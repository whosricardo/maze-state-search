from .graph import Graph
from collections import deque
def bfs(g: Graph, start, end = None):
    edges = g.adjacency
    if start not in edges:
        raise ValueError("Vertice Inicial não está no Grafo")
    if end is not None:
        if end not in edges:
            raise ValueError("Vertice Final não está no grafo")

    start_list = [start] 
    queue = deque(start_list)
    visited = {start}
    parents = {start: start}


    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in g.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = current
                queue.append(neighbor)
    if end is None:
        return {"status": "Explorado", "steps": None, "path": None, "parents": parents}
    
    if end not in parents:
        return {"status": "Sem Caminho", "steps": None, "path": None, "parents": parents}

    path = [end]
    node = end

    while node != start:
        node = parents[node]
        path.append(node)

    path.reverse()
    cont = len(path) - 1

    return {"status":"Encontrado", "steps": cont, "path": path, "parents": parents}


def useDijkstra(graph: Graph, source: str , destination: str) -> tuple:
    
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
    
    previous = {
        vertex: None
        for vertex in graph.adjacency
    }
    
    distances[source] = 0
    unvisited = set(graph.adjacency)
    
    while unvisited:
        current = min(unvisited, key=distances.get)
        
        for neighbor, weight in graph.get_neighbors(current).items():
            
            if neighbor not in unvisited:
                continue
            
            newDistance = distances[current] + weight
            
            if newDistance < distances[neighbor]:
                distances[neighbor] = newDistance
                previous[neighbor] = current
                
        unvisited.remove(current)
        

    if distances[destination] == float("inf"):
        return float("inf"), []

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()        
        
    return distances[destination], path