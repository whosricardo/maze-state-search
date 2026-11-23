import pandas as pd

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
)


DATASET_PATH = "data/dataset_parte2/soc-redditHyperlinks-body.tsv"


def main():
    df = load_reddit_dataset(DATASET_PATH)

    print("\n=== DIMENSÕES ===")
    print("Linhas:", len(df))
    print("Colunas:", len(df.columns))

    print("\n=== TIPOS ===")
    print(df.dtypes)

    print("\n=== VALORES AUSENTES ===")
    print(df.isna().sum())

    print("\n=== DUPLICATAS EXATAS ===")
    print(df.duplicated().sum())

    print("\n=== SENTIMENTO ===")
    print(
        df["LINK_SENTIMENT"]
        .value_counts()
        .sort_index()
    )

    print("\n=== PERÍODO TEMPORAL ===")

    timestamps = pd.to_datetime(
        df["TIMESTAMP"],
        errors="coerce",
    )

    print("Datas inválidas:", timestamps.isna().sum())
    print("Data inicial:", timestamps.min())
    print("Data final:", timestamps.max())

    print("\n=== SELF-LINKS ===")

    self_links = (
        df["SOURCE_SUBREDDIT"]
        == df["TARGET_SUBREDDIT"]
    ).sum()

    print("Self-links:", self_links)

    print("\n=== SUBREDDITS ===")

    source_unicos = df["SOURCE_SUBREDDIT"].nunique()
    print("SOURCE_SUBREDDIT distintos:", source_unicos)

    target_unicos = df["TARGET_SUBREDDIT"].nunique()
    print("TARGET_SUBREDDIT distintos:", target_unicos)

    total_unicos = pd.concat(
        [df["SOURCE_SUBREDDIT"], df["TARGET_SUBREDDIT"]]
    ).nunique()
    print("Total de subreddits distintos (origem + destino):", total_unicos)

    print("\n=== GRAFO AGREGADO ===")

    aggregated = aggregate_interactions(df)

    print("Arestas agregadas:", len(aggregated))

    print("\n=== PESOS AGREGADOS ===")

    print(aggregated["WEIGHT"].describe())

    positivos = (aggregated["WEIGHT"] > 0).sum()
    negativos = (aggregated["WEIGHT"] < 0).sum()
    zeros = (aggregated["WEIGHT"] == 0).sum()

    print("\nPesos positivos:", positivos)
    print("Pesos negativos:", negativos)
    print("Pesos zero:", zeros)


if __name__ == "__main__":
    main()
