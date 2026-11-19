from .graph import Graph


def count_vertex(graph: Graph):
    return len(graph.adjacency)


def count_edges(graph: Graph):
    total = 0

    for vertex in graph.adjacency:
        total += len(graph.get_neighbors(vertex))

    return total


def out_degree(graph: Graph, vertex):
    if vertex not in graph.adjacency:
        raise ValueError("Vertice não está no Grafo")

    return len(graph.get_neighbors(vertex))


def in_degree(graph: Graph, vertex):
    if vertex not in graph.adjacency:
        raise ValueError("Vertice não está no Grafo")

    total = 0

    for source in graph.adjacency:
        if vertex in graph.get_neighbors(source):
            total += 1

    return total


def directed_density(graph: Graph):
    vertex_count = count_vertex(graph)
    edge_count = count_edges(graph)

    if vertex_count <= 1:
        return 0.0

    return edge_count / (vertex_count * (vertex_count - 1))


def count_map_features(grid):
    free_cells = 0
    key_count = 0
    bonus_count = 0

    for row in grid:
        for cell in row:
            if cell == '#':
                continue

            free_cells += 1

            if cell in {'a', 'b', 'c', 'd'}:
                key_count += 1
            elif cell == '+':
                bonus_count += 1

    return free_cells, key_count, bonus_count


def theoretical_ceiling(grid):
    free_cells, key_count, bonus_count = count_map_features(grid)
    return free_cells * (2 ** key_count) * (2 ** bonus_count)


def state_occupancy(graph: Graph, ceiling):
    reachable_states = len(graph.adjacency)

    if "ALVO" in graph.adjacency:
        reachable_states -= 1

    if ceiling == 0:
        return 0.0

    return reachable_states / ceiling
