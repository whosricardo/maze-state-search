from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


REPORT_PATH = Path(
    "out/parte2/parte2_report.json"
)

OUTPUT_PATH = Path(
    "out/parte2/comportamento_dfs.png"
)


def load_report():
    with REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# [IA] ChatGPT – suporte de sintaxe Matplotlib para
# visualização em barras agrupadas escolhida pelo grupo.
def plot_dfs_behavior(report):
    dfs_results = (
        report["mandatory_cases"]
        ["dfs"]
        ["results"]
    )

    rows = []

    for source, result in dfs_results.items():
        counts = result["edge_type_counts"]

        rows.append({
            "origem": source,
            "TREE": counts["TREE"],
            "BACK": counts["BACK"],
            "FORWARD": counts["FORWARD"],
            "CROSS": counts["CROSS"],
        })

    comparison = pd.DataFrame(rows)

    print(
        "\n=== CLASSIFICAÇÃO DE ARESTAS DO DFS ==="
    )
    print(
        comparison.to_string(index=False)
    )

    ax = comparison.plot(
        x="origem",
        y=[
            "TREE",
            "BACK",
            "FORWARD",
            "CROSS",
        ],
        kind="bar",
        figsize=(10, 6),
    )

    ax.set_xlabel("Subreddit de origem")
    ax.set_ylabel("Quantidade de arestas")
    ax.set_title(
        "Classificação das arestas durante a execução do DFS"
    )

    ax.tick_params(
        axis="x",
        rotation=0,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def main():
    report = load_report()

    plot_dfs_behavior(report)


if __name__ == "__main__":
    main()
