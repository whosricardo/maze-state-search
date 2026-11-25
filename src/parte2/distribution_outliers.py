# [IA] Claude Code (Opus 5.5) – gráficos de distribuição e de outliers dos graus
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
)
from src.parte2.explanatory_visualizations import build_degrees_dataframe


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)

OUTPUT_DIR = Path("out/parte2")

DEGREE_COLUMNS = {
    "grau_entrada": "Grau de entrada",
    "grau_saida": "Grau de saída",
}

COLORS = {
    "grau_entrada": "#2a78c8",
    "grau_saida": "#e07b39",
}

TOP_OUTLIERS = 5


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)


def iqr_limits(values):
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def spread_labels(values, min_gap=0.13):
    """Afasta rótulos próximos, em escala log, para não se sobreporem.

    Recebe os graus em ordem decrescente e devolve a altura de cada rótulo.
    """
    positions = []

    for value in values:
        y = np.log10(value + 1)
        if positions and positions[-1] - y < min_gap:
            y = positions[-1] - min_gap
        positions.append(y)

    return [10 ** y - 1 for y in positions]


def find_outliers(degrees):
    """Marca como outlier o subreddit acima de Q3 + 1,5·IQR em cada grau."""
    rows = []

    for column, label in DEGREE_COLUMNS.items():
        _, upper = iqr_limits(degrees[column])
        selected = degrees[degrees[column] > upper]

        for row in selected.itertuples(index=False):
            rows.append(
                {
                    "subreddit": row.subreddit,
                    "metrica": label,
                    "grau": int(getattr(row, column)),
                    "limite_superior": upper,
                }
            )

    return (
        pd.DataFrame(rows)
        .sort_values(["metrica", "grau"], ascending=[True, False])
        .reset_index(drop=True)
    )


def distribution_chart(degrees):
    """Histograma com bins logarítmicos dos graus de entrada e saída."""
    max_degree = int(degrees[list(DEGREE_COLUMNS)].max().max())

    # Bins logarítmicos para uma distribuição de cauda longa. As bordas
    # ficam em meio-inteiros para que cada grau baixo (0, 1, 2...) tenha
    # um bin próprio, sem bins vazios entre inteiros.
    edges = np.unique(
        np.round(np.logspace(0, np.log10(max_degree + 1), 30))
    )
    bins = np.concatenate([[0], edges]) - 0.5

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

    for ax, (column, label) in zip(axes, DEGREE_COLUMNS.items()):
        values = degrees[column]
        median = values.median()
        p99 = values.quantile(0.99)

        ax.hist(
            values,
            bins=bins,
            color=COLORS[column],
            alpha=0.85,
            edgecolor="white",
            linewidth=0.5,
        )

        ax.axvline(median, color="#333333", linestyle="--", linewidth=1.2)
        ax.axvline(p99, color="#333333", linestyle=":", linewidth=1.2)

        ax.text(
            0.97,
            0.95,
            (
                f"Mediana: {median:.0f}\n"
                f"Percentil 99: {p99:.0f}\n"
                f"Máximo: {values.max():.0f}"
            ),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", alpha=0.15),
        )

        ax.set_xscale("symlog", linthresh=1)
        ax.set_xlim(bins[0], bins[-1])
        ax.set_yscale("log")
        ax.set_xlabel(label)
        ax.set_title(f"Distribuição do {label.lower()}")
        style_axis(ax)

    axes[0].set_ylabel("Número de subreddits (escala log)")

    fig.suptitle(
        "Os graus dos subreddits seguem uma distribuição de cauda longa",
        fontsize=13,
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "distribuicao_graus.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def outlier_chart(degrees, outliers):
    """Boxplot dos graus com os subreddits mais extremos rotulados."""
    columns = list(DEGREE_COLUMNS)

    fig, ax = plt.subplots(figsize=(11, 7))

    box = ax.boxplot(
        [degrees[column] for column in columns],
        positions=range(1, len(columns) + 1),
        widths=0.45,
        patch_artist=True,
        whis=1.5,
        flierprops=dict(
            marker="o",
            markersize=3,
            alpha=0.25,
            markeredgecolor="none",
        ),
        medianprops=dict(color="#333333", linewidth=1.5),
    )

    for patch, flier, column in zip(box["boxes"], box["fliers"], columns):
        patch.set_facecolor(COLORS[column])
        patch.set_alpha(0.6)
        flier.set_markerfacecolor(COLORS[column])

    total = len(degrees)

    for position, (column, label) in enumerate(DEGREE_COLUMNS.items(), start=1):
        subset = outliers[outliers["metrica"] == label]
        upper = iqr_limits(degrees[column])[1]
        share = len(subset) / total * 100

        # Resumo abaixo do rótulo do eixo x (x em dados, y em fração do eixo).
        ax.text(
            position,
            -0.07,
            f"{len(subset)} outliers ({share:.1f}%)\nlimite: grau > {upper:.0f}",
            ha="center",
            va="top",
            fontsize=9,
            transform=ax.get_xaxis_transform(),
        )

        top = subset.head(TOP_OUTLIERS)

        for row, label_y in zip(
            top.itertuples(index=False),
            spread_labels(top["grau"].tolist()),
        ):
            ax.annotate(
                f"r/{row.subreddit} ({row.grau})",
                xy=(position, row.grau),
                xytext=(position + 0.28, label_y),
                fontsize=8.5,
                va="center",
                arrowprops=dict(arrowstyle="-", alpha=0.4),
            )

    ax.set_yscale("symlog", linthresh=1)
    ax.set_ylim(bottom=-0.1)
    ax.set_xticks(range(1, len(columns) + 1))
    ax.set_xticklabels(DEGREE_COLUMNS.values())
    ax.set_xlim(0.5, len(columns) + 0.9)
    ax.set_ylabel("Grau (escala symlog)")
    ax.set_title(
        "Poucos subreddits concentram graus muito acima da maioria "
        "(outliers por Q3 + 1,5·IQR)"
    )
    style_axis(ax)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "outliers_graus.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_reddit_dataset(DATASET_PATH)
    aggregated = aggregate_interactions(df)
    degrees = build_degrees_dataframe(aggregated)

    outliers = find_outliers(degrees)
    outliers.to_csv(OUTPUT_DIR / "outliers_graus.csv", index=False)

    print("\n=== RESUMO DOS GRAUS ===")
    print(degrees[list(DEGREE_COLUMNS)].describe())

    print("\n=== OUTLIERS (Q3 + 1,5·IQR) ===")
    print(outliers.groupby("metrica").size())

    for label in DEGREE_COLUMNS.values():
        print(f"\nTop {TOP_OUTLIERS} – {label}:")
        print(
            outliers[outliers["metrica"] == label]
            .head(TOP_OUTLIERS)[["subreddit", "grau"]]
            .to_string(index=False)
        )

    distribution_chart(degrees)
    outlier_chart(degrees, outliers)


if __name__ == "__main__":
    main()