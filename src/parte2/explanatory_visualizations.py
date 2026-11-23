from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)

OUTPUT_DIR = Path("out/parte2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_degrees_dataframe(aggregated):
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

    return degrees


def explanatory_scatter_low_degree_concentration(aggregated):
    degrees = build_degrees_dataframe(aggregated)

    low_limit = 10

    low_region = degrees[
        (degrees["grau_saida"] <= low_limit)
        & (degrees["grau_entrada"] <= low_limit)
    ]

    percentage = (
        len(low_region) / len(degrees)
    ) * 100

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(
        degrees["grau_saida"],
        degrees["grau_entrada"],
        alpha=0.25,
        s=18,
    )

    highlight = Rectangle(
        (0, 0),
        low_limit,
        low_limit,
        alpha=0.18,
    )
    ax.add_patch(highlight)

    ax.set_xscale("symlog")
    ax.set_yscale("symlog")

    ax.set_xlabel("Grau de saída")
    ax.set_ylabel("Grau de entrada")
    ax.set_title(
        "A maior parte dos subreddits concentra-se em graus baixos"
    )

    # [IA] ChatGPT – ajuste de texto e posicionamento da anotação.
    ax.text(
        1.2,
        7,
        (
            f"{percentage:.1f}% dos subreddits\n"
            f"estão na região com grau ≤ {low_limit}\n"
            "de entrada e saída"
        ),
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.4",
            alpha=0.15,
        ),
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "explanatoria_1_concentracao_graus.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def explanatory_time_growth(df):
    df = df.copy()

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"],
        errors="coerce",
    )

    df = df.dropna(subset=["TIMESTAMP"])

    monthly = (
        df
        .set_index("TIMESTAMP")
        .resample("ME")
        .size()
        .reset_index(name="interacoes")
    )

    # Dezembro/2013 é excluído porque o dataset começa em 31/12/2013.
    monthly = monthly[
        (monthly["TIMESTAMP"] >= "2014-01-01")
        & (monthly["TIMESTAMP"] <= "2017-04-30")
    ].copy()

    monthly["indice"] = range(len(monthly))

    start_value = monthly.iloc[0]["interacoes"]
    end_value = monthly.iloc[-1]["interacoes"]

    growth_pct = (
        (end_value - start_value) / start_value
    ) * 100

    # [IA] ChatGPT – suporte de sintaxe para cálculo da tendência linear.
    coefficients = np.polyfit(
        monthly["indice"],
        monthly["interacoes"],
        1,
    )

    trend = (
        coefficients[0] * monthly["indice"]
        + coefficients[1]
    )

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        monthly["TIMESTAMP"],
        monthly["interacoes"],
        linewidth=1.5,
        alpha=0.45,
        label="Interações mensais",
    )

    ax.plot(
        monthly["TIMESTAMP"],
        trend,
        linewidth=3,
        label="Tendência linear",
    )

    ax.scatter(
        monthly.iloc[0]["TIMESTAMP"],
        start_value,
        s=60,
    )

    ax.scatter(
        monthly.iloc[-1]["TIMESTAMP"],
        end_value,
        s=60,
    )

    ax.annotate(
        f"Jan/2014\n{start_value} interações",
        xy=(
            monthly.iloc[0]["TIMESTAMP"],
            start_value,
        ),
        xytext=(20, 20),
        textcoords="offset points",
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.3",
            alpha=0.15,
        ),
        arrowprops=dict(
            arrowstyle="->",
        ),
    )

    ax.annotate(
        f"Abr/2017\n{end_value} interações",
        xy=(
            monthly.iloc[-1]["TIMESTAMP"],
            end_value,
        ),
        xytext=(-100, -35),
        textcoords="offset points",
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.3",
            alpha=0.15,
        ),
        arrowprops=dict(
            arrowstyle="->",
        ),
    )

    ax.text(
        monthly.iloc[len(monthly) // 2]["TIMESTAMP"],
        max(monthly["interacoes"]) * 0.92,
        f"Crescimento de {growth_pct:.1f}% no período",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.4",
            alpha=0.15,
        ),
    )

    # [IA] ChatGPT – ajustes finais de apresentação definidos pelo grupo.
    ax.set_ylim(bottom=0)

    ax.set_xlabel("Tempo")
    ax.set_ylabel("Número mensal de interações")
    ax.set_title(
        f"Interações mensais entre subreddits cresceram "
        f"{growth_pct:.1f}% entre jan/2014 e abr/2017"
    )

    ax.legend()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "explanatoria_2_crescimento_interacoes.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def main():
    df = load_reddit_dataset(DATASET_PATH)
    aggregated = aggregate_interactions(df)

    explanatory_scatter_low_degree_concentration(aggregated)
    explanatory_time_growth(df)


if __name__ == "__main__":
    main()
