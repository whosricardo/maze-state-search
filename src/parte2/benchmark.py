import json
from pathlib import Path

from src.graphs.algorithms import (
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
)

from src.parte2.benchmark_utils import benchmark_call

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_reddit_graph,
    build_dijkstra_graph,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)

REPORT_PATH = Path(
    "out/parte2/parte2_report.json"
)


GRAPH_SIZES = [
    0.10,
    0.50,
    1.00,
]

BENCHMARK_REPETITIONS = 5


BFS_DFS_SOURCES = [
    "csshelp",
    "steam",
    "redditinsider",
]


DIJKSTRA_PAIRS = [
    ("csshelp", "brisbane"),
    ("redditinsider", "30rock"),
    ("steam", "linuxquestions"),
    ("redditdev", "technology"),
    ("brasil", "askreddit"),
]


BELLMAN_FORD_CASES = {
    0.10: [
        ("anticivilization", "globalhealth"),
    ],
    0.50: [
        ("anticivilization", "globalhealth"),
    ],
    1.00: [
        ("anticivilization", "globalhealth"),
    ],
}


BELLMAN_FORD_NO_CYCLE_CASE = (
    "anticivilization",
    "globalhealth",
)

BELLMAN_FORD_NEGATIVE_CYCLE_CASE = (
    "csshelp",
    "brisbane",
)


MANDATORY_CASE_FRACTION = 1.00
NEGATIVE_CYCLE_FRACTION = 0.10


def count_edges(graph):
    return sum(
        len(neighbors)
        for neighbors in graph.adjacency.values()
    )


# [IA] ChatGPT – 08–10: apoio na serialização dos resultados.
def json_default(value):
    if hasattr(value, "item"):
        return value.item()

    if isinstance(value, set):
        return list(value)

    raise TypeError(
        f"Object of type {type(value).__name__} "
        "is not JSON serializable"
    )


def save_report(report):
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=json_default,
        )


def build_graphs_for_size(
    df,
    fraction,
):
    row_count = int(
        len(df) * fraction
    )

    snapshot = df.iloc[:row_count]

    aggregated = aggregate_interactions(
        snapshot
    )

    normal_graph = build_reddit_graph(
        aggregated
    )

    dijkstra_graph = build_dijkstra_graph(
        aggregated
    )

    return (
        normal_graph,
        dijkstra_graph,
    )


def require_vertex(
    graph,
    vertex,
):
    if vertex not in graph.adjacency:
        raise ValueError(
            f"Required vertex not found: {vertex}"
        )


def benchmark_bfs(graph):
    results = {}

    for source in BFS_DFS_SOURCES:
        require_vertex(
            graph,
            source,
        )

        results[source] = benchmark_call(
            lambda source=source: bfs(
                graph,
                source,
            ),
            repetitions=BENCHMARK_REPETITIONS,
        )

    return results


def benchmark_dfs(graph):
    results = {}

    for source in BFS_DFS_SOURCES:
        require_vertex(
            graph,
            source,
        )

        results[source] = benchmark_call(
            lambda source=source: dfs(
                graph,
                source,
            ),
            repetitions=BENCHMARK_REPETITIONS,
        )

    return results


def benchmark_dijkstra(graph):
    results = {}

    for source, target in DIJKSTRA_PAIRS:
        require_vertex(
            graph,
            source,
        )

        require_vertex(
            graph,
            target,
        )

        pair_key = (
            f"{source}->{target}"
        )

        results[pair_key] = benchmark_call(
            lambda source=source, target=target: dijkstra(
                graph,
                source,
                target,
            ),
            repetitions=BENCHMARK_REPETITIONS,
        )

    return results


def benchmark_bellman_ford(
    graph,
    fraction,
):
    results = {}

    cases = BELLMAN_FORD_CASES.get(
        fraction,
        [],
    )

    for source, target in cases:
        require_vertex(
            graph,
            source,
        )

        require_vertex(
            graph,
            target,
        )

        pair_key = (
            f"{source}->{target}"
        )

        results[pair_key] = benchmark_call(
            lambda source=source, target=target: bellman_ford(
                graph,
                source,
                target,
            ),
            repetitions=BENCHMARK_REPETITIONS,
        )

    return results


def benchmark_size(
    df,
    fraction,
):
    (
        normal_graph,
        dijkstra_graph,
    ) = build_graphs_for_size(
        df,
        fraction,
    )

    return {
        "fraction": fraction,
        "vertices": len(
            normal_graph.adjacency
        ),
        "edges": count_edges(
            normal_graph
        ),
        "bfs": benchmark_bfs(
            normal_graph
        ),
        "dfs": benchmark_dfs(
            normal_graph
        ),
        "dijkstra": benchmark_dijkstra(
            dijkstra_graph
        ),
        "bellman_ford": benchmark_bellman_ford(
            normal_graph,
            fraction,
        ),
    }


# [IA] ChatGPT – 38–42: discussão da contagem de vértices alcançados pela BFS.
def summarize_bfs(
    bfs_result,
):
    parents = bfs_result.get(
        "parents",
        {},
    )

    return {
        "status": bfs_result.get(
            "status"
        ),
        "reachable_vertices": len(
            parents
        ),
    }


# [IA] ChatGPT – 08–10: apoio no resumo dos resultados de caminhos.
def summarize_shortest_path_result(
    result,
):
    summary = {
        "status": result.get("status"),
        "steps": result.get("steps"),
        "path": result.get("path"),
        "cost": result.get("cost"),
    }

    cycle = result.get("cycle")

    if cycle is not None:
        summary["cycle"] = cycle

    return summary


def summarize_dfs(
    dfs_result,
):
    summary = {
        "status": dfs_result.get(
            "status"
        ),
        "has_cycle": dfs_result.get(
            "has_cycle"
        ),
    }

    edge_types = dfs_result.get(
        "edge_types",
        [],
    )

    if edge_types:
        counts = {}

        for _, _, edge_type in edge_types:
            counts[edge_type] = (
                counts.get(
                    edge_type,
                    0,
                )
                + 1
            )

        summary["edge_type_counts"] = counts

    return summary


def build_mandatory_cases(df):
    (
        full_graph,
        dijkstra_graph,
    ) = build_graphs_for_size(
        df,
        MANDATORY_CASE_FRACTION,
    )

    (
        negative_cycle_graph,
        _,
    ) = build_graphs_for_size(
        df,
        NEGATIVE_CYCLE_FRACTION,
    )

    bfs_results = {}

    for source in BFS_DFS_SOURCES:
        require_vertex(
            full_graph,
            source,
        )

        bfs_raw = bfs(
            full_graph,
            source,
        )

        bfs_results[source] = summarize_bfs(
            bfs_raw
        )

    dfs_results = {}

    for source in BFS_DFS_SOURCES:
        require_vertex(
            full_graph,
            source,
        )

        dfs_raw = dfs(
            full_graph,
            source,
        )

        dfs_results[source] = summarize_dfs(
            dfs_raw
        )

    dijkstra_results = {}

    for source, target in DIJKSTRA_PAIRS:
        require_vertex(
            dijkstra_graph,
            source,
        )

        require_vertex(
            dijkstra_graph,
            target,
        )

        pair_key = (
            f"{source}->{target}"
        )

        dijkstra_raw = dijkstra(
            dijkstra_graph,
            source,
            target,
        )

        dijkstra_results[pair_key] = (
            summarize_shortest_path_result(
                dijkstra_raw
            )
        )

    (
        no_cycle_source,
        no_cycle_target,
    ) = BELLMAN_FORD_NO_CYCLE_CASE

    require_vertex(
        full_graph,
        no_cycle_source,
    )

    require_vertex(
        full_graph,
        no_cycle_target,
    )

    bf_no_cycle_raw = bellman_ford(
        full_graph,
        no_cycle_source,
        no_cycle_target,
    )

    bf_no_cycle = (
        summarize_shortest_path_result(
            bf_no_cycle_raw
        )
    )

    (
        cycle_source,
        cycle_target,
    ) = BELLMAN_FORD_NEGATIVE_CYCLE_CASE

    require_vertex(
        negative_cycle_graph,
        cycle_source,
    )

    require_vertex(
        negative_cycle_graph,
        cycle_target,
    )

    bf_negative_cycle_raw = bellman_ford(
        negative_cycle_graph,
        cycle_source,
        cycle_target,
    )

    bf_negative_cycle = (
        summarize_shortest_path_result(
            bf_negative_cycle_raw
        )
    )

    return {
        "bfs": {
            "fraction": MANDATORY_CASE_FRACTION,
            "sources": list(
                BFS_DFS_SOURCES
            ),
            "results": bfs_results,
        },

        "dfs": {
            "fraction": MANDATORY_CASE_FRACTION,
            "sources": list(
                BFS_DFS_SOURCES
            ),
            "results": dfs_results,
        },

        "dijkstra": {
            "fraction": MANDATORY_CASE_FRACTION,
            "pairs": [
                [
                    source,
                    target,
                ]
                for source, target
                in DIJKSTRA_PAIRS
            ],
            "weight_transformation": {
                "description": (
                    "Os pesos agregados originais são "
                    "convertidos para custos positivos "
                    "antes da execução do Dijkstra."
                ),
                "formula": (
                    "cost = max_weight - weight + 1"
                ),
                "source_function": (
                    "src.parte2.loader."
                    "build_dijkstra_graph"
                ),
            },
            "results": dijkstra_results,
        },

        "bellman_ford": {
            "negative_without_cycle": {
                "fraction": (
                    MANDATORY_CASE_FRACTION
                ),
                "pair": [
                    no_cycle_source,
                    no_cycle_target,
                ],
                "result": bf_no_cycle,
            },

            "negative_cycle": {
                "fraction": (
                    NEGATIVE_CYCLE_FRACTION
                ),
                "pair": [
                    cycle_source,
                    cycle_target,
                ],
                "result": bf_negative_cycle,
            },
        },
    }


def run_scalability_benchmarks(df):
    results = []

    for fraction in GRAPH_SIZES:
        percentage = int(
            fraction * 100
        )

        print(
            f"Benchmarking {percentage}%"
        )

        result = benchmark_size(
            df,
            fraction,
        )

        results.append(
            result
        )

    return results


def main():
    df = load_reddit_dataset(
        DATASET_PATH
    )

    scalability_results = (
        run_scalability_benchmarks(
            df
        )
    )

    print(
        "Running mandatory cases"
    )

    mandatory_cases = (
        build_mandatory_cases(
            df
        )
    )

    report = {
        "mandatory_cases": mandatory_cases,
        "scalability": scalability_results,
    }

    save_report(
        report
    )

    print()
    print(
        f"Report saved to: {REPORT_PATH}"
    )


if __name__ == "__main__":
    main()
