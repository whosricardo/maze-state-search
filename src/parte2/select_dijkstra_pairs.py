from pathlib import Path
from src.graphs.algorithms import dijkstra

from src.parte2.loader import (
    load_reddit_dataset,
    aggregate_interactions,
    build_dijkstra_graph,
)


DATASET_PATH = Path(
    "data/dataset_parte2/soc-redditHyperlinks-body.tsv"
)

DIJKSTRA_PAIRS = [
    ("csshelp", "brisbane"),
    ("amiibo", "worldoftanks"),
    ("steam", "linuxquestions"),
    ("redditdev", "technology"),
    ("brasil", "askreddit"),
]


def main():
    df = load_reddit_dataset(DATASET_PATH)
    aggregated = aggregate_interactions(df)
    graph = build_dijkstra_graph(aggregated)

    print("Resultados Dijkstra:\n")

    for source, target in DIJKSTRA_PAIRS:
        result = dijkstra(
            graph,
            source,
            target
        )

        print(f"Origem:  {source}")
        print(f"Destino: {target}")
        print(f"Status:  {result['status']}")
        print(f"Custo:   {result.get('cost')}")

        if "steps" in result and result["steps"] is not None:
            print(f"Passos:  {result['steps']}")

        if "path" in result and result["path"] is not None:
            print(f"Tamanho do Path: {len(result['path']) - 1}")

        print("-" * 40)


if __name__ == "__main__":
    main()
