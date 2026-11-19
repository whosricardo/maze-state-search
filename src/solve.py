from src.graphs.io import parse_map, validate_map
from src.graphs.estados import build_g_est, get_initial_state, TARGET_VERTEX
from src.graphs.algorithms import (
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
    find_trap_states,
)


MAPS = [
    "m01_terreno",
    "m02_uma_chave",
    "m03_tres_chaves",
    "m04_esteiras",
    "m05_bonus",
    "m06_fonte",
    "m07_impossivel",
    "m08_grande",
]


def run_map(map_name):
    path = f"data/mapas/{map_name}.txt"

    grid = parse_map(path)

    if not validate_map(grid):
        print(f"{map_name}: mapa inválido")
        return

    graph = build_g_est(grid)
    start = get_initial_state(grid)

    print(f"\n=== {map_name} ===")
    print("Vértices:", len(graph.adjacency))

    dfs_result = dfs(graph, start)

    print(
        "DFS:",
        dfs_result["status"],
        "ciclo:",
        dfs_result["has_cycle"],
    )

    if TARGET_VERTEX not in graph.adjacency:
        print("BFS: Sem Caminho")
        print("Dijkstra: Sem Caminho")
        print("Bellman-Ford: Sem Caminho")

        traps = find_trap_states(
            graph,
            start,
            TARGET_VERTEX,
        )

        print("Armadilhas:", len(traps))
        return

    bfs_result = bfs(
        graph,
        start,
        TARGET_VERTEX,
    )

    print(
        "BFS:",
        bfs_result["status"],
        bfs_result["steps"],
    )

    try:
        dijkstra_result = dijkstra(
            graph,
            start,
            TARGET_VERTEX,
        )

        print(
            "Dijkstra:",
            dijkstra_result["status"],
            dijkstra_result["cost"],
        )

    except ValueError as error:
        print("Dijkstra: Recusado -", error)

    bellman_result = bellman_ford(
        graph,
        start,
        TARGET_VERTEX,
    )

    print(
        "Bellman-Ford:",
        bellman_result["status"],
        bellman_result["cost"],
    )

    if bellman_result["cycle"] is not None:
        print(
            "Ciclo negativo:",
            bellman_result["cycle"],
        )

    traps = find_trap_states(
        graph,
        start,
        TARGET_VERTEX,
    )

    print("Armadilhas:", len(traps))


for map_name in MAPS:
    run_map(map_name)
