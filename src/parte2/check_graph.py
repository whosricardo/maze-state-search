from pathlib import Path

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_reddit_graph,
)

DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)


def main():
    df = load_reddit_dataset(DATASET_PATH)

    aggregated = aggregate_interactions(df)

    print("Raw interactions:")
    print(len(df))

    print("\nAggregated edges:")
    print(len(aggregated))

    print("\nPositive weights:")
    print((aggregated["WEIGHT"] > 0).sum())

    print("\nNegative weights:")
    print((aggregated["WEIGHT"] < 0).sum())

    print("\nZero weights:")
    print((aggregated["WEIGHT"] == 0).sum())

    graph = build_reddit_graph(aggregated)

    print("\nGraph vertices:")
    print(len(graph.adjacency))

    print("\nGraph edges:")
    print(
        sum(
            len(neighbors)
            for neighbors in graph.adjacency.values()
        )
    )


if __name__ == "__main__":
    main()
