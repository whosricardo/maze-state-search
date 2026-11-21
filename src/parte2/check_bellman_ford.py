from pathlib import Path

from src.graphs.algorithms import (
    bfs,
    bellman_ford,
)

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_reddit_graph,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)


NO_CYCLE_CANDIDATES = [
    ("askreddit", "politics"),
    ("dadjokes", "circlejerk"),
    ("49ers", "azcardinals"),
    ("conspiracy", "politic"),
    ("subredditdrama", "anarchism"),
]


NEGATIVE_CYCLE_CASE = (
    "csshelp",
    "brisbane",
)


def count_edges(graph):
    return sum(
        len(neighbors)
        for neighbors in graph.adjacency.values()
    )


def build_snapshot(df, percentage):
    sample_size = int(
        len(df) * percentage
    )

    snapshot_df = df.iloc[:sample_size]

    aggregated = aggregate_interactions(
        snapshot_df
    )

    graph = build_reddit_graph(
        aggregated
    )

    return (
        snapshot_df,
        aggregated,
        graph,
    )


def count_negative_edges_in_region(
    graph,
    reachable,
):
    negative_edges = 0

    for source in reachable:
        for target, weight in graph.get_neighbors(
            source
        ).items():
            if (
                target in reachable
                and weight < 0
            ):
                negative_edges += 1

    return negative_edges


def print_graph_summary(
    label,
    snapshot_df,
    aggregated,
    graph,
):
    negative_edges = (
        aggregated["WEIGHT"] < 0
    ).sum()

    zero_edges = (
        aggregated["WEIGHT"] == 0
    ).sum()

    positive_edges = (
        aggregated["WEIGHT"] > 0
    ).sum()

    print()
    print(label)
    print("-" * 50)

    print(
        "Raw interactions:",
        len(snapshot_df),
    )

    print(
        "Vertices:",
        len(graph.adjacency),
    )

    print(
        "Edges:",
        count_edges(graph),
    )

    print(
        "Negative edges:",
        negative_edges,
    )

    print(
        "Zero edges:",
        zero_edges,
    )

    print(
        "Positive edges:",
        positive_edges,
    )


def run_no_negative_cycle_cases(df):
    (
        snapshot_df,
        aggregated,
        graph,
    ) = build_snapshot(
        df,
        0.01,
    )

    print_graph_summary(
        "Bellman-Ford 1% snapshot",
        snapshot_df,
        aggregated,
        graph,
    )

    print()
    print(
        "Negative-weight / no-cycle candidates"
    )
    print("-" * 50)

    for source, target in NO_CYCLE_CANDIDATES:
        source_exists = (
            source in graph.adjacency
        )

        target_exists = (
            target in graph.adjacency
        )

        if (
            not source_exists
            or not target_exists
        ):
            print()
            print(
                f"{source} -> {target}"
            )
            print(
                "Skipped: vertex not found"
            )
            continue

        bfs_result = bfs(
            graph,
            source,
        )

        reachable = set(
            bfs_result["parents"].keys()
        )

        reachable_negative_edges = (
            count_negative_edges_in_region(
                graph,
                reachable,
            )
        )

        result = bellman_ford(
            graph,
            source,
            target,
        )

        print()
        print(
            f"{source} -> {target}"
        )

        print(
            "Reachable vertices:",
            len(reachable),
        )

        print(
            "Negative edges in reachable region:",
            reachable_negative_edges,
        )

        print(
            "Status:",
            result["status"],
        )

        print(
            "Cost:",
            result.get("cost"),
        )

        print(
            "Negative cycle:",
            result.get("cycle"),
        )

        path = result.get("path")

        if path is not None:
            print(
                "Path length:",
                len(path) - 1,
            )

            print(
                "Path:",
                path,
            )


def calculate_cycle_cost(
    graph,
    cycle,
):
    total = 0

    print()
    print("Cycle edges:")
    print("-" * 50)

    for source, target in zip(
        cycle,
        cycle[1:],
    ):
        weight = graph.get_neighbors(
            source
        )[target]

        print(
            f"{source} -> "
            f"{target}: "
            f"{weight}"
        )

        total += weight

    return total


def run_negative_cycle_case(df):
    (
        snapshot_df,
        aggregated,
        graph,
    ) = build_snapshot(
        df,
        0.10,
    )

    print_graph_summary(
        "Bellman-Ford 10% snapshot",
        snapshot_df,
        aggregated,
        graph,
    )

    source, target = (
        NEGATIVE_CYCLE_CASE
    )

    print()
    print("Negative-cycle case")
    print("-" * 50)

    print(
        f"Running: "
        f"{source} -> {target}"
    )

    result = bellman_ford(
        graph,
        source,
        target,
    )

    print(
        "Status:",
        result["status"],
    )

    cycle = result.get("cycle")

    print(
        "Negative cycle:",
        cycle,
    )

    if cycle is None:
        print(
            "No negative cycle returned."
        )
        return

    cycle_total = (
        calculate_cycle_cost(
            graph,
            cycle,
        )
    )

    print()
    print(
        "Cycle total:",
        cycle_total,
    )

    print(
        "Is negative:",
        cycle_total < 0,
    )


def main():
    df = load_reddit_dataset(
        DATASET_PATH
    )

    run_no_negative_cycle_cases(
        df
    )

    print()
    print("=" * 60)

    run_negative_cycle_case(
        df
    )


if __name__ == "__main__":
    main()
