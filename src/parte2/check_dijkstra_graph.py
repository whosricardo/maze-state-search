from pathlib import Path

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_dijkstra_graph,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)


def main():
    df = load_reddit_dataset(DATASET_PATH)
    aggregated = aggregate_interactions(df)

    print("Original weight range:")
    print(
        aggregated["WEIGHT"].min(),
        "to",
        aggregated["WEIGHT"].max(),
    )

    graph = build_dijkstra_graph(aggregated)

    costs = []

    for neighbors in graph.adjacency.values():
        for cost in neighbors.values():
            costs.append(cost)

    print("\nDijkstra cost range:")
    print(
        min(costs),
        "to",
        max(costs),
    )

    print("\nNegative costs:")
    print(
        sum(
            1
            for cost in costs
            if cost < 0
        )
    )

    print("\nZero costs:")
    print(
        sum(
            1
            for cost in costs
            if cost == 0
        )
    )

    print("\nVertices:")
    print(len(graph.adjacency))

    print("\nEdges:")
    print(
        sum(
            len(neighbors)
            for neighbors in graph.adjacency.values()
        )
    )


if __name__ == "__main__":
    main()
