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

GRAPH_SIZES = [
    0.10,
    0.50,
    1.00,
]

BFS_DFS_SOURCES = [
    "csshelp",
    "steam",
    "amiibo",
]

DIJKSTRA_PAIRS = [
    ("csshelp", "brisbane"),
    ("amiibo", "worldoftanks"),
    ("steam", "linuxquestions"),
    ("redditdev", "technology"),
    ("brasil", "askreddit"),
]


def count_edges(graph):
    return sum(
        len(neighbors)
        for neighbors in graph.adjacency.values()
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

    return normal_graph, dijkstra_graph


def benchmark_bfs(graph):
    results = {}

    for source in BFS_DFS_SOURCES:
        if source not in graph.adjacency:
            continue

        results[source] = benchmark_call(
            lambda: bfs(
                graph,
                source,
            )
        )

    return results


def benchmark_dfs(graph):
    results = {}

    for source in BFS_DFS_SOURCES:
        if source not in graph.adjacency:
            continue

        results[source] = benchmark_call(
            lambda: dfs(
                graph,
                source,
            )
        )

    return results


def benchmark_dijkstra(graph):
    results = {}

    for source, target in DIJKSTRA_PAIRS:
        if (
            source not in graph.adjacency
            or target not in graph.adjacency
        ):
            continue

        pair_key = (
            f"{source}->{target}"
        )

        results[pair_key] = benchmark_call(
            lambda: dijkstra(
                graph,
                source,
                target,
            )
        )

    return results


def benchmark_bellman_ford(
    graph,
    fraction,
):
    results = {}

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

    results = {
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

    return results


def main():
    df = load_reddit_dataset(
        DATASET_PATH
    )

    benchmark_results = []

    for fraction in GRAPH_SIZES:
        percentage = int(
            fraction * 100
        )

        print(
            f"\nBenchmarking {percentage}%"
        )

        result = benchmark_size(
            df,
            fraction,
        )

        benchmark_results.append(
            result
        )

    print()
    print(benchmark_results)


if __name__ == "__main__":
    main()
