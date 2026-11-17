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
        return {"status": "Sem caminho", "steps": None, "path": None, "parents": parents}

    path = [end]
    node = end

    while node != start:
        node = parents[node]
        path.append(node)

    path.reverse()
    cont = len(path) - 1

    return {"status":"Encontrado", "steps": cont, "path": path, "parents": parents}