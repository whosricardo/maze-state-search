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


def bellman_ford(graph, start, end="ALVO"):
    if start not in graph.adjacency:
        raise ValueError("Vertice Inicial não está no Grafo")
    if end not in graph.adjacency:
        raise ValueError("Vertice Final não está no grafo")

    reverse_tree = {start: None}
    cost_map = {start: 0}

    vertex_count = len(graph.adjacency)

    for _ in range(vertex_count - 1):
        changed = False
        for state, adj in graph.adjacency.items():
            if state not in cost_map:
                continue

            cost = cost_map[state]
            for next_state, next_cost in adj.items():
                accumulated_cost = cost + next_cost
                if cost_map.get(next_state, float("inf")) <= accumulated_cost:
                    continue

                cost_map[next_state] = accumulated_cost
                reverse_tree[next_state] = state
                changed = True

        if not changed:
            break

    for state, adj in graph.adjacency.items():
        if state not in cost_map:
            continue

        cost = cost_map[state]
        for next_state, next_cost in adj.items():
            accumulated_cost = cost + next_cost

            if cost_map.get(next_state, float("inf")) > accumulated_cost:
                reverse_tree[next_state] = state

                cycle_node = next_state
                for _ in range(vertex_count):
                    cycle_node = reverse_tree[cycle_node]

                cycle = []
                curr = cycle_node
                while True:
                    cycle.append(curr)
                    curr = reverse_tree[curr]
                    if curr == cycle_node:
                        cycle.append(curr)
                        break

                cycle.reverse()

                return {
                    "status": "Ciclo Negativo",
                    "steps": None,
                    "path": None,
                    "cost": float("-inf"),
                    "parents": reverse_tree,
                    "cycle": cycle
                }

    if end not in reverse_tree:
        return {
            "status": "Sem Caminho",
            "steps": None,
            "path": None,
            "cost": None,
            "parents": reverse_tree,
            "cycle": None
        }

    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = reverse_tree[curr]
    path.reverse()

    return {
        "status": "Encontrado",
        "steps": len(path) - 1,
        "path": path,
        "cost": cost_map[end],
        "parents": reverse_tree,
        "cycle": None
    }


def transpose_graph(graph: Graph) -> Graph:
    transposed = Graph()

    for vertex in graph.adjacency:
        transposed.add_vertex(vertex)

    for source, neighbors in graph.adjacency.items():
        for destination, weight in neighbors.items():
            transposed.add_edge(destination, source, weight)

    return transposed


def reachable_vertices(graph: Graph, start):
    if start not in graph.adjacency:
        raise ValueError("Vértice Inicial não está no Grafo")

    visited = set()
    stack = [start]

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                stack.append(neighbor)

    return visited


def find_trap_states(graph: Graph, start, target="ALVO"):
    if start not in graph.adjacency:
        raise ValueError("Vértice Inicial não está no Grafo")

    reachable_from_start = reachable_vertices(graph, start)

    if target not in graph.adjacency:
        return reachable_from_start

    transposed = transpose_graph(graph)
    can_reach_target = reachable_vertices(transposed, target)

    return reachable_from_start - can_reach_target
