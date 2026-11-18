from .graph import Graph
from collections import deque


def bfs(g: Graph, start, end=None):
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

    return {"status": "Encontrado", "steps": cont, "path": path, "parents": parents}


def dfs(graph, start):
    if start not in graph.adjacency:
        raise ValueError("Vértice Inicial não está no Grafo")

    color = {vertex: "WHITE" for vertex in graph.adjacency}

    parents = {start: None}
    discovery = {}
    finish = {}
    edge_types = []

    time = 0
    has_cycle = False

    stack = [start]
    time += 1
    discovery[start] = time
    color[start] = "GRAY"

    iters = {vertex: iter(graph.get_neighbors(vertex))
             for vertex in graph.adjacency}

    while stack:
        state = stack[-1]

        try:
            next_state = next(iters[state])

            if color[next_state] == "WHITE":
                edge_types.append((state, next_state, "TREE"))

                parents[next_state] = state

                color[next_state] = "GRAY"
                time += 1
                discovery[next_state] = time
                stack.append(next_state)

            elif color[next_state] == "GRAY":
                edge_types.append((state, next_state, "BACK"))
                has_cycle = True

            elif color[next_state] == "BLACK":
                if discovery[state] < discovery[next_state]:
                    edge_types.append((state, next_state, "FORWARD"))
                else:
                    edge_types.append((state, next_state, "CROSS"))

        except StopIteration:
            stack.pop()
            color[state] = "BLACK"
            time += 1
            finish[state] = time

    return {
        "status": "Finalizado",
        "parents": parents,
        "edge_types": edge_types,
        "has_cycle": has_cycle,
        "discovery": discovery,
        "finish": finish
    }
