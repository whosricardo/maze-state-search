import pandas as pd

from src.graphs.graph import Graph


def load_reddit_dataset(path):
    return pd.read_csv(
        path,
        sep="\t",
    )


def aggregate_interactions(df):
    aggregated = (
        df.groupby(
            [
                "SOURCE_SUBREDDIT",
                "TARGET_SUBREDDIT",
            ],
            as_index=False,
        )["LINK_SENTIMENT"]
        .sum()
        .rename(
            columns={
                "LINK_SENTIMENT": "WEIGHT",
            }
        )
    )

    return aggregated


def build_reddit_graph(df):
    graph = Graph()

    for row in df.itertuples(index=False):
        graph.add_edge(
            row.SOURCE_SUBREDDIT,
            row.TARGET_SUBREDDIT,
            row.WEIGHT,
        )

    return graph


def build_dijkstra_graph(df):
    graph = Graph()

    max_weight = df["WEIGHT"].max()

    for row in df.itertuples(index=False):
        cost = max_weight - row.WEIGHT + 1

        graph.add_edge(
            row.SOURCE_SUBREDDIT,
            row.TARGET_SUBREDDIT,
            cost,
        )

    return graph
