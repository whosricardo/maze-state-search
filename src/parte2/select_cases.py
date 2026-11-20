from pathlib import Path

from src.graphs.algorithms import dfs

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_reddit_graph,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)

SELECTED_SOURCES = [
    "csshelp",
    "steam",
    "amiibo",
]


def calculate_out_degrees(graph):
    degrees = []

    for vertex, neighbors in graph.adjacency.items():
        degrees.append(
            (
                vertex,
                len(neighbors),
            )
        )

    return sorted(
        degrees,
        key=lambda item: item[1],
        reverse=True,
    )


def calculate_in_degrees(graph):
    in_degrees = {
        vertex: 0
        for vertex in graph.adjacency
    }

    for source, neighbors in graph.adjacency.items():
        for destination in neighbors:
            in_degrees[destination] += 1

    return sorted(
        in_degrees.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def reachable_vertices_with_dfs(graph, source):
    result = dfs(graph, source)

    reached = {source}

    for origin, destination, _ in result["edge_types"]:
        reached.add(origin)
        reached.add(destination)

    return reached


def main():
    df = load_reddit_dataset(DATASET_PATH)

    aggregated = aggregate_interactions(df)

    graph = build_reddit_graph(aggregated)

    total_vertices = len(graph.adjacency)

    print("\nSelected BFS/DFS candidates:")

    reachable_sets = {}

    for source in SELECTED_SOURCES:
        reached = reachable_vertices_with_dfs(
            graph,
            source,
        )

        reachable_sets[source] = reached

        reachable = len(reached)

        percentage = (
            reachable / total_vertices
        ) * 100

        print(
            f"{source:20} "
            f"reachable={reachable:6} "
            f"({percentage:.2f}%)"
        )

    print("\nReachable set comparison:")

    print(
        "csshelp == steam:",
        reachable_sets["csshelp"]
        == reachable_sets["steam"],
    )

    print(
        "csshelp == amiibo:",
        reachable_sets["csshelp"]
        == reachable_sets["amiibo"],
    )

    print(
        "steam == amiibo:",
        reachable_sets["steam"]
        == reachable_sets["amiibo"],
    )

    out_degrees = calculate_out_degrees(graph)
    in_degrees = calculate_in_degrees(graph)

    print("\nTop 20 by out-degree:")

    for vertex, degree in out_degrees[:20]:
        print(
            f"{vertex:30} out={degree}"
        )

    print("\nTop 20 by in-degree:")

    for vertex, degree in in_degrees[:20]:
        print(
            f"{vertex:30} in={degree}"
        )

    print("\nPossible medium out-degree candidates:")

    medium_candidates = [
        (vertex, degree)
        for vertex, degree in out_degrees
        if 20 <= degree <= 100
    ]

    for vertex, degree in medium_candidates[:20]:
        print(
            f"{vertex:30} out={degree}"
        )

    print("\nPossible lower out-degree candidates:")

    lower_candidates = [
        (vertex, degree)
        for vertex, degree in out_degrees
        if 5 <= degree < 20
    ]

    for vertex, degree in lower_candidates[:20]:
        print(
            f"{vertex:30} out={degree}"
        )


if __name__ == "__main__":
    main()
