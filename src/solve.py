from pathlib import Path

from src.graphs.io import parse_map, validate_map
from src.graphs.estados import (
    build_g_est,
    build_g_pos,
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
    export_degrees,
    export_global_metrics,
    format_state,
    build_bonus_id_map,
    export_layers,
    export_model_comparison
)
from src.graphs.metrics import (
    count_vertex,
    count_edges,
    in_degree,
    out_degree,
    directed_density,
    theoretical_ceiling,
    state_occupancy,
    analyze_layers
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

COMPARISON_MAPS = {
    "m02_uma_chave",
    "m03_tres_chaves",
    "m04_esteiras",
}

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


def collect_dfs_rows(
    rows,
    map_name,
    dfs_result,
    bonus_ids,
):
    for source, destination, edge_type in dfs_result["edge_types"]:
        rows.append([
            map_name,
            format_state(source, bonus_ids),
            format_state(destination, bonus_ids),
            edge_type,
        ])


def export_map_traps(
    graph,
    start,
    map_name,
    bonus_ids,
):
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
        bonus_ids,
    )


def find_start_and_goal(grid):
    start_pos = None
    goal_pos = None
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == 'S':
                start_pos = (r, c)
            elif cell == 'G':
                goal_pos = (r, c)
    return start_pos, goal_pos


def run_map(map_name, solution_rows, dfs_rows, metrics_data, layers_data, comparison_rows):
    map_path = Path("data/mapas") / f"{map_name}.txt"

    grid = parse_map(map_path)

    if not validate_map(grid):
        raise ValueError(f"Mapa inválido: {map_name}")

    bonus_ids = build_bonus_id_map(grid)

    graph = build_g_est(grid)

    g_pos = build_g_pos(
        grid,
        door_mode="floor",
    )

    export_degrees(
        graph,
        OUTPUT_DIR / f"graus_{map_name}.csv",
        in_degree,
        out_degree,
        bonus_ids
    )
    start = get_initial_state(grid)

    print(f"\n=== {map_name} ===")
    print("Vértices:", len(graph.adjacency))

    export_edges(
        graph,
        OUTPUT_DIR / f"arestas_{map_name}.csv",
        bonus_ids
    )

    dfs_result = dfs(graph, start)

    collect_dfs_rows(
        dfs_rows,
        map_name,
        dfs_result,
        bonus_ids
    )

    print(
        "DFS:",
        dfs_result["status"],
        "ciclo:",
        dfs_result["has_cycle"],
    )

    ceiling = theoretical_ceiling(grid)

    metrics_data[map_name] = {
        "g_pos": {
            "ordem": count_vertex(g_pos),
            "tamanho": count_edges(g_pos),
            "densidade": directed_density(g_pos),
        },
        "g_est": {
            "ordem": count_vertex(graph),
            "tamanho": count_edges(graph),
            "densidade": directed_density(graph),
            "teto_teorico": ceiling,
            "ocupacao": state_occupancy(
                graph,
                ceiling,
            ),
        },
    }

    layers_data[map_name] = analyze_layers(graph)

    if map_name in COMPARISON_MAPS:
        pos_start, pos_goal = find_start_and_goal(grid)

        bfs_pos_floor = bfs(g_pos, pos_start, pos_goal)
        comparison_rows.append([
            map_name,
            "porta_como_chao",
            bfs_pos_floor["status"],
            bfs_pos_floor.get("steps", "")
        ])

        g_pos_wall = build_g_pos(grid, door_mode="wall")
        bfs_pos_wall = bfs(g_pos_wall, pos_start, pos_goal)
        comparison_rows.append([
            map_name,
            "porta_como_parede",
            bfs_pos_wall["status"],
            bfs_pos_wall.get("steps", "")
        ])

        bfs_est = bfs(graph, start, TARGET_VERTEX)
        comparison_rows.append([
            map_name,
            "grafo_estados",
            bfs_est["status"],
            bfs_est.get("steps", "")
        ])

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
            bonus_ids
        )

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

    add_solution(
        solution_rows,
        map_name,
        "BFS",
        bfs_result["status"],
        steps=bfs_result["steps"],
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
                bonus_ids
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

    if (
        map_name == "m06_fonte"
        and bellman_result.get("cycle") is not None
    ):
        print("Ciclo negativo encontrado.")

        export_negative_cycle_json(
            bellman_result,
            OUTPUT_DIR / "ciclo_negativo_m06.json",
            bonus_ids
        )

    export_map_traps(
        graph,
        start,
        map_name,
        bonus_ids
    )


def main():
    metrics_data = {}
    solution_rows = []
    dfs_rows = []
    layers_data = {}
    comparison_rows = []

    for map_name in MAPS:
        run_map(
            map_name,
            solution_rows,
            dfs_rows,
            metrics_data,
            layers_data,
            comparison_rows
        )

    export_solutions(
        solution_rows,
        OUTPUT_DIR / "solucoes.csv",
    )

    export_dfs_classification(
        dfs_rows,
        OUTPUT_DIR / "dfs_classificacao.csv",
    )

    export_global_metrics(
        metrics_data,
        OUTPUT_DIR / "metricas_global.json",
    )

    export_layers(
        layers_data,
        OUTPUT_DIR / "camadas.json",
    )

    export_model_comparison(
        comparison_rows,
        OUTPUT_DIR / "comparacao_modelagem.csv",
    )

    print(
        "\nArquivos CSV e JSON gerados em out/parte1/"
    )


if __name__ == "__main__":
    main()
