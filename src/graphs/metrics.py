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


def analyze_layers(graph):
    layer_states = {}

    for state in graph.adjacency:
        if state == "ALVO":
            continue

        position, keys, consumed_bonus = state

        keys_label = "".join(sorted(keys))
        layer_name = keys_label if keys_label else "-"

        if layer_name not in layer_states:
            layer_states[layer_name] = set()

        layer_states[layer_name].add(state)

    layer_edges = {
        layer: 0
        for layer in layer_states
    }

    transitions = []

    for source, neighbors in graph.adjacency.items():
        if source == "ALVO":
            continue

        source_pos, source_keys, _ = source

        source_label = "".join(sorted(source_keys))
        source_layer = source_label if source_label else "-"

        for destination in neighbors:
            if destination == "ALVO":
                continue

            dest_pos, dest_keys, _ = destination

            dest_label = "".join(sorted(dest_keys))
            dest_layer = dest_label if dest_label else "-"

            if source_layer == dest_layer:
                layer_edges[source_layer] += 1

            else:
                transitions.append({
                    "origem": source_layer,
                    "destino": dest_layer,
                    "posicao": list(dest_pos),
                })

    result = {
        "camadas": {},
        "arcos_entre_camadas": transitions,
    }

    for layer, states in layer_states.items():
        vertex_count = len(states)
        edge_count = layer_edges[layer]

        if vertex_count > 1:
            density = edge_count / (
                vertex_count * (vertex_count - 1)
            )
        else:
            density = 0.0

        result["camadas"][layer] = {
            "ordem": vertex_count,
            "tamanho": edge_count,
            "densidade": density,
        }

    return result
