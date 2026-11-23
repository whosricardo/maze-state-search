import json

import pandas as pd
import matplotlib.pyplot as plt


REPORT_PATH = "out/parte2/parte2_report.json"
OUTPUT_PATH = "out/parte2/comparacao_algoritmos.png"


def avg_mean_seconds(benchmarks):
    values = [
        case["mean_seconds"]
        for case in benchmarks.values()
    ]

    return sum(values) / len(values)


def fraction_to_percentage(fraction):
    return f"{int(fraction * 100)}%"


def plot_comparison(comparison):
    ax = comparison.plot(
        x="tamanho",
        y=[
            "BFS",
            "DFS",
            "Dijkstra",
            "Bellman-Ford",
        ],
        kind="bar",
        figsize=(10, 6),
    )

    ax.set_xlabel("Tamanho do grafo")
    ax.set_ylabel("Tempo médio (ms)")
    ax.set_title(
        "Tempo médio dos algoritmos por tamanho do grafo"
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

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()


def main():
    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        report = json.load(file)

    rows = []

    for data in report["scalability"]:
        size = fraction_to_percentage(
            data["fraction"]
        )

        rows.append({
            "tamanho": size,
            "BFS": (
                avg_mean_seconds(data["bfs"]) * 1000
            ),
            "DFS": (
                avg_mean_seconds(data["dfs"]) * 1000
            ),
            "Dijkstra": (
                avg_mean_seconds(data["dijkstra"]) * 1000
            ),
            "Bellman-Ford": (
                avg_mean_seconds(
                    data["bellman_ford"]
                ) * 1000
            ),
        })

    comparison = pd.DataFrame(rows)

    print(
        "\n=== COMPARAÇÃO DE TEMPO MÉDIO (ms) ==="
    )
    print(
        comparison
        .round(2)
        .to_string(index=False)
    )

    plot_comparison(comparison)


if __name__ == "__main__":
    main()
