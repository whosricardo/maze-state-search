import pandas as pd

from src.parte2.loader import (
    aggregate_interactions,
    build_reddit_graph,
)


def test_aggregate_interactions_sums_sentiments():
    df = pd.DataFrame({
        "SOURCE_SUBREDDIT": [
            "a",
            "a",
            "a",
            "b",
        ],
        "TARGET_SUBREDDIT": [
            "b",
            "b",
            "b",
            "c",
        ],
        "LINK_SENTIMENT": [
            1,
            1,
            -1,
            -1,
        ],
    })

    result = aggregate_interactions(df)

    weights = {
        (row.SOURCE_SUBREDDIT, row.TARGET_SUBREDDIT): row.WEIGHT
        for row in result.itertuples(index=False)
    }

    assert weights[("a", "b")] == 1
    assert weights[("b", "c")] == -1


def test_build_reddit_graph():
    df = pd.DataFrame({
        "SOURCE_SUBREDDIT": ["a", "b"],
        "TARGET_SUBREDDIT": ["b", "c"],
        "WEIGHT": [2, -1],
    })

    graph = build_reddit_graph(df)

    assert graph.get_neighbors("a")["b"] == 2
    assert graph.get_neighbors("b")["c"] == -1
    assert "c" in graph.adjacency
