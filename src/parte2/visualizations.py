import pandas as pd
import matplotlib.pyplot as plt

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
)


DATASET_PATH = "data/dataset_parte2/soc-redditHyperlinks-body.tsv"


def main():
    df = load_reddit_dataset(DATASET_PATH)
    aggregated = aggregate_interactions(df)

    # =========================
    # EXPLORATÓRIA 1
    # Grau de saída x Grau de entrada
    # =========================

    out_degree = (
        aggregated
        .groupby("SOURCE_SUBREDDIT")
        .size()
        .rename("grau_saida")
    )

    in_degree = (
        aggregated
        .groupby("TARGET_SUBREDDIT")
        .size()
        .rename("grau_entrada")
    )

    degrees = (
        pd.concat([out_degree, in_degree], axis=1)
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "subreddit"})
    )

    plt.figure(figsize=(10, 7))

    plt.scatter(
        degrees["grau_saida"],
        degrees["grau_entrada"],
        alpha=0.4,
    )

    plt.xlabel("Grau de saída")
    plt.ylabel("Grau de entrada")
    plt.title(
        "Relação entre grau de saída e grau de entrada dos subreddits"
    )

    plt.xscale("symlog")
    plt.yscale("symlog")

    plt.savefig(
        "out/parte2/scatter_graus_symlog.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.tight_layout()
    plt.show()

    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

    interactions_by_month = (
        df
        .set_index("TIMESTAMP")
        .resample("ME")
        .size()
        .reset_index(name="interacoes")
    )

    print("\nPrimeiros meses:")
    print(interactions_by_month.head())

    print("\nÚltimos meses:")
    print(interactions_by_month.tail())

    plt.figure(figsize=(12, 6))

    plt.plot(
        interactions_by_month["TIMESTAMP"],
        interactions_by_month["interacoes"],
    )

    plt.xlabel("Tempo")
    plt.ylabel("Número de interações")
    plt.title("Interações entre subreddits ao longo do tempo")

    plt.savefig(
        "out/parte2/interacoes_ao_longo_do_tempo.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
