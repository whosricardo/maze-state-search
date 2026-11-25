import pandas as pd

from src.graphs.graph import Graph


# [IA] Codex – sintaxe pandas para compatibilidade com o cabeçalho oficial
def load_reddit_dataset(path):
    data = pd.read_csv(path, sep="\t")
    if "LINK_SENTIMENT" not in data.columns and "POST_LABEL" in data.columns:
        data = data.rename(columns={"POST_LABEL": "LINK_SENTIMENT"})
    return data


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
