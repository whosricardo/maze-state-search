from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


REPORT_PATH = Path(
    "out/parte2/parte2_report.json"
)

OUTPUT_PATH = Path(
    "out/parte2/comparacao_custos_dijkstra.png"
)


def load_report():
    with REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# [IA] ChatGPT – suporte de sintaxe Matplotlib para
# gráfico de barras escolhido pelo grupo.
def plot_dijkstra_costs(report):
    results = (
        report["mandatory_cases"]
        ["dijkstra"]
        ["results"]
    )

    rows = []

    for pair, result in results.items():
        rows.append({
            "par": pair,
            "custo": result["cost"],
        })

    comparison = pd.DataFrame(rows)

    print(
        "\n=== CUSTOS DOS CAMINHOS DO DIJKSTRA ==="
    )
    print(
        comparison.to_string(index=False)
    )

    ax = comparison.plot(
        x="par",
        y="custo",
        kind="bar",
        figsize=(11, 6),
        legend=False,
    )

    ax.set_xlabel("Par origem → destino")
    ax.set_ylabel("Custo transformado acumulado")
    ax.set_title(
        "Custo transformado dos caminhos encontrados pelo Dijkstra"
    )

    ax.tick_params(
        axis="x",
        rotation=25,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.0f",
            padding=3,
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def main():
    report = load_report()

    plot_dijkstra_costs(report)


if __name__ == "__main__":
    main()
