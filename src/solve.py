from pathlib import Path

from src.graphs.io import parse_map, validate_map
from src.graphs.estados import (
    build_g_est,
    get_initial_state,
    TARGET_VERTEX,
)
from src.graphs.algorithms import (
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
    find_trap_states,
)
from src.graphs.export import (
    export_solutions,
    export_dfs_classification,
    export_edges,
    export_traps,
    export_path_json,
    export_negative_cycle_json,
    format_state,
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

OUTPUT_DIR = Path("out/parte1")

TRAP_OUTPUTS = {
    "m04_esteiras": "armadilhas_m04.csv",
    "m07_impossivel": "armadilhas_m07.csv",
}


def add_solution(
    rows,
    map_name,
    algorithm,
    status,
    steps="",
    cost="",
):
    rows.append([
        map_name,
        algorithm,
        status,
        steps,
        cost,
    ])


def collect_dfs_rows(rows, map_name, dfs_result):
    for source, destination, edge_type in dfs_result["edge_types"]:
        rows.append([
            map_name,
            format_state(source),
            format_state(destination),
            edge_type,
        ])


def export_map_traps(graph, start, map_name):
    if map_name not in TRAP_OUTPUTS:
        return

    traps = find_trap_states(
        graph,
        start,
        TARGET_VERTEX,
    )

    print("Armadilhas:", len(traps))

    export_traps(
        traps,
        OUTPUT_DIR / TRAP_OUTPUTS[map_name],
    )


def run_map(map_name, solution_rows, dfs_rows):
    map_path = Path("data/mapas") / f"{map_name}.txt"

    grid = parse_map(map_path)

    if not validate_map(grid):
        raise ValueError(f"Mapa inválido: {map_name}")

    graph = build_g_est(grid)
    start = get_initial_state(grid)

    print(f"\n=== {map_name} ===")
    print("Vértices:", len(graph.adjacency))

    # Arestas do grafo de estados
    export_edges(
        graph,
        OUTPUT_DIR / f"arestas_{map_name}.csv",
    )

    # DFS
    dfs_result = dfs(graph, start)

    collect_dfs_rows(
        dfs_rows,
        map_name,
        dfs_result,
    )

    print(
        "DFS:",
        dfs_result["status"],
        "ciclo:",
        dfs_result["has_cycle"],
    )

    # Caso sem ALVO, como m07
    if TARGET_VERTEX not in graph.adjacency:
        print("BFS: Sem Caminho")
        print("Dijkstra: Sem Caminho")
        print("Bellman-Ford: Sem Caminho")

        add_solution(
            solution_rows,
            map_name,
            "BFS",
            "Sem Caminho",
        )

        add_solution(
            solution_rows,
            map_name,
            "Dijkstra",
            "Sem Caminho",
        )

        add_solution(
            solution_rows,
            map_name,
            "Bellman-Ford",
            "Sem Caminho",
        )

        export_map_traps(
            graph,
            start,
            map_name,
        )

        return

    # BFS
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

    add_solution(
        solution_rows,
        map_name,
        "BFS",
        bfs_result["status"],
        steps=bfs_result["steps"],
    )

    # Dijkstra
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

        add_solution(
            solution_rows,
            map_name,
            "Dijkstra",
            dijkstra_result["status"],
            cost=dijkstra_result["cost"],
        )

        if map_name == "m03_tres_chaves":
            export_path_json(
                dijkstra_result,
                OUTPUT_DIR / "percurso_m03.json",
            )

    except ValueError as error:
        print(
            "Dijkstra: Recusado -",
            error,
        )

        add_solution(
            solution_rows,
            map_name,
            "Dijkstra",
            "Recusado",
        )

    # Bellman-Ford
    bellman_result = bellman_ford(
        graph,
        start,
        TARGET_VERTEX,
    )

    print(
        "Bellman-Ford:",
        bellman_result["status"],
        bellman_result.get("cost"),
    )

    bellman_cost = ""

    if bellman_result["status"] == "Encontrado":
        bellman_cost = bellman_result["cost"]

    add_solution(
        solution_rows,
        map_name,
        "Bellman-Ford",
        bellman_result["status"],
        cost=bellman_cost,
    )

    # Ciclo negativo obrigatório do m06
    if (
        map_name == "m06_fonte"
        and bellman_result.get("cycle") is not None
    ):
        print("Ciclo negativo encontrado.")

        export_negative_cycle_json(
            bellman_result,
            OUTPUT_DIR / "ciclo_negativo_m06.json",
        )

    # Armadilhas de m04 / m07
    export_map_traps(
        graph,
        start,
        map_name,
    )


def main():
    solution_rows = []
    dfs_rows = []

    for map_name in MAPS:
        run_map(
            map_name,
            solution_rows,
            dfs_rows,
        )

    export_solutions(
        solution_rows,
        OUTPUT_DIR / "solucoes.csv",
    )

    export_dfs_classification(
        dfs_rows,
        OUTPUT_DIR / "dfs_classificacao.csv",
    )

    print(
        "\nArquivos CSV e JSON gerados em out/parte1/"
    )


if __name__ == "__main__":
    main()
